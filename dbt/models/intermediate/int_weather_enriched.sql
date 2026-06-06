{{ config(materialized='view', schema='intermediate') }}

select
    local_dt,
    city_id,
    city_name,
    city_country,
    main_temp,
    main_temp_min,
    main_temp_max,
    main_feels_like,
    main_humidity,
    wind_speed,
    wind_gust,
    clouds_all,
    rain_3h,
    snow_3h,
    weather_main,
    weather_description,
    weather_id,
    pop,

    case
        when main_temp < 32 then 'freezing'
        when main_temp < 55 then 'cold'
        when main_temp < 70 then 'mild'
        when main_temp < 85 then 'warm'
        else 'hot'
    end as temp_category,

    case
        when wind_speed < 5 then 'calm'
        when wind_speed < 15 then 'light'
        when wind_speed < 25 then 'moderate'
        when wind_speed < 40 then 'strong'
        else 'storm'
    end as wind_category,

    case
        when coalesce(rain_3h, 0) > 0 and coalesce(snow_3h, 0) > 0 then 'rain_and_snow'
        when coalesce(rain_3h, 0) > 0 then 'rain'
        when coalesce(snow_3h, 0) > 0 then 'snow'
        else 'none'
    end as precip_type

from {{ ref('stg_weather__forecast') }}
