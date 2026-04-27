
  create view "weather_pipeline"."analytics"."cities__dbt_tmp"
    
    
  as (
    select distinct city_name
FROM "weather_pipeline"."analytics"."stg_weather_forecast"
  );