select distinct city_name
FROM {{ ref('weather_source_prep') }}
