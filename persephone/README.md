# Persephone Platform MVP

Первая минимально жизнеспособная версия бэкенда Persephone. Контроллер написан на FastAPI, агент запускается внутри GPU-пода и собирает метрики.

## Структура проекта

```
persephone/
  controller/
    app/
      api/              # FastAPI роутеры
      core/             # конфигурация, аутентификация
      providers/        # интеграции с RunPod
      services/         # бизнес-логика запусков
      storage/          # in-memory хранилище
      main.py           # точка входа FastAPI
  agent/
    agent.py            # entrypoint агента
    gpu_metrics.py      # съём GPU метрик через NVML
    runner.py           # mock-инференс и расчёт метрик
  docker/
    controller.Dockerfile
    agent.Dockerfile
  docker-compose.yml
```

## Конфигурация окружения

Контроллер управляется переменными окружения:

```
PERSEPHONE_API_KEY=dev-secret
PERSEPHONE_CATALOG_MODE=mock   # или runpod
RUNPOD_API_KEY=...             # для режима runpod
PERSEPHONE_IMAGE_AGENT=registry/persephone-agent:0.1
PERSEPHONE_REQUEST_TIMEOUT_S=900
```

## Локальный запуск контроллера

```bash
cd persephone
uvicorn controller.app.main:app --host 0.0.0.0 --port 8000
```

Или через Docker Compose:

```bash
cd persephone
docker compose up --build
```

## Тестовый сценарий

1. Запустить контроллер.
2. Запросить каталог: `curl -H "X-API-Key: dev-secret" http://localhost:8000/compute/gpus`.
3. Стартовать прогон: `curl -X POST -H "Content-Type: application/json" -H "X-API-Key: dev-secret" \
   -d '{"gpu_type":"l4-24gb","model_ref":"mock-v0","samples":8}' \
   http://localhost:8000/runs/start`.
4. Получить статус: `curl -H "X-API-Key: dev-secret" http://localhost:8000/runs/<run_id>`.
5. В случае ошибки RunPod контроллер вернёт статус `failed` и сообщение в `error_message`.

## Агент

Агент читает переменные окружения `MODEL_REF` и `SAMPLES`, собирает GPU метрики с частотой 0.5–1 Гц, выполняет mock-инференс и сохраняет результаты в `/workspace/result.json` и `/workspace/gpu_timeseries.csv`.

## Docker

- `docker/controller.Dockerfile` — образ контроллера на базе `python:3.11-slim`.
- `docker/agent.Dockerfile` — образ агента на базе `nvidia/cuda:12.2.2-runtime-ubuntu22.04`.

Оба образа можно собрать командой `docker build` из корня репозитория.
