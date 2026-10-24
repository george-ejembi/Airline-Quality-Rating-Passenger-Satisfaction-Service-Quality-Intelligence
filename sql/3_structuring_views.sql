/* =====================================================================
   03_structuring_views.sql
   Layer 2: Clean view — dedupe, standardise labels, treat 0 as NA,
            impute missing arrival_delay from departure_delay (flagged).
   Requires: 01_create_schema.sql
   Produces: vw_airline_clean
=========================================================================== */

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