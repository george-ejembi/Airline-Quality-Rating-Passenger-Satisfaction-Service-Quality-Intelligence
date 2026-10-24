# Airline Service Quality — DAX Measures Reference

**Table:** `'Airline Quality Ratings'`  
**Grain:** one row per passenger  
**Rating scale:** 1–5 Likert (`0` or `BLANK` = "not applicable" — see [Caveats](#caveats))

This document defines the service-quality DAX layer used in the Power BI report. It is
split into three measure groups:

| Group | Purpose | Measures |
|-------|---------|----------|
| **1. Rating bands** | Count how many touchpoints fall in each satisfaction band | `Neutral Ratings`, `Low Ratings`, `High Ratings` |
| **2. Stage scores** | Average rating per journey stage (Ground / Digital / In-flight) | `Avg Ground Score`, `Digital Score`, `In-flight Score`, `Digital vs In-flight Gap` |
| **3. Ratios** | Normalised percentages and overall average | `Average Rating`, `% Low Ratings`, `% High Ratings` |

Measures are intended to be used with the passenger-level table as the filter context
(slicers on `Customer Type`, `Travel Class`, `Type of Travel`, `Age Band`, etc.).

---

## Table of contents

1. [Rating bands](#1-rating-bands)
2. [Stage scores](#2-stage-scores)
3. [Ratios and averages](#3-ratios-and-averages)
4. [Dependency graph](#dependency-graph)
5. [Suggested display folders](#suggested-display-folders)
6. [Caveats](#caveats)

---

## 1. Rating bands

These three measures count how many of the **14 touchpoint ratings** on each passenger row
fall into each band. Each measure iterates the table row-by-row via `SUMX`, adds 1 for
every column matching the band, and sums the row totals.

### Band definitions

| Band | Rating values | Meaning |
|------|---------------|---------|
| **Low** | 1, 2 | Dissatisfied |
| **Neutral** | 3 | Neither satisfied nor dissatisfied |
| **High** | 4, 5 | Satisfied |

### `Neutral Ratings`

Counts touchpoints rated **exactly 3**.

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