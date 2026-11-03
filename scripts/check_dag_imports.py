"""Fail if any DAG in /opt/airflow/dags can't be imported. Run inside the Airflow image."""

from airflow.dag_processing.dagbag import DagBag

EXPECTED_DAGS = {"extract_weather"}

bag = DagBag(dag_folder="/opt/airflow/dags")

if bag.import_errors:
    for path, error in bag.import_errors.items():
        print(f"Import error in {path}:\n{error}")
    raise SystemExit(1)

missing = EXPECTED_DAGS - set(bag.dag_ids)
if missing:
    print(f"Expected DAGs not found: {sorted(missing)}")
    raise SystemExit(1)

print(f"DAGs loaded: {sorted(bag.dag_ids)}")
