# Navigator Auth

Сервис аутентификации и авторизации для платформы Navigator.

Отвечает за вход пользователей через внешний OIDC-провайдер и за управление правами доступа: роли, разрешения, области видимости (scopes), объекты, действия, назначения и точечные гранты. Другие сервисы платформы обращаются сюда, чтобы проверить, можно ли конкретному пользователю выполнить конкретное действие над конкретным объектом.

## Возможности

- Вход/выход через OIDC (Authorization Code), сессии и токены в HttpOnly-cookie
- Пользователи, роли, разрешения (permission = объект + действие)
- Области видимости (scope) и типы областей — иерархическое разграничение доступа
- Назначения ролей (assignment) и индивидуальные гранты (grant)
- Проверка доступа через `/api/access` — как для конкретных прав, так и списком

## Стек

| | |
|---|---|
| Язык | Python 3.12 |
| Фреймворк | FastAPI + Uvicorn |
| БД | PostgreSQL, SQLAlchemy 2.0 (async, asyncpg) |
| Миграции | Alembic |
| Аутентификация | Authlib (OIDC), PyJWT |
| Конфигурация | pydantic-settings |
| Инфраструктура | Docker Compose |

## Структура

```
app/
  src/
    app.py           # сборка FastAPI-приложения, роутеры, middleware
    setting.py       # настройки из .env
    authentication/  # OIDC-логин, сессии, cookie
    user/ role/ permission/ object/ action/
    scope/           # области и типы областей
    assignment/      # назначение ролей пользователям
    grant/           # точечные выдачи прав
    access/          # проверка доступа
    database/        # engine, сессии, базовые модели
  migrations/        # Alembic
```

Каждый модуль устроен одинаково: `router.py` → `service.py` → `models.py` / `schema.py`, зависимости в `deps.py`, ошибки в `exceptions.py`.

## Запуск

Требуется Docker и Docker Compose.

1. Создайте `.env` на основе примера:

```bash
cp .env.example .env
```

2. Заполните переменные:

| Переменная | Описание |
|---|---|
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | подключение к PostgreSQL (`DB_HOST=db` при запуске в Compose) |
| `BACKEND_PORT` | внешний порт API |
| `ALLOWED_ORIGINS` | CORS, список origin через запятую |
| `OIDC_ISSUER`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET` | параметры OIDC-провайдера |
| `OIDC_REDIRECT_URL`, `OIDC_POST_LOGOUT_REDIRECT_URL` | callback-адреса |
| `BASE_DOMAIN`, `COOKIE_DOMAIN` | домен сервиса и домен cookie |
| `APPS` | список приложений платформы через запятую |
| `SESSION_SECRET` | секрет для подписи сессии |
| `MODE` | `dev` — cookie без `https_only` |

3. Поднимите сервисы и накатите миграции:

```bash
make start
```

API будет доступно на `http://localhost:${BACKEND_PORT}/api`, Swagger — на `/api/docs`.

## Команды Makefile

| Команда | Что делает |
|---|---|
| `make start` | собрать и запустить backend + db, применить миграции |
| `make rebuild` | пересоздать всё с нуля (`down -v`), включая данные БД |
| `make down` | остановить сервисы |
| `make update-api` | перезапустить backend |
| `make update-db` | `alembic upgrade head` |
| `make new-migr name="..."` | создать миграцию с автогенерацией |
| `make back-migr` | откатить одну миграцию |
| `make see-migr` | текущая версия схемы |
| `make see-db` | psql внутри контейнера |
| `make see-api time=10m` | логи backend |
| `make dump` | дамп БД в `dumps/` |

## Разработка

Код в `app/` смонтирован в контейнер как volume, поэтому изменения подхватываются перезапуском:

```bash
make update-api
```

После изменения моделей:

```bash
make new-migr name="add_something"
make update-db
```
