FROM python:3.11-slim

WORKDIR /app

COPY persephone/controller /app/controller

RUN pip install --no-cache-dir fastapi uvicorn[standard] requests pydantic

EXPOSE 8000

CMD ["uvicorn", "controller.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
