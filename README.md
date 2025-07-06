# 🗣️ AltMur

**AltMur** — это альтернативая чат-платформа с акцентом на **групповые комнаты**, **общение в реальном времени** через WebSocket и **встроенную систему модерации**. Проект построен на FastAPI как учебно-боевой backend, который легко расширять и использовать для прокачки реальных навыков разработки.

---

## 🚀 Функции

- 📦 Регистрация и авторизация (JWT)
- 💬 Комнаты (публичные и приватные)
- 🧵 WebSocket-чаты с сохранением истории
- 🛡️ Роли: `user`, `moderator`, `admin`
- 🧹 Модерация: удаление сообщений, баны
- 🧠 Асинхронная архитектура + Redis pub/sub
- 🧪 Тесты, Alembic миграции, Docker, CI/CD

---

## 🛠️ Стек технологий

- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Redis](https://redis.io/)
- [WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [Docker](https://www.docker.com/)
- [Pytest](https://docs.pytest.org/)
- [GitHub Actions](https://github.com/features/actions)

---

## 📂 Структура проекта

```
murmur/
├── src/
│   ├── routers/         # Все FastAPI роуты
│   ├── models/          # SQLAlchemy модели
│   ├── schemas/         # Pydantic-схемы (DTO)
│   ├── services/        # Бизнес-логика (на уровне use-case)
│   ├── repositories/    # Работа с базой (SQLAlchemy запросы)
│   ├── utils/           # Хелперы (например, security, WebSocket-менеджер)
│   ├── test/            # Тесты
│   └── main.py          # Точка входа (FastAPI app + include_routers)
├── alembic/             # Миграции
├── alembic.ini
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── README.md
└── pyproject.toml

````

---

## 🧑‍💻 Как запустить

> Требуется: Docker, Docker Compose

```bash
git clone https://github.com/yourname/murmur-backend.git
cd murmur-backend

cp .env.example .env
# отредактируй .env при необходимости

docker-compose up --build
````

После запуска:

* API: `http://localhost:8000`
* Swagger UI: `http://localhost:8000/docs`

---

## 🧪 Тесты

```bash
docker-compose exec api pytest
```

---

## 💡 TODO / Планы

* [ ] Личные чаты
* [ ] Уведомления
* [ ] Интеграция с Telegram
* [ ] Панель администратора
* [ ] Фронтенд (React/Svelte)

---

## ⚖️ Лицензия

MIT License © \ Khudoberdi