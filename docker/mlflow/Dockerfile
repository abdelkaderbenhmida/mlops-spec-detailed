# MLflow tracking server image (VM06) with the Postgres backend store driver.
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MLFLOW_HOME=/opt/mlflow

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    mlflow==2.7.1 \
    psycopg2-binary \
    boto3

WORKDIR /opt/mlflow

# Artifact store lives on VM06 disk.
VOLUME ["/opt/mlflow/artifacts"]

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://localhost:5000/health || exit 1

ENTRYPOINT ["mlflow", "server"]
CMD ["--host", "0.0.0.0", "--port", "5000"]
