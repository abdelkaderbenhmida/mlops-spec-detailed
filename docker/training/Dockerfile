# Reproducible training image (VM11 / CI train stage).
# Pinned Python + libraries so a retrain is deterministic.
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    mlflow==2.7.1 \
    scikit-learn==1.3.2 \
    pandas==2.1.4 \
    numpy==1.26.3 \
    pyyaml==6.0.1

COPY ml/ ./ml/

ENTRYPOINT ["python", "ml/training/train.py"]
