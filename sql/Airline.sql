/* =====================================================================
   AIRLINE PASSENGER SATISFACTION: SQL BI WORKFLOW (PostgreSQL)
   Layers:  0 Raw table | 1 Profiling | 2 Clean view
            3 Intelligence layer (features, long view, ML set)
            4 Analysis for the 10 business questions
=========================================================================== */
   
/* =====================  0. RAW TABLE  ===================== */
	CREATE TABLE IF NOT EXISTS airline_raw (
	    id                      INT,
	    gender                  TEXT,
	    age                     INT,
	    customer_type           TEXT,
	    type_of_travel          TEXT,
	    travel_class            TEXT,
	    flight_distance         INT,
	    departure_delay         INT,
	    arrival_delay           NUMERIC,
	    dep_arr_time_convenient INT,
	    ease_of_online_booking  INT,
	    checkin_service         INT,
	    online_boarding         INT,
	    gate_location           INT,
	    onboard_service         INT,
	    seat_comfort            INT,
	    leg_room_service        INT,
	    cleanliness             INT,
	    food_and_drink          INT,
	    inflight_service        INT,
	    inflight_wifi           INT,
	    inflight_entertainment  INT,
	    baggage_handling        INT,
	    satisfaction            TEXT
	);
	
-- Load: \copy airline_raw FROM 'airline.csv' CSV HEADER;
-- the data has been successfully loaded; 


/* =====================  1. DATA PROFILING  ===================== */

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


/* =====================  2. CLEAN VIEW  ===================== */
-- Decisions: dedupe on id, standardise labels, rating 0 -> NULL (not applicable),
-- missing arrival_delay imputed with departure_delay (flagged).
	CREATE OR REPLACE VIEW vw_airline_clean AS
	SELECT DISTINCT ON (id)
	    id,
	    INITCAP(TRIM(gender))                                             AS gender,
	    age,
	    CASE WHEN LOWER(customer_type) LIKE 'loyal%' THEN 'Loyal' ELSE 'Disloyal' END AS customer_type,
	    CASE WHEN LOWER(type_of_travel) LIKE 'business%' THEN 'Business' ELSE 'Personal' END AS travel_type,
	    TRIM(travel_class)                                                AS travel_class,
	    flight_distance,
	    departure_delay,
	    COALESCE(arrival_delay, departure_delay)                          AS arrival_delay,
	    (arrival_delay IS NULL)                                           AS arrival_delay_imputed,
	    NULLIF(dep_arr_time_convenient, 0) AS time_convenience,
	    NULLIF(ease_of_online_booking, 0)  AS online_booking,
	    NULLIF(checkin_service, 0)         AS checkin,
	    NULLIF(online_boarding, 0)         AS online_boarding,
	    NULLIF(gate_location, 0)           AS gate_location,
	    NULLIF(onboard_service, 0)         AS onboard_service,
	    NULLIF(seat_comfort, 0)            AS seat_comfort,
	    NULLIF(leg_room_service, 0)        AS leg_room,
	    NULLIF(cleanliness, 0)             AS cleanliness,
	    NULLIF(food_and_drink, 0)          AS food_drink,
	    NULLIF(inflight_service, 0)        AS inflight_service,
	    NULLIF(inflight_wifi, 0)           AS wifi,
	    NULLIF(inflight_entertainment, 0)  AS entertainment,
	    NULLIF(baggage_handling, 0)        AS baggage,
	    CASE WHEN LOWER(TRIM(satisfaction)) = 'satisfied' THEN 1 ELSE 0 END AS satisfied_flag
	FROM airline_raw
	WHERE id IS NOT NULL
	ORDER BY id;


/* =====================  3. INTELLIGENCE LAYER  ===================== */

