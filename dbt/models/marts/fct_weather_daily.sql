{{ config(materialized='table') }}

select
    local_dt::date                        as forecast_date,
    city_id,
    city_name,
    city_country,
    min(main_temp_min)                    as temp_min,
    max(main_temp_max)                    as temp_max,
    round(avg(main_temp)::numeric, 2)     as temp_avg,
    round(avg(main_feels_like)::numeric, 2) as feels_like_avg,
    round(avg(main_humidity)::numeric, 2) as humidity_avg,
    round(avg(wind_speed)::numeric, 2)    as wind_speed_avg,
    round(avg(clouds_all)::numeric, 2)    as clouds_avg,
    round(sum(coalesce(rain_3h, 0))::numeric, 2) as total_rain,
    round(sum(coalesce(snow_3h, 0))::numeric, 2) as total_snow,
    count(*)                              as forecast_periods
from {{ ref('fct_weather_forecast') }}
group by local_dt::date, city_id, city_name, city_country
