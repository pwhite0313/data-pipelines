{{ config(materialized='view', schema='reports') }}

with latest_per_city as (
    select
        city_id,
        max(local_dt) as latest_dt
    from {{ ref('int_weather_enriched') }}
    group by city_id
)

select
    e.local_dt,
    e.city_id,
    e.city_name,
    e.city_country,
    e.main_temp,
    e.main_feels_like,
    e.main_humidity,
    e.wind_speed,
    e.wind_gust,
    e.clouds_all,
    e.rain_3h,
    e.snow_3h,
    e.weather_main,
    e.weather_description,
    e.pop,
    e.temp_category,
    e.wind_category,
    e.precip_type
from {{ ref('int_weather_enriched') }} e
inner join latest_per_city l
    on e.city_id = l.city_id
    and e.local_dt = l.latest_dt
