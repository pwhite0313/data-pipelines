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
    clouds_all
    rain_3h,
    wind_speed,
    wind_gust,
    weather_main,
    weather_description,
    weather_id
FROM {{ ref('stg_weather__forecast') }}