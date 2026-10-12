FROM apache/airflow:3.3.0-python3.11

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_DEFAULT_TIMEOUT=600

RUN pip install --no-cache-dir \
    httpx \
    joblib \
    numpy \
    pandas \
    pydantic \
    python-dotenv \
    PyYAML \
    scikit-learn