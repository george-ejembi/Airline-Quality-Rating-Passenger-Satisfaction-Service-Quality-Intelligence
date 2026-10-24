# Airline Service Quality — Complete DAX Measures Reference

| | |
|---|---|
| **Model** | Airline Passenger Satisfaction |
| **Table** | `'Airline Quality Ratings'` |
| **Grain** | one row per passenger |
| **Rating scale** | 1–5 Likert, `0` / `BLANK` = not applicable |
| **Measure count** | 10 |
| **Version** | 1.0 |
| **Last reviewed** | 2026-10-24 |

---

## Overview

The service-quality DAX layer is made up of **10 measures** in three groups:

| Group | Measures | Purpose |
|-------|----------|---------|
| **1. Rating bands** | `Neutral Ratings`, `Low Ratings`, `High Ratings` | Count touchpoint ratings per satisfaction band (1–2 / 3 / 4–5) |
| **2. Stage scores** | `Avg Ground Score`, `Digital Score`, `In-flight Score`, `Digital vs In-flight Gap` | Composite averages per journey stage |
| **3. Ratios** | `Average Rating`, `% Low Ratings`, `% High Ratings` | Normalised percentages and overall average |

All measures are designed for the passenger-level row and respect slicers on
`Customer Type`, `Travel Class`, `Type of Travel`, `Age Band`, `Distance Band`, etc.

---

## Measure index

| # | Measure name | Group | Format | Returns | Depends on |
|---|--------------|-------|--------|---------|------------|
| 1 | `Neutral Ratings` | Rating bands | Whole number | Count of rated-touchpoint = 3 | — |
| 2 | `Low Ratings` | Rating bands | Whole number | Count of rated-touchpoint ∈ {1,2} | — |
| 3 | `High Ratings` | Rating bands | Whole number | Count of rated-touchpoint ∈ {4,5} | — |
| 4 | `Avg Ground Score` | Stage scores | 1 dp, `/ 5` | Average of 3 ground touchpoints | — |
| 5 | `Digital Score` | Stage scores | 1 dp, `/ 5` | Average of 3 digital touchpoints | — |
| 6 | `In-flight Score` | Stage scores | 1 dp, `/ 5` | Average of 6 in-flight touchpoints | — |
| 7 | `Digital vs In-flight Gap` | Stage scores | 1 dp, signed | Difference of two stage scores | `Digital Score`, `In-flight Score` |
| 8 | `Average Rating` | Ratios | 1 dp, `/ 5` | Mean of all 14 touchpoints | — |
| 9 | `% Low Ratings` | Ratios | Percentage, 1 dp | Low-share of rated touchpoints | `Low Ratings`, `High Ratings`, `Neutral Ratings` |
| 10 | `% High Ratings` | Ratios | Percentage, 1 dp | High-share of rated touchpoints | `Low Ratings`, `High Ratings`, `Neutral Ratings` |

---

# Detailed measure catalogue

## 1. `Neutral Ratings`

| Property | Value |
|----------|-------|
| Group | Rating bands |
| Returns | Whole number |
| Dependencies | None |
| Format string | `#,0` |
| Display folder | `_Service Quality \ 1. Rating Bands` |

**Purpose.** Counts, per passenger, how many of the 14 touchpoints were rated **exactly 3**.
Used as the numerator of the "neutral share" and as a completeness check against
`Low Ratings` and `High Ratings`.

