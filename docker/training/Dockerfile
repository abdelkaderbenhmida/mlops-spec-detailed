# GPU training image (local). Base on NVIDIA CUDA runtime so XGBoost/gpu_hist works.
FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    mlflow==2.7.1 \
    xgboost \
    scikit-learn==1.3.2 \
    pandas==2.1.4 \
    numpy==1.26.3 \
    pyyaml==6.0.1

COPY ml/ ./ml/

ENTRYPOINT ["python3", "ml/training/train.py"]