-- 3.1 Feature view: bands, flags, composite scores, weakest touchpoint
	CREATE OR REPLACE VIEW vw_passenger_features AS
	SELECT
	    c.*,
	    CASE WHEN age < 18 THEN '<18'   WHEN age <= 24 THEN '18-24'
	         WHEN age <= 34 THEN '25-34' WHEN age <= 44 THEN '35-44'
	         WHEN age <= 54 THEN '45-54' WHEN age <= 64 THEN '55-64'
	         ELSE '65+' END                                         AS age_band,
	    CASE WHEN flight_distance < 1000 THEN 'Short'
	         WHEN flight_distance < 2500 THEN 'Medium'
	         ELSE 'Long' END                                        AS distance_band,
	    CASE WHEN departure_delay = 0 THEN '0 On time'
	         WHEN departure_delay <= 15 THEN '1-15 min'
	         WHEN departure_delay <= 60 THEN '16-60 min'
	         WHEN departure_delay <= 120 THEN '61-120 min'
	         ELSE '120+ min' END                                    AS dep_delay_band,
	    CASE WHEN arrival_delay = 0 THEN '0 On time'
	         WHEN arrival_delay <= 15 THEN '1-15 min'
	         WHEN arrival_delay <= 60 THEN '16-60 min'
	         WHEN arrival_delay <= 120 THEN '61-120 min'
	         ELSE '120+ min' END                                    AS arr_delay_band,
	    (departure_delay > 15)::INT                                 AS dep_delayed_flag,
	    (arrival_delay > 15)::INT                                   AS arr_delayed_flag,
	    arrival_delay - departure_delay                             AS delay_recovery,
	    s.avg_service_score,
	    s.digital_score,
	    s.inflight_score,
	    s.ground_score,
	    w.weakest_touchpoint,
	    (c.travel_class = 'Business' AND c.customer_type = 'Loyal')::INT AS high_value_flag
	FROM vw_airline_clean c
	CROSS JOIN LATERAL (
	    SELECT
	        ROUND((SELECT AVG(x) FROM UNNEST(ARRAY[c.time_convenience, c.online_booking, c.checkin,
	              c.online_boarding, c.gate_location, c.onboard_service, c.seat_comfort, c.leg_room,
	              c.cleanliness, c.food_drink, c.inflight_service, c.wifi, c.entertainment,
	              c.baggage]) x)::NUMERIC, 2) AS avg_service_score,
	        ROUND((SELECT AVG(x) FROM UNNEST(ARRAY[c.online_booking, c.online_boarding, c.wifi]) x)::NUMERIC, 2) AS digital_score,
	        ROUND((SELECT AVG(x) FROM UNNEST(ARRAY[c.seat_comfort, c.leg_room, c.food_drink,
	              c.inflight_service, c.entertainment, c.cleanliness, c.onboard_service]) x)::NUMERIC, 2) AS inflight_score,
	        ROUND((SELECT AVG(x) FROM UNNEST(ARRAY[c.checkin, c.gate_location, c.baggage,
	              c.time_convenience]) x)::NUMERIC, 2) AS ground_score
	) s
	CROSS JOIN LATERAL (
	    SELECT v.name AS weakest_touchpoint
	    FROM (VALUES
	        ('time_convenience', c.time_convenience), ('online_booking', c.online_booking),
	        ('checkin', c.checkin), ('online_boarding', c.online_boarding),
	        ('gate_location', c.gate_location), ('onboard_service', c.onboard_service),
	        ('seat_comfort', c.seat_comfort), ('leg_room', c.leg_room),
	        ('cleanliness', c.cleanliness), ('food_drink', c.food_drink),
	        ('inflight_service', c.inflight_service), ('wifi', c.wifi),
	        ('entertainment', c.entertainment), ('baggage', c.baggage)
	    ) v(name, score)
	    WHERE v.score IS NOT NULL
	    ORDER BY v.score, v.name
	    LIMIT 1
	) w;

-- 3.2 Long (unpivoted) ratings view: one row per passenger per touchpoint
	CREATE OR REPLACE VIEW vw_ratings_long AS
	SELECT f.id, t.touchpoint, t.stage, t.score,
	       f.satisfied_flag, f.gender, f.age_band, f.customer_type, f.travel_type,
	       f.travel_class, f.distance_band
	FROM vw_passenger_features f
	CROSS JOIN LATERAL (VALUES
	    ('time_convenience', 'Ground',    f.time_convenience),
	    ('online_booking',   'Digital',   f.online_booking),
	    ('checkin',          'Ground',    f.checkin),
	    ('online_boarding',  'Digital',   f.online_boarding),
	    ('gate_location',    'Ground',    f.gate_location),
	    ('onboard_service',  'In-flight', f.onboard_service),
	    ('seat_comfort',     'In-flight', f.seat_comfort),
	    ('leg_room',         'In-flight', f.leg_room),
	    ('cleanliness',      'In-flight', f.cleanliness),
	    ('food_drink',       'In-flight', f.food_drink),
	    ('inflight_service', 'In-flight', f.inflight_service),
	    ('wifi',             'Digital',   f.wifi),
	    ('entertainment',    'In-flight', f.entertainment),
	    ('baggage',          'Ground',    f.baggage)
	) t(touchpoint, stage, score)
	WHERE t.score IS NOT NULL;

