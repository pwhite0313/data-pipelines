{{ config(materialized='incremental', unique_key=['city_id', 'local_dt']) }}

select
    local_dt,
    city_country,
    city_name,
    city_id,
    main_temp,
    main_temp_min,
    main_temp_max,
    main_feels_like,
    main_humidity,
    clouds_all,
    rain_3h,
    snow_3h,
    wind_speed,
    wind_gust,
    weather_main,
    weather_description,
    weather_id
from {{ ref('stg_weather__forecast') }}

{% if is_incremental() %}
    where not exists (
        select 1 from {{ this }} t
        where t.city_id = city_id
          and t.local_dt = local_dt
    )
{% endif %}
