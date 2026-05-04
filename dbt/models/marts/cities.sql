select distinct city_name
FROM {{ ref('stg_weather__forecast') }}
