SCHEDULER = docker compose exec airflow-scheduler
DBT = $(SCHEDULER) bash -c "cd /opt/airflow/dbt && dbt

.PHONY: up down restart logs trigger backfill dbt-run dbt-test dbt-fresh psql

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down && docker compose up -d

logs:
	docker compose logs -f airflow-scheduler

trigger:
	$(SCHEDULER) airflow dags trigger weather_forecast_pipeline

backfill:
	$(SCHEDULER) python -m src.postgres_loader all

dbt-run:
	$(DBT) run --profiles-dir /opt/airflow/dbt"

dbt-test:
	$(DBT) test --profiles-dir /opt/airflow/dbt"

dbt-fresh:
	$(DBT) source freshness --profiles-dir /opt/airflow/dbt"

psql:
	docker compose exec postgres-warehouse psql -U weather_user -d weather_db
