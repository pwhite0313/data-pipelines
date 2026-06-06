{{ config(materialized='table') }}

with ranked as (
    select
        city_id,
        city_name,
        city_country,
        city_population,
        city_timezone,
        city_coord_lat,
        city_coord_lon,
        row_number() over (partition by city_id order by dt_utc desc) as row_num
    from {{ ref('stg_weather__forecast') }}
)

select
    city_id,
    city_name,
    city_country,
    city_population,
    city_timezone,
    city_coord_lat,
    city_coord_lon
from ranked
where row_num = 1
