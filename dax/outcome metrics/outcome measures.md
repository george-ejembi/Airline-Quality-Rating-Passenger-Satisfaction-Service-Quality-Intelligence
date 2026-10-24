# Airline Satisfaction KPIs — Complete DAX Measures Reference

| | |
|---|---|
| **Model** | Airline Passenger Satisfaction |
| **Table** | `'Airline Quality Ratings'` |
| **Key column** | `[id]` (surrogate passenger id) |
| **Outcome column** | `[Satisfaction]` = `"Satisfied"` \| `"Neutral or Dissatisfied"` |
| **Measure count** | 8 |
| **Version** | 1.0 |
| **Last reviewed** | 2026-10-24 |
| **Related doc** | `airline_service_quality_measures.md` |

---

## Overview

The satisfaction layer is the KPI spine of the report: it turns the
`Satisfaction` column into **rates**, **segment-vs-overall gaps**, and
**performance-vs-target variances**.

| Group | Measures | Purpose |
|-------|----------|---------|
| **1. Population counts** | `Total Passengers`, `Satisfied Passengers`, `Dissatisfied Passengers` | Row counts / population denominator |
| **2. Satisfaction rates** | `Satisfaction Rate %`, `Overall Satisfaction Rate %` | Rate at current filter context, plus the all-segment benchmark |
| **3. Benchmarking** | `Satisfaction Target %`, `Satisfaction Gap vs Overall`, `Satisfaction vs Target` | KPI gaps against overall and target |

Together they answer three questions every stakeholder asks:

1. *"What is our satisfaction rate?"* → `Satisfaction Rate %`
2. *"Is this segment doing better or worse than the airline?"* → `Satisfaction Gap vs Overall`
3. *"Are we hitting target?"* → `Satisfaction vs Target`

---

## Measure index

| # | Measure name | Group | Format | Returns | Depends on |
|---|--------------|-------|--------|---------|------------|
| 1 | `Total Passengers` | Population | `#,0` | Distinct id count | — |
| 2 | `Satisfied Passengers` | Population | `#,0` | Row count where Satisfaction = "Satisfied" | — |
| 3 | `Dissatisfied Passengers` | Population | `#,0` | Row count where Satisfaction = "Neutral or Dissatisfied" | — |
| 4 | `Satisfaction Rate %` | Rates | `0.0%` | Satisfied / Total | `Satisfied Passengers`, `Total Passengers` |
| 5 | `Overall Satisfaction Rate %` | Rates | `0.0%` | Rate ignoring fact-table filters | `Satisfaction Rate %` |
| 6 | `Satisfaction Target %` | Benchmarking | `0.0%` | Static constant (0.75) | — |
| 7 | `Satisfaction Gap vs Overall` | Benchmarking | `+0.0%;-0.0%;0.0%` | Segment rate − overall rate | `Satisfaction Rate %`, `Overall Satisfaction Rate %` |
| 8 | `Satisfaction vs Target` | Benchmarking | `+0.0%;-0.0%;0.0%` | Rate − target | `Satisfaction Rate %`, `Satisfaction Target %` |

---

# Detailed measure catalogue

## 1. `Total Passengers`

| Property | Value |
|----------|-------|
| Group | Population |
| Returns | Whole number |
| Dependencies | None |
| Format string | `#,0` |
| Display folder | `_Satisfaction \ 1. Population` |

**Purpose.** Population denominator for all rate measures. Uses `DISTINCTCOUNT([id])`
so a passenger appearing on multiple rows (e.g. one row per leg) is counted once.

```dax
Total Passengers = DISTINCTCOUNT ( 'Airline Quality Ratings'[id] )
```

**Edge cases.**

