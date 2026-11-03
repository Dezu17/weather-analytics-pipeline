ARG AIRFLOW_VERSION=3.3.2
FROM apache/airflow:${AIRFLOW_VERSION}-python3.12

ARG AIRFLOW_VERSION
WORKDIR /opt/airflow/project

COPY --chown=airflow:0 pyproject.toml ./
COPY --chown=airflow:0 src ./src

# Editable install: the src folder is also mounted at runtime, so code changes apply without a rebuild.
# Pinning apache-airflow stops pip from upgrading Airflow's own dependencies.
# --no-build-isolation reuses the image's setuptools instead of downloading a fresh copy.
RUN pip install --no-cache-dir --no-build-isolation "apache-airflow==${AIRFLOW_VERSION}" -e .

WORKDIR /opt/airflow
