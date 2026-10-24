"""End-to-end orchestration.

Run from the ``python/`` directory:
    python -m src.pipeline
"""
from __future__ import annotations

import joblib

from . import db, evaluate, features, interpret, segment, train
from .config import MODEL_PATH, OUTPUTS_DIR


def main() -> None:
    # --- 1. load ---------------------------------------------------------- #
    raw = db.load_training_set()
    print(f"Loaded {raw.shape[0]:,} rows x {raw.shape[1]} columns")

    # --- 2. features + split --------------------------------------------- #
    prep = features.prepare(raw)
    X_train, y_train = prep["X_train"], prep["y_train"]
    X_test, y_test = prep["X_test"], prep["y_test"]
    feats = prep["features"]
    print(f"Train: {len(X_train):,}   Test: {len(X_test):,}   "
          f"Features: {len(feats)}")

    # --- 3. cross-validation on training data only ----------------------- #
    models = train.build_models()
    cv_results = train.cross_validate_models(models, X_train, y_train)
    cv_results.to_csv(OUTPUTS_DIR / "cv_results.csv", index=False)
    print("\nCross-validation:\n", cv_results.to_string(index=False))

    # --- 4. tune the strongest family (gradient boosting) ---------------- #
    best, best_params, best_cv = train.tune_hist_gb(X_train, y_train)
    print(f"\nBest HGB params: {best_params}  (CV ROC-AUC {best_cv:.4f})")

    # --- 5. final evaluation on untouched test set ----------------------- #
    metrics = evaluate.evaluate_on_test(best, X_test, y_test)
    print("\nTest metrics:",
          {k: metrics[k] for k in ("roc_auc", "pr_auc", "f1", "accuracy")})
    print(metrics["report"])
    evaluate.plot_diagnostics(y_test, metrics["y_pred"], metrics["y_proba"])
    evaluate.save_metrics(metrics)

    # --- 6. interpretation ------------------------------------------------ #
    interpret.permutation_importance_plot(best, X_test, y_test, feats)
    logreg = models["logreg"].fit(X_train, y_train)
    interpret.logistic_coefficients_plot(logreg, feats)
    interpret.shap_summary(best, X_train, X_test)

    # --- 7. segmentation -------------------------------------------------- #
    df_seg, sil, k = segment.fit_segments(prep["df"])
    profile = segment.profile_clusters(df_seg)
    profile.to_csv(OUTPUTS_DIR / "cluster_profile.csv")
    print(f"\nSilhouette by k:\n{sil.to_string()}")
    print(f"\nChosen k = {k}\n{profile.to_string()}")

    # --- 8. persist model + write predictions back to PostgreSQL --------- #
    joblib.dump({"model": best, "features": feats}, MODEL_PATH)

    out = df_seg[["id", "split", "cluster"]].copy()
    out["pred_prob_satisfied"] = (
        best.predict_proba(df_seg[feats])[:, 1].round(4)
    )
    out["pred_label"] = (out["pred_prob_satisfied"] >= 0.5).astype(int)
    out["actual"] = df_seg["target"]

    n = db.write_predictions(out)
    print(f"Wrote {n:,} rows to ml_predictions")
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()