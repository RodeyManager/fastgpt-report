FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src/ src/
COPY app.py ./

RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

EXPOSE 7860

CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
