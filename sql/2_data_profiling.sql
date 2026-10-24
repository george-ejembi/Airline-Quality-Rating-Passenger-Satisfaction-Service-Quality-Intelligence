/* =====================================================================
   02_data_profiling.sql
   Layer 1: Data profiling (volume, nulls, distributions, outliers)
   Requires: 01_create_schema.sql (airline_raw must be loaded)
=========================================================================== */

-- 1.1 Volume and duplicate IDs
SELECT COUNT(*)                        AS total_rows,
       COUNT(DISTINCT id)              AS distinct_ids,
       COUNT(*) - COUNT(DISTINCT id)   AS duplicate_ids
FROM airline_raw;

-- 1.2 Duplicate records ignoring id
SELECT COUNT(*) AS duplicated_profiles
FROM (
    SELECT 1
    FROM airline_raw
    GROUP BY gender, age, customer_type, type_of_travel, travel_class,
             flight_distance, departure_delay, arrival_delay,
             dep_arr_time_convenient, ease_of_online_booking, checkin_service,
             online_boarding, gate_location, onboard_service, seat_comfort,
             leg_room_service, cleanliness, food_and_drink, inflight_service,
             inflight_wifi, inflight_entertainment, baggage_handling, satisfaction
    HAVING COUNT(*) > 1
) d;

-- 1.3 Null count per column
SELECT j.key AS column_name,
       COUNT(*) FILTER (WHERE j.value IS NULL)                               AS null_count,
       ROUND(100.0 * COUNT(*) FILTER (WHERE j.value IS NULL) / COUNT(*), 2)  AS null_pct
FROM airline_raw r
CROSS JOIN LATERAL jsonb_each_text(to_jsonb(r)) j
GROUP BY j.key
ORDER BY null_count DESC;

-- 1.4 Categorical value distributions (spot typos / inconsistent labels)
SELECT 'gender' AS col, gender AS val, COUNT(*) AS n FROM airline_raw GROUP BY gender
UNION ALL SELECT 'customer_type', customer_type, COUNT(*) FROM airline_raw GROUP BY customer_type
UNION ALL SELECT 'type_of_travel', type_of_travel, COUNT(*) FROM airline_raw GROUP BY type_of_travel
UNION ALL SELECT 'travel_class', travel_class, COUNT(*) FROM airline_raw GROUP BY travel_class
UNION ALL SELECT 'satisfaction', satisfaction, COUNT(*) FROM airline_raw GROUP BY satisfaction
ORDER BY col, n DESC;

-- 1.5 Numeric profile
SELECT 'age' AS col, MIN(age) mn, MAX(age) mx, ROUND(AVG(age),1) avg_,
       ROUND(STDDEV(age),1) sd,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY age) median
FROM airline_raw
UNION ALL
SELECT 'flight_distance', MIN(flight_distance), MAX(flight_distance), ROUND(AVG(flight_distance),1),
       ROUND(STDDEV(flight_distance),1), PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY flight_distance)
FROM airline_raw
UNION ALL
SELECT 'departure_delay', MIN(departure_delay), MAX(departure_delay), ROUND(AVG(departure_delay),1),
       ROUND(STDDEV(departure_delay),1), PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY departure_delay)
FROM airline_raw
UNION ALL
SELECT 'arrival_delay', MIN(arrival_delay), MAX(arrival_delay), ROUND(AVG(arrival_delay),1),
       ROUND(STDDEV(arrival_delay),1), PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY arrival_delay)
FROM airline_raw;

-- 1.6 Rating distribution per touchpoint (0 = "not applicable"; anything outside 0-5 is invalid)
WITH long_raw AS (
    SELECT t.touchpoint, t.score
    FROM airline_raw r
    CROSS JOIN LATERAL (VALUES
        ('time_convenience', r.dep_arr_time_convenient), ('online_booking', r.ease_of_online_booking),
        ('checkin', r.checkin_service), ('online_boarding', r.online_boarding),
        ('gate_location', r.gate_location), ('onboard_service', r.onboard_service),
        ('seat_comfort', r.seat_comfort), ('leg_room', r.leg_room_service),
        ('cleanliness', r.cleanliness), ('food_drink', r.food_and_drink),
        ('inflight_service', r.inflight_service), ('wifi', r.inflight_wifi),
        ('entertainment', r.inflight_entertainment), ('baggage', r.baggage_handling)
    ) t(touchpoint, score)
)
SELECT touchpoint,
       COUNT(*) FILTER (WHERE score = 0)                      AS zeros_na,
       ROUND(100.0 * COUNT(*) FILTER (WHERE score = 0) / COUNT(*), 2) AS zero_pct,
       COUNT(*) FILTER (WHERE score NOT BETWEEN 0 AND 5)      AS invalid_values,
       COUNT(*) FILTER (WHERE score IS NULL)                  AS nulls
FROM long_raw
GROUP BY touchpoint
ORDER BY zero_pct DESC;

-- 1.7 Outliers and logic checks
SELECT
    COUNT(*) FILTER (WHERE age < 5 OR age > 100)                       AS suspicious_age,
    COUNT(*) FILTER (WHERE flight_distance <= 0)                       AS bad_distance,
    COUNT(*) FILTER (WHERE departure_delay < 0 OR arrival_delay < 0)   AS negative_delays,
    COUNT(*) FILTER (WHERE departure_delay > 0 AND arrival_delay = 0)  AS full_recovery_flights,
    COUNT(*) FILTER (WHERE arrival_delay IS NULL)                      AS missing_arrival_delay
FROM airline_raw;

-- 1.8 Delay outliers (IQR rule)
WITH q AS (
    SELECT PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY departure_delay) q1,
           PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY departure_delay) q3
    FROM airline_raw
)
SELECT COUNT(*) AS dep_delay_outliers, q.q3 + 1.5*(q.q3 - q.q1) AS upper_fence
FROM airline_raw, q
WHERE departure_delay > q.q3 + 1.5*(q.q3 - q.q1)
GROUP BY q.q3, q.q1;