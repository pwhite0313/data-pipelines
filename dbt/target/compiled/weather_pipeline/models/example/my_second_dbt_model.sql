-- Use the `ref` function to select from other models

select *
from "weather_pipeline"."analytics"."my_first_dbt_model"
where id = 1