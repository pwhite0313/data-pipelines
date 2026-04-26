
  create view "weather_pipeline"."analytics"."stg_weather_forcast__dbt_tmp"
    
    
  as (
    select *
FROM "weather_pipeline"."raw"."weather_forecast"
  );