-- 3.3 ML-ready table: encoded features, target, reproducible train/test split
-- Notes: composite scores are derived from the ratings, so drop them if you use raw ratings (avoid redundancy).
--        Leakage check: nothing here is computed from the target.
	CREATE OR REPLACE VIEW ml_training_set AS
	SELECT
	    id,
	    satisfied_flag                                   AS target,
	    age,
	    flight_distance,
	    departure_delay,
	    arrival_delay,
	    delay_recovery,
	    dep_delayed_flag,
	    arr_delayed_flag,
	    (gender = 'Female')::INT                         AS is_female,
	    (customer_type = 'Loyal')::INT                   AS is_loyal,
	    (travel_type = 'Business')::INT                  AS is_business_travel,
	    (travel_class = 'Business')::INT                 AS class_business,
	    (travel_class = 'Eco Plus')::INT                 AS class_eco_plus,
	    -- ratings: NULL (not applicable) kept as NULL; add *_missing flags, then impute in Python
	    time_convenience, online_booking, checkin, online_boarding, gate_location,
	    onboard_service, seat_comfort, leg_room, cleanliness, food_drink,
	    inflight_service, wifi, entertainment, baggage,
	    (wifi IS NULL)::INT                              AS wifi_na,
	    (online_booking IS NULL)::INT                    AS online_booking_na,
	    avg_service_score, digital_score, inflight_score, ground_score,
	    CASE WHEN MOD(ABS(hashtext(id::TEXT)), 10) < 8 THEN 'train' ELSE 'test' END AS split
	FROM vw_passenger_features;

-- 3.4 Segment-level summary table (useful for clustering / BI dashboards)
	CREATE OR REPLACE VIEW vw_segment_summary AS
	SELECT travel_class, customer_type, travel_type, distance_band,
	       COUNT(*)                                         AS passengers,
	       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_passengers,
	       ROUND(100.0 * AVG(satisfied_flag), 1)            AS satisfaction_pct,
	       ROUND(AVG(avg_service_score), 2)                 AS avg_service_score,
	       ROUND(AVG(departure_delay), 1)                   AS avg_dep_delay
	FROM vw_passenger_features
	GROUP BY travel_class, customer_type, travel_type, distance_band;


/* =====================  4. BUSINESS QUESTIONS  ===================== */

-- Q1. Overall satisfaction, by gender and age band
	SELECT 'Overall' AS segment, 'All' AS grp, COUNT(*) AS passengers,
	       ROUND(100.0 * AVG(satisfied_flag), 1) AS satisfaction_pct
	FROM vw_passenger_features
	UNION ALL
	SELECT 'Gender', gender, COUNT(*), ROUND(100.0 * AVG(satisfied_flag), 1)
	FROM vw_passenger_features GROUP BY gender
	UNION ALL
	SELECT 'Age band', age_band, COUNT(*), ROUND(100.0 * AVG(satisfied_flag), 1)
	FROM vw_passenger_features GROUP BY age_band
	ORDER BY segment, grp;

-- Q2. Satisfaction by travel class, with gap versus the best class
	WITH c AS (
	    SELECT travel_class, COUNT(*) AS passengers,
	           ROUND(100.0 * AVG(satisfied_flag), 1) AS satisfaction_pct
	    FROM vw_passenger_features GROUP BY travel_class
	)
	SELECT travel_class, passengers, satisfaction_pct,
	       satisfaction_pct - MAX(satisfaction_pct) OVER () AS gap_vs_best_pts
	FROM c ORDER BY satisfaction_pct;

-- Q3. Business vs personal travel, split by class
	SELECT travel_type, travel_class, COUNT(*) AS passengers,
	       ROUND(100.0 * AVG(satisfied_flag), 1) AS satisfaction_pct,
	       ROUND(AVG(avg_service_score), 2)      AS avg_service_score
	FROM vw_passenger_features
	GROUP BY travel_type, travel_class
	ORDER BY travel_type, satisfaction_pct DESC;

-- Q4. Loyal vs disloyal, and where loyalty is not translating into satisfaction
	SELECT customer_type, travel_type, COUNT(*) AS passengers,
	       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct,
	       ROUND(100.0 * AVG(satisfied_flag), 1)              AS satisfaction_pct
	FROM vw_passenger_features
	GROUP BY customer_type, travel_type
	ORDER BY customer_type, travel_type;

-- Q5. Lowest-rated touchpoints (average and % of low ratings)
	SELECT touchpoint, stage,
	       ROUND(AVG(score), 2)                                       AS avg_rating,
	       ROUND(100.0 * AVG((score <= 2)::INT), 1)                   AS pct_low_ratings,
	       RANK() OVER (ORDER BY AVG(score))                          AS weakness_rank
	FROM vw_ratings_long
	GROUP BY touchpoint, stage
	ORDER BY avg_rating;

