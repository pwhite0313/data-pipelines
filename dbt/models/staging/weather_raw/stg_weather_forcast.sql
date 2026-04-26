select *
FROM {{ source('raw', 'weather_forecast') }}
