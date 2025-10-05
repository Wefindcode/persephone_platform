# Требования к бэкенду для Persephone UI

## Общие условия
- Бэкенд обслуживает HTTP API по базовому URL, задаваемому переменной окружения `NEXT_PUBLIC_API_BASE` (по умолчанию `http://localhost:8000`).
- Все запросы выполняются с включёнными cookie/credentials, поэтому сервер должен поддерживать сессии и CORS (если UI и API на разных хостах) с `credentials: include`.
- Ответы об ошибках возвращаются с соответствующим HTTP статусом и JSON телом вида `{ "message": string }`, которое отображается в интерфейсе.
- Тайпскрипт-клиент ожидает JSON для всех успешных ответов, кроме загрузки файла (см. ниже).

## Загрузка артефакта
`POST /upload`
- Принимает multipart/form-data с полем `file` (zip/tar/onnx/pt/pkl, до 500 МБ).
- Возвращает `{ "runId": string }` — идентификатор пайплайна, сохраняемый в localStorage.

## Подготовка окружения
`POST /prepare/start?runId=...&gpuId=...`
- Параметр `runId` обязателен. `gpuId` передаётся, если пользователь выбрал конкретный GPU.
- Возвращает текущее состояние подготовки (`PrepareStatusResponse`).

`GET /prepare/status?runId=...`
- Возвращает `PrepareStatusResponse` для периодического поллинга.

`GET /prepare/gpus?runId=...`
- Возвращает массив доступных GPU (`GpuOption[]`). Если массив пуст — свободных GPU нет.

Структура `PrepareStatusResponse`:
```json
{
  "runId": "string",
  "phase": "Pending" | "Running" | "Succeeded" | "Failed",
  "steps": [
    {
      "name": "string",
      "status": "Pending" | "Running" | "Succeeded" | "Failed",
      "message": "string?",
      "completedAt": "ISO8601?"
    }
  ],
  "updatedAt": "ISO8601?"
}
```

Структура `GpuOption`:
```json
{
  "id": "string",
  "name": "string",
  "memoryGb": number?,
  "provider": "string?",
  "region": "string?"
}
```

## Деплой
`POST /deploy/start?runId=...&env=dev|stage|prod`
- Запускает деплой в указанное окружение.
- Возвращает `DeployStatusResponse`.

`GET /deploy/status?runId=...&env=...`
- Возвращает текущее состояние деплоя для выбранного окружения.

Структура `DeployStatusResponse`:
```json
{
  "runId": "string",
  "environment": "dev" | "stage" | "prod" | string,
  "phase": "Pending" | "Running" | "Succeeded" | "Failed",
  "message": "string?",
  "version": "string?",
  "startedAt": "ISO8601?",
  "updatedAt": "ISO8601?"
}
```

## Мониторинг
`GET /monitor/summary?runId=...`
- Возвращает мониторинговые метрики запуска (`MonitorSummaryResponse`).
- UI опрашивает endpoint каждые 5 секунд.

Структура `MonitorSummaryResponse`:
```json
{
  "runId": "string",
  "red": {
    "rps": number,
    "errorsPercent": number,
    "p95DurationMs": number
  },
  "slo": {
    "availability": number,
    "latencyP95Ms": number
  },
  "updatedAt": "ISO8601?"
}
```

## UX ожидания
- Для любого запроса отсутствие `runId` должно приводить к ошибке с объяснением.
- Статусы должны обновляться без долгих задержек: подготовка поллится каждые 2 сек, мониторинг — каждые 5 сек.
- Если GPU недоступны, `GET /prepare/gpus` должен возвращать пустой массив, чтобы UI показал сообщение о нехватке ресурсов.