```dax
Neutral Ratings =
SUMX(
    'Airline Quality Ratings',
    IF('Airline Quality Ratings'[Departure and Arrival Time Convenience] = 3, 1, 0) +
    IF('Airline Quality Ratings'[Ease of Online Booking] = 3, 1, 0) +
    IF('Airline Quality Ratings'[Check-in Service] = 3, 1, 0) +
    IF('Airline Quality Ratings'[Online Boarding] = 3, 1, 0) +
    IF('Airline Quality Ratings'[Gate Location] = 3, 1, 0) +
    IF('Airline Quality Ratings'[On-board Service] = 3, 1, 0) +
    IF('Airline Quality Ratings'[Seat Comfort] = 3, 1, 0) +
    IF('Airline Quality Ratings'[Leg Room Service] = 3, 1, 0) +
    IF('Airline Quality Ratings'[Cleanliness] = 3, 1, 0) +
    IF('Airline Quality Ratings'[Food and Drink] = 3, 1, 0) +
    IF('Airline Quality Ratings'[In-flight Service] = 3, 1, 0) +
    IF('Airline Quality Ratings'[In-flight Wifi Service] = 3, 1, 0) +
    IF('Airline Quality Ratings'[In-flight Entertainment] = 3, 1, 0) +
    IF('Airline Quality Ratings'[Baggage Handling] = 3, 1, 0)
)
```

**Edge cases.**

- `0` (not applicable) → contributes **0** to the count (correct).
- `BLANK` → `IF(BLANK() = 3, 1, 0)` returns 0 (correct).
- `NULL` in SQL → DAX `BLANK` → contributes 0 (correct).

---

## 2. `Low Ratings`

| Property | Value |
|----------|-------|
| Group | Rating bands |
| Returns | Whole number |
| Dependencies | None |
| Format string | `#,0` |
| Display folder | `_Service Quality \ 1. Rating Bands` |

**Purpose.** Counts, per passenger, how many touchpoints were rated **1 or 2**. Numerator of
`% Low Ratings` and used directly in pain-point rankings.

```dax
Low Ratings =
SUMX(
    'Airline Quality Ratings',
    IF('Airline Quality Ratings'[Departure and Arrival Time Convenience] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[Ease of Online Booking] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[Check-in Service] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[Online Boarding] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[Gate Location] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[On-board Service] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[Seat Comfort] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[Leg Room Service] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[Cleanliness] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[Food and Drink] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[In-flight Service] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[In-flight Wifi Service] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[In-flight Entertainment] IN {1, 2}, 1, 0) +
    IF('Airline Quality Ratings'[Baggage Handling] IN {1, 2}, 1, 0)
)
```

**Edge cases.** `0` / `BLANK` / `NULL` → contributes 0 (correct).

---

## 3. `High Ratings`

| Property | Value |
|----------|-------|
| Group | Rating bands |
| Returns | Whole number |
| Dependencies | None |
| Format string | `#,0` |
| Display folder | `_Service Quality \ 1. Rating Bands` |

**Purpose.** Counts, per passenger, how many touchpoints were rated **4 or 5**. Numerator of
`% High Ratings` and used directly in delight-point rankings.

```dax
High Ratings =
SUMX(
    'Airline Quality Ratings',
    IF('Airline Quality Ratings'[Departure and Arrival Time Convenience] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[Ease of Online Booking] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[Check-in Service] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[Online Boarding] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[Gate Location] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[On-board Service] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[Seat Comfort] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[Leg Room Service] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[Cleanliness] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[Food and Drink] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[In-flight Service] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[In-flight Wifi Service] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[In-flight Entertainment] IN {4, 5}, 1, 0) +
    IF('Airline Quality Ratings'[Baggage Handling] IN {4, 5}, 1, 0)
)
```

**Edge cases.** `0` / `BLANK` / `NULL` → contributes 0 (correct).

