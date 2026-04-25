-- Create raw schema
create schema if not exists raw;

-- Create raw weather forecast table
create table if not exists raw.weather_forecast (
    -- Forecast identifiers
    dt bigint,
    dt_txt timestamp,

    -- Probability / visibility
    pop numeric(6,3),
    visibility integer,
    sys_pod text,

    -- Temperature & pressure
    main_temp numeric(10,2),
    main_temp_kf numeric(10,2),
    main_humidity integer,
    main_pressure integer,
    main_temp_max numeric(10,2),
    main_temp_min numeric(10,2),
    main_sea_level integer,
    main_feels_like numeric(10,2),
    main_grnd_level integer,

    -- Wind
    wind_deg integer,
    wind_gust numeric(10,2),
    wind_speed numeric(10,2),

    -- Clouds / precipitation
    clouds_all integer,
    rain_3h numeric(10,3),
    snow_3h numeric(10,3),

    -- Weather description
    weather_id integer,
    weather_icon text,
    weather_main text,
    weather_description text,

    -- City info
    city_id bigint,
    city_name text,
    city_sunset bigint,
    city_country text,
    city_sunrise bigint,
    city_timezone integer,
    city_population bigint,
    city_coord_lat numeric(10,6),
    city_coord_lon numeric(10,6),

    -- Pipeline metadata
    source_file_name text not null,
    source_file_ts timestamp not null,
    ingested_at timestamp not null default current_timestamp,
    dag_run_id text
);