- No filters → returns the total row population in the model.
- Empty filter context → returns `BLANK` (handled downstream by `DIVIDE(..., 0)`).
- **Mismatch with `COUNTROWS`** if `id` is not unique — see
  [Caveat 2](#caveat-2--countrows-vs-distinctcount-drift).

---

## 2. `Satisfied Passengers`

| Property | Value |
|----------|-------|
| Group | Population |
| Returns | Whole number |
| Dependencies | None |
| Format string | `#,0` |
| Display folder | `_Satisfaction \ 1. Population` |

**Purpose.** Numerator of the satisfaction rate. Counts rows where the passenger reported
`"Satisfied"` on the survey.

```dax
Satisfied Passengers =
CALCULATE (
    COUNTROWS ( 'Airline Quality Ratings' ),
    'Airline Quality Ratings'[Satisfaction] = "Satisfied"
)
```

**Edge cases.**

- Any other value in `[Satisfaction]` (blank, unknown, typo) is **not** counted.
- This means `Satisfied + Dissatisfied` may be less than `Total Passengers` — see
  [Caveat 1](#caveat-1--dissatisfied-passengers-is-misnamed) and
  [Caveat 3](#caveat-3--satisfaction-column-domain).

---

## 3. `Dissatisfied Passengers`

| Property | Value |
|----------|-------|
| Group | Population |
| Returns | Whole number |
| Dependencies | None |
| Format string | `#,0` |
| Display folder | `_Satisfaction \ 1. Population` |

**Purpose.** Counts rows where the source label is `"Neutral or Dissatisfied"`.
Semantically this is **not-satisfied** passengers (neutral *and* dissatisfied combined).

```dax
Dissatisfied Passengers =
CALCULATE (
    COUNTROWS ( 'Airline Quality Ratings' ),
    'Airline Quality Ratings'[Satisfaction] = "Neutral or Dissatisfied"
)
```

**Naming warning.** The name understates the scope: the source category groups
*neutral* passengers with *dissatisfied* ones. See
[Caveat 1](#caveat-1--dissatisfied-passengers-is-misnamed) for a recommended rename.

---

## 4. `Satisfaction Rate %`

| Property | Value |
|----------|-------|
| Group | Satisfaction rates |
| Returns | Percentage (0–1) |
| Dependencies | `Satisfied Passengers`, `Total Passengers` |
| Format string | `0.0%` |
| Display folder | `_Satisfaction \ 2. Rates` |

**Purpose.** The headline KPI: share of **satisfied** passengers in the current filter
context. This is the measure that should be bound to card visuals, KPI visuals, and
conditional formatting rules across every report page.

```dax
Satisfaction Rate % = DIVIDE ( [Satisfied Passengers], [Total Passengers] )
```

**Edge cases.**

- Denominator = 0 (no rows in slice) → `DIVIDE` returns `BLANK` (safe; renders as `-`).
- `% Satisfied + % Not Satisfied` = 100% **only if** `[Satisfaction]` contains exactly
  the two expected categories — see [Caveat 3](#caveat-3--satisfaction-column-domain).

---

## 5. `Overall Satisfaction Rate %`

| Property | Value |
|----------|-------|
| Group | Satisfaction rates |
| Returns | Percentage (0–1) |
| Dependencies | `Satisfaction Rate %` |
| Format string | `0.0%` |
| Display folder | `_Satisfaction \ 2. Rates` |

**Purpose.** Benchmark: the satisfaction rate with all filters on the fact table removed.
Use on segment pages to show *"this segment vs the airline"* — paired with
`Satisfaction Gap vs Overall`.

```dax
Overall Satisfaction Rate % =
CALCULATE ( [Satisfaction Rate %], ALL ( 'Airline Quality Ratings' ) )
```

**Edge cases.**

- `ALL('Airline Quality Ratings')` clears filters **only on the fact table**. Filters on
  related dimension tables (if any exist, e.g. `DimCustomerType`, `DimTravelClass`) are
  **not** cleared — see [Caveat 4](#caveat-4--all-fact-table-does-not-clear-dimension-filters).

---

## 6. `Satisfaction Target %`

| Property | Value |
|----------|-------|
| Group | Benchmarking |
| Returns | Constant decimal |
| Dependencies | None |
| Format string | `0.0%` |
| Display folder | `_Satisfaction \ 3. Benchmarking` |

**Purpose.** Business target for satisfaction rate. Hard-coded at **75%**.

```dax
Satisfaction Target % = 0.75
```

**Edge cases.**

- A measure-as-constant works but is **not user-adjustable** in the report.
- Does not vary by segment — see [Caveat 5](#caveat-5--static-target--no-per-segment-goals).

---

## 7. `Satisfaction Gap vs Overall`

| Property | Value |
|----------|-------|
| Group | Benchmarking |
| Returns | Signed percentage |
| Dependencies | `Satisfaction Rate %`, `Overall Satisfaction Rate %` |
| Format string | `+0.0%;-0.0%;0.0%` |
| Display folder | `_Satisfaction \ 3. Benchmarking` |

**Purpose.** Segment performance relative to the whole-airline rate. Positive → segment
outperforms; negative → underperforms.

```dax
Satisfaction Gap vs Overall = [Satisfaction Rate %] - [Overall Satisfaction Rate %]
```

**Interpretation guide.**

| Value | Reading | Typical action |
|-------|---------|----------------|
| `> +5.0 pts` | Segment clearly above average | Protect and replicate drivers |
| `-5.0 … +5.0 pts` | Near average | Monitor |
| `< -5.0 pts` | Underperforming vs airline | Escalate to intervention list (Q10) |

**Edge cases.** Returns `BLANK` when the filter context is empty (inherits from `DIVIDE`
inside `Satisfaction Rate %`) — desirable: no misleading `0` gaps on blank slicers.

---

## 8. `Satisfaction vs Target`

| Property | Value |
|----------|-------|
| Group | Benchmarking |
| Returns | Signed percentage |
| Dependencies | `Satisfaction Rate %`, `Satisfaction Target %` |
| Format string | `+0.0%;-0.0%;0.0%` |
| Display folder | `_Satisfaction \ 3. Benchmarking` |

**Purpose.** Variance against the 75% business target. Positive = above target.

```dax
Satisfaction vs Target = [Satisfaction Rate %] - [Satisfaction Target %]
```

**Interpretation guide.**

| Value | Reading | Visual cue |
|-------|---------|------------|
| `≥ 0` | At or above target | Green KPI indicator |
| `< 0` | Below target | Red KPI indicator |

**Edge cases.** Inherits the static-target limitation of `Satisfaction Target %`
([Caveat 5](#caveat-5--static-target--no-per-segment-goals)).

---

# Dependency graph

```
Satisfied Passengers ─┐
Total Passengers ─────┴──► Satisfaction Rate % ─┬──► Overall Satisfaction Rate % ──► Satisfaction Gap vs Overall
                                                 │
Dissatisfied Passengers                          ├──► Satisfaction vs Target
                                                 │
Satisfaction Target % (0.75) ────────────────────┘
```

- **Leaf measures** (no dependencies): `Total Passengers`, `Satisfied Passengers`,
  `Dissatisfied Passengers`, `Satisfaction Target %`.
- **Rate layer** (1 hop): `Satisfaction Rate %`.
- **Benchmark layer** (2 hops): `Overall Satisfaction Rate %`, `Satisfaction vs Target`,
  `Satisfaction Gap vs Overall`.

---

# Column reference

| Column | Role | Used by |
|--------|------|---------|
| `[id]` | Unique passenger key (surrogate) | `Total Passengers` |
| `[Satisfaction]` | Binary outcome: `"Satisfied"` \| `"Neutral or Dissatisfied"` | `Satisfied Passengers`, `Dissatisfied Passengers` |

Both columns come from the SQL clean view `vw_airline_clean` (mapped via the
`satisfied_flag` derivation in `03_structuring_views.sql`).

---

# Edge-case matrix

How each measure behaves under the three "non-standard" data states:

| Scenario | `Total` | `Satisfied` | `Dissatisfied` | `Satisfaction Rate %` | `Overall` | `Gap vs Overall` | `vs Target` |
|----------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Clean data (`id` unique, `Satisfaction` ∈ {S, ND}) | N | S | ND | S/N | unfiltered S/N | Δ | Δ − 0.75 |
| Duplicate `id` (multi-leg passenger) | lower | higher | higher | higher | higher | inherited bias | inherited bias |
| `Satisfaction` has a third value (e.g. `"Unknown"`) | N | S | ND | S/N | S/N | — | — (but D + S ≠ Total) |
| `Satisfaction` is `BLANK` on some rows | N | S | ND | S/N | S/N | — | — (see [Caveat 3](#caveat-3--satisfaction-column-domain)) |
| Empty filter context | BLANK | BLANK | BLANK | BLANK | BLANK | BLANK | BLANK |

Only the "clean data" row is the intended target state. Every other row is a signal that
one of the caveats below is in play.

---

# Caveats

## Caveat 1 — `Dissatisfied Passengers` is misnamed

The source category is `"Neutral or Dissatisfied"`, not `"Dissatisfied"`. The measure name
understates the scope by lumping neutral passengers (rating = 3) together with genuinely
dissatisfied ones (rating 1–2).

**Fix (recommended).** Rename to `Not Satisfied Passengers`. Either:
- Rename the measure and update dependent visuals, **or**
- Split into `Neutral Passengers` + `Dissatisfied Passengers` if the source ever starts
  emitting the two separately.

Until then, treat the number as *"everyone who did not tick Satisfied"* — a safe reading.

## Caveat 2 — `COUNTROWS` vs `DISTINCTCOUNT` drift

`Satisfied Passengers` and `Dissatisfied Passengers` use `COUNTROWS`.
`Total Passengers` uses `DISTINCTCOUNT([id])`.

If `id` is **not unique** in `'Airline Quality Ratings'`, then:

```
[Satisfied Passengers] + [Dissatisfied Passengers] > [Total Passengers]
```

and every rate derived from them is biased upward (numerator inflated, denominator fixed).

**Detect with [Validation V1](#validation-queries).** Fix at source by:

- Deduplicating at the SQL layer (`DISTINCT ON (id)` is already applied in
  `vw_airline_clean`), **or**
- Switching `Satisfied` / `Dissatisfied` to `DISTINCTCOUNT([id])` — but only if a
  passenger cannot legitimately appear in both categories, **or**
- Keeping `COUNTROWS` but documenting the row-grain assumption clearly.

## Caveat 3 — `Satisfaction` column domain

`Satisfied Passengers` matches `"Satisfied"` exactly; `Dissatisfied Passengers` matches
`"Neutral or Dissatisfied"` exactly. Anything else (blank, `"Unknown"`, casing mismatch,
trailing spaces) is silently **excluded from both**, which means:

```
[Satisfied] + [Dissatisfied] ≠ [Total Passengers]
```

**Diagnose with [Validation V2](#validation-queries).** If the drift is non-zero, either:

- Add a third measure `Unknown Satisfaction Passengers` to make the gap visible, **or**
- Clean the domain at source (Power Query: `Text.Trim`, casing normalise, replace blank
  with an explicit `"Unknown"` bucket), **or**
- Accept the gap and add a **denominator measure** `Passengers with Valid Satisfaction`
  equal to `[Satisfied] + [Dissatisfied]`, then define
  `Satisfaction Rate % = DIVIDE([Satisfied], [Passengers with Valid Satisfaction])`.

Currently the report assumes the clean state (S + D = Total), which the SQL clean view
guarantees via `CASE WHEN LOWER(TRIM(satisfaction)) = 'satisfied' THEN 1 ELSE 0 END`.
Verify once per refresh with V2.

## Caveat 4 — `ALL(fact table)` does not clear dimension filters

`Overall Satisfaction Rate %` uses:

```dax
CALCULATE ( [Satisfaction Rate %], ALL ( 'Airline Quality Ratings' ) )
```

`ALL('Airline Quality Ratings')` removes **filters on the fact table only**. If any slicer
or visual filter lives on a **related dimension table** (e.g. a star-schema
`DimCustomerType`, `DimTravelClass`, `DimDate`), the "overall" rate is still scoped by
that dimension.

**Two valid interpretations:**

| Intent | Correct formula |
|--------|-----------------|
| "Overall within the current dimension slice" (segment-relative benchmark) | Current formula — leave as-is |
| "True global overall across all slicers" (airline-wide benchmark) | `CALCULATE([Satisfaction Rate %], REMOVEFILTERS())` |

If the report is a flat single-table model (as in this file), the current formula is
correct. As soon as dimension tables are introduced, decide which intent you want and
document it in the measure description.

## Caveat 5 — Static target, no per-segment goals

`Satisfaction Target % = 0.75` is a **constant**, not a table lookup. Consequences:

1. Every segment is judged against the same 75% goal — but Business-class satisfaction
   is structurally different from Economy, Long-haul from Short-haul.
2. Report authors cannot adjust the target without editing the measure and republishing.
3. `Satisfaction vs Target` inherits both limitations.

**Recommended alternatives (pick one):**

| Option | Setup | Trade-off |
|--------|-------|-----------|
| **A. What-If parameter** | `Target Rate = GENERATESERIES(0.5, 1.0, 0.01)` → slider on report page | User-adjustable; no per-segment differentiation |
| **B. Disconnected targets table** | `Targets[Segment]`, `Targets[Rate]`; rewrite as `Satisfaction Target % = LOOKUPVALUE(Targets[Rate], Targets[Segment], SELECTEDVALUE(<segment>))` | Per-segment targets; needs refreshable table |
| **C. Related targets table** | Targets keyed on `Travel Class` / `Customer Type` / `Distance Band`; joined to the fact | Cleanest model; most upfront work |

Until then, at minimum add a tooltip in the report clarifying *"Target = 75% globally;
not segment-specific"*.

---

# Display folders and format strings

Recommended Power BI model organisation:

| Display folder | Measures | Format string |
|----------------|----------|---------------|
| `_Satisfaction \ 1. Population` | `Total Passengers`, `Satisfied Passengers`, `Dissatisfied Passengers` | `#,0` |
| `_Satisfaction \ 2. Rates` | `Satisfaction Rate %`, `Overall Satisfaction Rate %` | `0.0%` |
| `_Satisfaction \ 3. Benchmarking` | `Satisfaction Target %` | `0.0%` |
| `_Satisfaction \ 3. Benchmarking` | `Satisfaction Gap vs Overall`, `Satisfaction vs Target` | `+0.0%;-0.0%;0.0%` |

The signed format strings (`+0.0%;-0.0%;0.0%`) render `+3.2%`, `-1.8%`, and `0.0%`
respectively, which is what you want on variance cards.

---

# Validation queries

Run these in DAX Studio against the model to verify the measures before publishing.

## V1 — population integrity (`COUNTROWS` vs `DISTINCTCOUNT`)

```dax
EVALUATE
ROW(
    "satisfied",              [Satisfied Passengers],
    "dissatisfied",           [Dissatisfied Passengers],
    "s_plus_d",               [Satisfied Passengers] + [Dissatisfied Passengers],
    "total_distinct",         [Total Passengers],
    "total_rows",             COUNTROWS ( 'Airline Quality Ratings' ),
    "row_id_drift",           COUNTROWS ( 'Airline Quality Ratings' )
                              - DISTINCTCOUNT ( 'Airline Quality Ratings'[id] ),
    "s_plus_d_minus_total",   [Satisfied Passengers] + [Dissatisfied Passengers]
                              - [Total Passengers]
)
-- Expect: row_id_drift = 0, s_plus_d_minus_total = 0
-- Non-zero row_id_drift      → duplicate id, see Caveat 2
-- Non-zero s_plus_d_minus_total → unknown Satisfaction category, see Caveat 3
```

## V2 — Satisfaction domain audit

```dax
EVALUATE
SUMMARIZECOLUMNS(
    'Airline Quality Ratings'[Satisfaction],
    "passengers", COUNTROWS ( 'Airline Quality Ratings' )
)
ORDER BY [passengers] DESC
-- Expect exactly two rows: "Satisfied", "Neutral or Dissatisfied".
-- Any other row (BLANK, "Unknown", casing variants) is a data-quality issue.
```

## V3 — rate bounds (must be within 0 and 1, or BLANK)

```dax
EVALUATE
ROW(
    "rate_min",     MINX ( VALUES ( 'Airline Quality Ratings'[id] ), [Satisfaction Rate %] ),
    "rate_max",     MAXX ( VALUES ( 'Airline Quality Ratings'[id] ), [Satisfaction Rate %] ),
    "overall",      [Overall Satisfaction Rate %]
)
-- Expect rate_min ≥ 0, rate_max ≤ 1, overall within the same range.
-- Any value outside 0..1 signals V1 / V3 data corruption cascading through.
```

## V4 — overall vs unfiltered rate

```dax
EVALUATE
ROW(
    "in_filter_context", [Satisfaction Rate %],          -- current filter context
    "via_ALL",           [Overall Satisfaction Rate %],  -- fact-table filter cleared
    "global",            CALCULATE ( [Satisfaction Rate %], REMOVEFILTERS () )
)
-- On a page with no active slicers, all three should match.
-- Divergence between "via_ALL" and "global" reveals Caveat 4 (dimension filters).
```

## V5 — target variance consistency

```dax
EVALUATE
ROW(
    "rate",                    [Satisfaction Rate %],
    "target",                  [Satisfaction Target %],
    "vs_target_direct",        [Satisfaction Rate %] - [Satisfaction Target %],
    "vs_target_measure",       [Satisfaction vs Target],
    "diff_should_be_zero",     [Satisfaction vs Target]
                               - ( [Satisfaction Rate %] - [Satisfaction Target %] )
)
-- Last value must equal 0 — proves the measure is wired correctly.
```

---

# Suggested extensions

Not required for the current report, but worth considering as the model matures:

| Measure | Formula sketch | Why |
|---------|----------------|-----|
| `% Not Satisfied` | `DIVIDE([Dissatisfied Passengers], [Total Passengers])` | Complements `Satisfaction Rate %`; sums to 100% with it when data is clean |
| `Unknown Satisfaction Passengers` | `[Total Passengers] - [Satisfied Passengers] - [Dissatisfied Passengers]` | Makes Caveat 3 visible as a first-class measure instead of a silent gap |
| `Target (user-adjustable)` | What-If parameter `TargetParam[Value]` | Replaces static `Satisfaction Target %`, supports scenario analysis |
| `Satisfaction Rank (segment)` | `RANKX ( ALLSELECTED ( 'Airline Quality Ratings'[travel_class] ), [Satisfaction Rate %] )` | Feeds "top/bottom class" visuals |
| `Satisfaction YoY delta` | With a `DimDate` and `SAMEPERIODLASTYEAR` | Trend reporting (needs date dimension) |

These are documented here so future contributors extend the model in the same style.

---

# Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-10-24 | Initial consolidation of all 8 satisfaction-KPI measures with metadata, edge-case matrix, caveats, validation queries, and suggested extensions. |

---

# Related documents

- `airline_service_quality_measures.md` — the 10 touchpoint / stage-score measures
  (companion to this file)
- `airline_satisfaction_ml.md` — ML pipeline reference (Python package + notebook)
- SQL layer: `01_create_schema.sql`, `02_data_profiling.sql`,
  `03_structuring_views.sql`, `04_intelligence_layers.sql`
- Power BI model: `AirlineSatisfaction.pbix`