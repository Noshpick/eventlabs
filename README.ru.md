# DeepSeek Agent Evaluation Lab

**[Read in English](README.md)**

Небольшая open-source платформа, которая проверяет, насколько эффективно DeepSeek решает задачи программирования, и ищет способы снизить стоимость **решённой задачи** без потери качества.

## Что измеряется

| Метрика | Источник                                                                                  |
|---|-------------------------------------------------------------------------------------------|
| % решённых задач (+ Wilson 95% CI) | pytest в изолированном Docker-контейнере                                                  |
| **Стоимость одной решённой задачи** | суммарные затраты / число решённых                                                        |
| p50 / p95 latency | wall time всего прогона                                                                   |
| Токены, повторные попытки, ошибки инструментов | usage из API + трассировки сообщений                                                      |
| Эффективность context cache | `prompt_cache_hit_tokens` / `prompt_cache_miss_tokens` из API - измерено, не предположено |

## Что сравнивается

- `layout: naive` против `layout: static_first` - весь неизменяемый контент (инструкции, условие задачи) уходит в общий префикс сообщений, переменный фидбек только дописывается в конец → выше cache hit rate, дешевле повторные попытки.
- `agent: plain` против `agent: tools` - одиночная генерация кода против агента с инструментами `run_tests` / `submit`.
- Модель, температура, число попыток - обычные поля конфига.

## Быстрый старт

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # вписать DEEPSEEK_API_KEY
docker build -t eval-lab-sandbox -f Dockerfile.sandbox .

python3 scripts/run_benchmark.py --config configs/example.yaml

uvicorn web.app:app --port 8000   # dashboard
```

Одна команда запускает весь бенчмарк и складывает воспроизводимый отчёт (markdown + графики + разбор неудач) в `reports/experiment-N/`. Автономный smoke-тест без API-ключа и Docker: `python scripts/smoke_test.py`.

## Структура проекта

```
eval_lab/
  config.py            конфиг эксперимента + прайсинг
  deepseek_client.py   OpenAI-совместимый клиент, учёт cache-токенов, ретраи
  agents/              plain-агент (код + фидбек) и tools-агент (function calling)
  sandbox.py           docker run: без сети, 512 МБ RAM, 1 CPU, read-only root FS
  grader.py            pytest-прогон; решено = весь набор тестов зелёный
  metrics.py           $/решённая задача, p50/p95, cache hit rate, Wilson CI
  runner.py            configs × tasks × repeats → SQLite
  report.py            воспроизводимый отчёт с графиками
web/app.py             FastAPI: эксперименты, сравнение конфигураций, трассировки
tasks/                 формат задачи: task.yaml + statement.md + tests/
configs/               конфигурации экспериментов
scripts/               run_benchmark.py, smoke_test.py
```

## Добавление задачи

```
tasks/<id>/task.yaml      id, entry_file
tasks/<id>/statement.md   условие (уходит модели)
tasks/<id>/tests/         pytest-тесты (модели не видны)
```

В репозитории 33 задачи (массивы, строки, DP, графы, проектирование структур данных). Каждая покрыта эталонным решением - `python scripts/validate_tasks.py` прогоняет все наборы тестов против них, это контроль качества при добавлении новых задач.

## Честные оговорки

- На 20–30 задачах solve rate шумный: сравнивайте конфигурации с учётом доверительных интервалов и используйте `repeats >= 3`.
- Цены в `configs/example.yaml` - заглушки: перед публикацией цифр проверьте актуальный прайсинг DeepSeek (https://api-docs.deepseek.com/quick_start/pricing).
- Sandbox защищает от случайного вреда, а не от целенаправленного побега.