-- Q6. Which touchpoints drive satisfaction? (correlation + satisfaction lift)
	SELECT touchpoint,
	       ROUND(CORR(score, satisfied_flag)::NUMERIC, 3)                              AS corr_with_satisfaction,
	       ROUND(100.0 * AVG(satisfied_flag) FILTER (WHERE score >= 4), 1)             AS sat_pct_when_high,
	       ROUND(100.0 * AVG(satisfied_flag) FILTER (WHERE score <= 2), 1)             AS sat_pct_when_low,
	       ROUND(100.0 * (AVG(satisfied_flag) FILTER (WHERE score >= 4)
	                    - AVG(satisfied_flag) FILTER (WHERE score <= 2)), 1)           AS lift_pts
	FROM vw_ratings_long
	GROUP BY touchpoint
	ORDER BY corr_with_satisfaction DESC;

-- Q7. Delay impact on satisfaction
	SELECT dep_delay_band, COUNT(*) AS passengers,
	       ROUND(100.0 * AVG(satisfied_flag), 1) AS satisfaction_pct
	FROM vw_passenger_features
	GROUP BY dep_delay_band
	ORDER BY MIN(departure_delay);
	
	SELECT arr_delay_band, COUNT(*) AS passengers,
	       ROUND(100.0 * AVG(satisfied_flag), 1) AS satisfaction_pct
	FROM vw_passenger_features
	GROUP BY arr_delay_band
	ORDER BY MIN(arrival_delay);

-- Q7b. Does recovering delay in the air rescue satisfaction? (departed late only)
	SELECT CASE WHEN delay_recovery < 0 THEN 'Recovered time'
	            WHEN delay_recovery = 0 THEN 'Same delay'
	            ELSE 'Lost more time' END AS in_flight_effect,
	       COUNT(*) AS passengers,
	       ROUND(100.0 * AVG(satisfied_flag), 1) AS satisfaction_pct
	FROM vw_passenger_features
	WHERE departure_delay > 15
	GROUP BY 1
	ORDER BY satisfaction_pct DESC;

-- Q8. Do drivers change by distance band? (correlation per band)
	SELECT touchpoint,
	       ROUND(CORR(score, satisfied_flag) FILTER (WHERE distance_band = 'Short')::NUMERIC,  3) AS short_haul,
	       ROUND(CORR(score, satisfied_flag) FILTER (WHERE distance_band = 'Medium')::NUMERIC, 3) AS medium_haul,
	       ROUND(CORR(score, satisfied_flag) FILTER (WHERE distance_band = 'Long')::NUMERIC,   3) AS long_haul
	FROM vw_ratings_long
	GROUP BY touchpoint
	ORDER BY long_haul DESC;

-- Q9. Digital touchpoints by age band
	SELECT age_band,
	       COUNT(*)                                  AS passengers,
	       ROUND(AVG(online_booking), 2)             AS online_booking,
	       ROUND(AVG(online_boarding), 2)            AS online_boarding,
	       ROUND(AVG(wifi), 2)                       AS wifi,
	       ROUND(AVG(digital_score), 2)              AS digital_score,
	       ROUND(100.0 * AVG(satisfied_flag), 1)     AS satisfaction_pct
	FROM vw_passenger_features
	GROUP BY age_band
	ORDER BY MIN(age);

-- Q10. Priority intervention list: low satisfaction x high exposure
	WITH seg AS (
	    SELECT travel_class, customer_type, travel_type, distance_band,
	           COUNT(*) AS passengers,
	           SUM(1 - satisfied_flag) AS unsatisfied_passengers,
	           AVG(satisfied_flag) AS sat_rate
	    FROM vw_passenger_features
	    GROUP BY travel_class, customer_type, travel_type, distance_band
	    HAVING COUNT(*) >= 200            -- to ignore tiny segments
	)
	SELECT travel_class, customer_type, travel_type, distance_band,
	       passengers,
	       unsatisfied_passengers,
	       ROUND(100.0 * sat_rate, 1)                                   AS satisfaction_pct,
	       ROUND(100.0 * passengers / SUM(passengers) OVER (), 2)       AS exposure_pct,
	       ROUND(100.0 * unsatisfied_passengers / SUM(unsatisfied_passengers) OVER (), 2) AS share_of_all_dissatisfaction_pct,
	       RANK() OVER (ORDER BY unsatisfied_passengers DESC)           AS priority_rank
	FROM seg
	ORDER BY priority_rank
	LIMIT 15;