**Invariant (when data is fully rated):**
`Low Ratings + Neutral Ratings + High Ratings = 14 × COUNTROWS(...)`.
Breaks only when any touchpoint is `0` or blank — see [Edge-case matrix](#edge-case-matrix).

---

## 4. `Avg Ground Score`

| Property | Value |
|----------|-------|
| Group | Stage scores |
| Returns | Decimal (1–5 scale) |
| Dependencies | None |
| Format string | `0.0" / 5"` |
| Display folder | `_Service Quality \ 2. Stage Scores` |

**Purpose.** Average rating across the three **ground** touchpoints:
Departure & Arrival Time Convenience, Check-in Service, Gate Location.
Interpreted on the same 1–5 scale as the underlying ratings (3 = neutral).

```dax
Avg Ground Score =
DIVIDE(
    SUM('Airline Quality Ratings'[Check-in Service]) +
    SUM('Airline Quality Ratings'[Gate Location]) +
    SUM('Airline Quality Ratings'[Departure and Arrival Time Convenience]),
    COUNTROWS('Airline Quality Ratings') * 3
)
```

**Edge cases.**

- `0` (not applicable) → included in the numerator sum, but denominator is fixed at `N × 3`
  → **drags the average down.** See [Caveats → 0-ratings](#caveat-1--0-ratings).
- Denominator of 0 (empty filter context) → `DIVIDE` returns `BLANK` (safe).

---

## 5. `Digital Score`

| Property | Value |
|----------|-------|
| Group | Stage scores |
| Returns | Decimal (1–5 scale) |
| Dependencies | None |
| Format string | `0.0" / 5"` |
| Display folder | `_Service Quality \ 2. Stage Scores` |

**Purpose.** Average rating across the three **digital** touchpoints:
Ease of Online Booking, Online Boarding, In-flight Wifi Service.

```dax
Digital Score =
DIVIDE(
    SUM('Airline Quality Ratings'[Ease of Online Booking]) +
    SUM('Airline Quality Ratings'[Online Boarding]) +
    SUM('Airline Quality Ratings'[In-flight Wifi Service]),
    COUNTROWS('Airline Quality Ratings') * 3
)
```

**Edge cases.** Same `0`-inclusion issue as `Avg Ground Score`.

---

## 6. `In-flight Score`

| Property | Value |
|----------|-------|
| Group | Stage scores |
| Returns | Decimal (1–5 scale) |
| Dependencies | None |
| Format string | `0.0" / 5"` |
| Display folder | `_Service Quality \ 2. Stage Scores` |

**Purpose.** Average rating across the six **in-flight** touchpoints:
On-board Service, Seat Comfort, Leg Room Service, Cleanliness, Food and Drink,
In-flight Entertainment.

```dax
In-flight Score =
DIVIDE(
    SUM('Airline Quality Ratings'[On-board Service]) +
    SUM('Airline Quality Ratings'[Seat Comfort]) +
    SUM('Airline Quality Ratings'[Leg Room Service]) +
    SUM('Airline Quality Ratings'[Cleanliness]) +
    SUM('Airline Quality Ratings'[Food and Drink]) +
    SUM('Airline Quality Ratings'[In-flight Entertainment]),
    COUNTROWS('Airline Quality Ratings') * 6
)
```

**Coverage note.** Does **not** include `In-flight Service` or `Baggage Handling` — see
[Caveats → Coverage mismatch](#caveat-2--coverage-mismatch).

---

## 7. `Digital vs In-flight Gap`

| Property | Value |
|----------|-------|
| Group | Stage scores |
| Returns | Signed decimal |
| Dependencies | `Digital Score`, `In-flight Score` |
| Format string | `+0.0;-0.0;0.0` |
| Display folder | `_Service Quality \ 2. Stage Scores` |

**Purpose.** Signed difference between digital and in-flight experience.
Positive → digital outperforms; negative → in-flight outperforms.

```dax
Digital vs In-flight Gap = [Digital Score] - [In-flight Score]
```

**Interpretation guide.**

| Value | Reading | Action |
|-------|---------|--------|
| `> +0.3` | Digital a clear strength, in-flight lagging | Prioritise cabin experience |
| `-0.3 … +0.3` | Stages balanced | Maintain both |
| `< -0.3` | In-flight outperforms; digital investment paying off less | Audit digital funnel (app / boarding / wifi) |

**Edge cases.** Returns `BLANK` if either component is `BLANK` — a natural consequence of DAX
`BLANK` propagation, which is desirable here (no misleading `0` gaps on empty filters).

---

## 8. `Average Rating`

| Property | Value |
|----------|-------|
| Group | Ratios |
| Returns | Decimal (1–5 scale) |
| Dependencies | None |
| Format string | `0.0" / 5"` |
| Display folder | `_Service Quality \ 3. Ratios` |

**Purpose.** Overall mean of all **14** touchpoints. This is the only measure that covers
the entire journey (unlike the composites, which cover 12). Use it as the single headline
quality number.

```dax
Average Rating =
DIVIDE(
    SUM('Airline Quality Ratings'[Departure and Arrival Time Convenience]) +
    SUM('Airline Quality Ratings'[Ease of Online Booking]) +
    SUM('Airline Quality Ratings'[Check-in Service]) +
    SUM('Airline Quality Ratings'[Online Boarding]) +
    SUM('Airline Quality Ratings'[Gate Location]) +
    SUM('Airline Quality Ratings'[On-board Service]) +
    SUM('Airline Quality Ratings'[Seat Comfort]) +
    SUM('Airline Quality Ratings'[Leg Room Service]) +
    SUM('Airline Quality Ratings'[Cleanliness]) +
    SUM('Airline Quality Ratings'[Food and Drink]) +
    SUM('Airline Quality Ratings'[In-flight Service]) +
    SUM('Airline Quality Ratings'[In-flight Wifi Service]) +
    SUM('Airline Quality Ratings'[In-flight Entertainment]) +
    SUM('Airline Quality Ratings'[Baggage Handling]),
    COUNTROWS('Airline Quality Ratings') * 14
)
```

**Edge cases.** Same `0`-inclusion issue as the stage scores.

---

## 9. `% Low Ratings`

| Property | Value |
|----------|-------|
| Group | Ratios |
| Returns | Percentage (0–1) |
| Dependencies | `Low Ratings`, `High Ratings`, `Neutral Ratings` |
| Format string | `0.0%` |
| Display folder | `_Service Quality \ 3. Ratios` |

**Purpose.** Share of **rated** touchpoints in the low band (1–2).

```dax
% Low Ratings =
DIVIDE(
    [Low Ratings],
    [Low Ratings] + [High Ratings] + [Neutral Ratings],
    0
)
```

**Edge cases.** When a filter returns zero rows, `DIVIDE(..., 0)` returns `0` (safe).
`% Low Ratings + % High Ratings + % Neutral` = 100% by construction, where
`% Neutral = DIVIDE([Neutral Ratings], [Low Ratings] + [High Ratings] + [Neutral Ratings], 0)`.

---

## 10. `% High Ratings`

| Property | Value |
|----------|-------|
| Group | Ratios |
| Returns | Percentage (0–1) |
| Dependencies | `Low Ratings`, `High Ratings`, `Neutral Ratings` |
| Format string | `0.0%` |
| Display folder | `_Service Quality \ 3. Ratios` |

**Purpose.** Share of **rated** touchpoints in the high band (4–5).

```dax
% High Ratings =
DIVIDE(
    [High Ratings],
    [Low Ratings] + [High Ratings] + [Neutral Ratings],
    0
)
```

**Reading.** Combine with `% Low Ratings` for a quick health check:
`% High − % Low` is a single-number satisfaction index (positive = net positive).

---

# Column reference

All 14 rating columns on `'Airline Quality Ratings'` with which measures use them:

| # | Column | Stage | In `Low/Neutral/High`? | In stage score? | In `Average Rating`? |
|---|--------|-------|:-:|:-:|:-:|
| 1 | Departure and Arrival Time Convenience | Ground | ✓ | ✓ `Avg Ground` | ✓ |
| 2 | Ease of Online Booking | Digital | ✓ | ✓ `Digital` | ✓ |
| 3 | Check-in Service | Ground | ✓ | ✓ `Avg Ground` | ✓ |
| 4 | Online Boarding | Digital | ✓ | ✓ `Digital` | ✓ |
| 5 | Gate Location | Ground | ✓ | ✓ `Avg Ground` | ✓ |
| 6 | On-board Service | In-flight | ✓ | ✓ `In-flight` | ✓ |
| 7 | Seat Comfort | In-flight | ✓ | ✓ `In-flight` | ✓ |
| 8 | Leg Room Service | In-flight | ✓ | ✓ `In-flight` | ✓ |
| 9 | Cleanliness | In-flight | ✓ | ✓ `In-flight` | ✓ |
| 10 | Food and Drink | In-flight | ✓ | ✓ `In-flight` | ✓ |
| 11 | In-flight Service | In-flight | ✓ | ❌ | ✓ |
| 12 | In-flight Wifi Service | Digital | ✓ | ✓ `Digital` | ✓ |
| 13 | In-flight Entertainment | In-flight | ✓ | ✓ `In-flight` | ✓ |
| 14 | Baggage Handling | Ground | ✓ | ❌ | ✓ |

Two columns (11, 14) are visible in `Average Rating` but invisible to every stage score —
see [Caveat 2](#caveat-2--coverage-mismatch).

---

# Edge-case matrix

How each measure behaves on the three non-standard input values:

| Input | `Low Ratings` | `Neutral Ratings` | `High Ratings` | `Avg Ground` / `Digital` / `In-flight` / `Average Rating` | `% Low` / `% High` |
|-------|:-:|:-:|:-:|:-:|:-:|
| `1` | +1 | 0 | 0 | included in numerator and denominator | counted |
| `3` | 0 | +1 | 0 | included | counted |
| `5` | 0 | 0 | +1 | included | counted |
| `0` (not applicable) | 0 | 0 | 0 | **included in numerator** (bug — drags avg down) | **excluded** (correct) |
| `BLANK` / `NULL` | 0 | 0 | 0 | ignored by `SUM` (effectively 0 in numerator) | **excluded** (correct) |

**Only the composite averages are affected** by the `0` issue. The band counts and the
percentages are correct as written.

---

# Caveats

## Caveat 1 — `0` ratings

The source data uses `0` to mean *"not applicable"* (a touchpoint that did not apply).
As written:

- **`Low / Neutral / High Ratings`** — correct (a `0` counts for nothing).
- **`% Low / % High`** — correct (a `0` is excluded from both numerator and denominator).
- **`Avg Ground Score` / `Digital Score` / `In-flight Score` / `Average Rating`** — **incorrect.**
  `SUM()` includes the `0` in the numerator but the denominator stays at `N × K`, so any
  passenger with a not-applicable touchpoint pulls the average down.

**Fix (recommended).** At the Power Query layer, replace `0` with `null` in all 14 rating
columns. This makes every downstream measure correct without touching DAX, and it aligns
with the SQL view where `NULLIF(col, 0)` already does this.

**Alternative fix (DAX only).** Replace the numerator
`SUM('Airline Quality Ratings'[Col])`
with
`SUMX('Airline Quality Ratings', IF('Airline Quality Ratings'[Col] <> 0, 'Airline Quality Ratings'[Col], BLANK()))`
and replace the denominator `COUNTROWS(...) * K` with a `SUMX` that counts non-blank ratings.
More verbose; harder to review; slower at scale. Prefer the Power Query fix.

## Caveat 2 — Coverage mismatch

`In-flight Service` and `Baggage Handling` are counted by `Average Rating` but not by any
stage score. The composites therefore cover **12 of the 14** touchpoints and are not directly
comparable to the overall average.

**Options.**

- **A (recommended).** Add `In-flight Service` to `In-flight Score` (`* 6` → `* 7`) and
  `Baggage Handling` to `Avg Ground Score` (`* 3` → `* 4`). Composites then tile the whole
  journey and sum-check against `Average Rating`.
- **B.** Leave as-is; document in the tooltip that `Average Rating` is the full-coverage
  number and the composites are diagnostic.
- **C.** Rename to `Partial In-flight Score` / `Partial Ground Score` to signal intent.

Pick one and apply it consistently across the report.

---

# Display folders and format strings

Recommended Power BI model organisation:

| Display folder | Measures | Format string |
|----------------|----------|---------------|
| `_Service Quality \ 1. Rating Bands` | `Neutral Ratings`, `Low Ratings`, `High Ratings` | `#,0` |
| `_Service Quality \ 2. Stage Scores` | `Avg Ground Score`, `Digital Score`, `In-flight Score` | `0.0" / 5"` |
| `_Service Quality \ 2. Stage Scores` | `Digital vs In-flight Gap` | `+0.0;-0.0;0.0` |
| `_Service Quality \ 3. Ratios` | `Average Rating` | `0.0" / 5"` |
| `_Service Quality \ 3. Ratios` | `% Low Ratings`, `% High Ratings` | `0.0%` |

---

# Validation queries (DAX Studio / Power BI Q&A)

Run these in DAX Studio against the model to verify the measures before publishing.

**V1 — band counts sum to expected total (fully rated data):**

```dax
EVALUATE
ROW(
    "rated_touchpoints", [Low Ratings] + [Neutral Ratings] + [High Ratings],
    "expected",          COUNTROWS('Airline Quality Ratings') * 14,
    "diff",              [Low Ratings] + [Neutral Ratings] + [High Ratings]
                         - COUNTROWS('Airline Quality Ratings') * 14
)
-- Expect diff = 0 only if no touchpoint is 0 or BLANK.
-- Non-zero diff reveals exactly how many not-applicable touchpoints exist.

```

**V2 — percentages are internally consistent:**

```dax
EVALUATE
ROW(
    "total_pct", [% Low Ratings] + [% High Ratings]
                 + DIVIDE([Neutral Ratings],
                          [Low Ratings] + [High Ratings] + [Neutral Ratings], 0)
)
-- Expect 1.0 (100%) when at least one touchpoint is rated.
```

**V3 — stage score bounds (must be within 1–5, or BLANK):**

```dax
EVALUATE
ROW(
    "ground_min",   MINX('Airline Quality Ratings', [Avg Ground Score]),
    "ground_max",   MAXX('Airline Quality Ratings', [Avg Ground Score]),
    "digital_min",  MINX('Airline Quality Ratings', [Digital Score]),
    "digital_max",  MAXX('Airline Quality Ratings', [Digital Score]),
    "inflight_min", MINX('Airline Quality Ratings', [In-flight Score]),
    "inflight_max", MAXX('Airline Quality Ratings', [In-flight Score])
)
-- Any value outside 1..5 signals a data-quality issue (usually a >5 rating).
```

**V4 — coverage audit (how many touchpoints per row are rated):**

```dax
EVALUATE
SUMMARIZECOLUMNS(
    "rows_with_all_14_rated",
        CALCULATE(
            COUNTROWS('Airline Quality Ratings'),
            FILTER('Airline Quality Ratings',
                [Low Ratings] + [Neutral Ratings] + [High Ratings] = 14)
        ),
    "total_rows", COUNTROWS('Airline Quality Ratings')
)
-- The gap between the two numbers is the population affected by Caveat 1.
```

---

# Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-10-24 | Initial consolidation of all 10 measures with metadata, edge cases, and validation queries. |

---

# Related documents

- `python/docs/airline_service_quality_measures.md` — this file
- `python/docs/airline_satisfaction_ml.md` — ML pipeline reference (Python package + notebook)
- SQL layer: `01_create_schema.sql`, `02_data_profiling.sql`, `03_structuring_views.sql`, `04_intelligence_layers.sql`
- Power BI model: `AirlineSatisfaction.pbix` (measure definitions, RLS, report pages)