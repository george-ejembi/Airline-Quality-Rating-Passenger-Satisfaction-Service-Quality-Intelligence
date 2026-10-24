/* =====================================================================
   01_create_schema.sql
   Layer 0: Raw table definition for airline passenger satisfaction
   Prerequisite for files 02, 03, 04.  Run this first.
=========================================================================== */

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