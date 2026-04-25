import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import os

df = pd.read_csv("data/raw/output_20260320_015412.csv")


db_url = os.getenv("POSTGRES_DBT_URL") or os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("Missing POSTGRES_DBT_URL or DATABASE_URL environment variable")

engine = create_engine(db_url)

db_cols = pd.read_sql(
    text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'raw'
          AND table_name = 'weather_forecast'
        ORDER BY ordinal_position
    """),
    engine
)["column_name"].tolist()

df_cols = df.columns.tolist()

print("In CSV/DataFrame but missing from DB:")
print(sorted(set(df_cols) - set(db_cols)))

print("In DB but missing from CSV/DataFrame:")
print(sorted(set(db_cols) - set(df_cols)))