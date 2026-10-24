"""Airline passenger satisfaction - ML package.

Public modules
--------------
config     : constants, paths, feature groups
db         : SQLAlchemy engine, read training set, write predictions
features   : leakage-safe feature engineering and split helpers
train      : model zoo, cross-validation, hyper-parameter tuning
evaluate   : hold-out metrics and diagnostic plots
interpret  : permutation importance, logistic coefficients, optional SHAP
segment    : unsupervised passenger segmentation
pipeline   : end-to-end orchestration (importable + CLI)
"""

__version__ = "1.0.0"