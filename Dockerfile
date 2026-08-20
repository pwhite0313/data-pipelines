FROM apache/airflow:2.8.1-python3.11

USER airflow

# Installed separately from requirements-airflow.txt, and version-pinned,
# on purpose. Two reasons:
# 1. Left unpinned, pip resolves the LATEST apache-airflow-providers-postgres
#    release, which targets Airflow 3.x's FastAPI-based stack (pulls in
#    fastapi/uvicorn/starlette/psycopg3, none of which belong here) — a
#    silent, version-drift-driven incompatibility with our Airflow 2.8.1,
#    not something that showed up until a fresh (uncached) build finally
#    re-resolved it against however new the package index had gotten.
# 2. Combining it into the same pip invocation as the pinned dbt packages
#    below forces pip to re-resolve the entire Airflow dependency tree
#    against those pins simultaneously, sending the resolver into a
#    multi-hour backtracking search instead of a clean install.
# 5.10.0 is the version apache-airflow==2.8.1's own official constraints
# file (constraints-2.8.1/constraints-3.11.txt) resolves it to.
RUN pip install --no-cache-dir apache-airflow-providers-postgres==5.10.0

COPY requirements-airflow.txt .
RUN pip install --no-cache-dir -r requirements-airflow.txt