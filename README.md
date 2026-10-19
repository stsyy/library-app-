# Library API

Учебная программная система «Библиотека» для лабораторной работы №1 (CI/CD, Jenkins).

Двухзвенная клиент-серверная архитектура: REST API на **Flask** + база данных **SQLite** (через Flask-SQLAlchemy).

## Сущности и операции (25 CRUD)

| Ресурс | Create | Read (list) | Read (one) | Update | Delete |
|---|---|---|---|---|---|
| `/api/genres`  | POST | GET | GET `/<id>` | PUT `/<id>` | DELETE `/<id>` |
| `/api/authors` | POST | GET | GET `/<id>` | PUT `/<id>` | DELETE `/<id>` |
| `/api/books`   | POST | GET | GET `/<id>` | PUT `/<id>` | DELETE `/<id>` |
| `/api/readers` | POST | GET | GET `/<id>` | PUT `/<id>` | DELETE `/<id>` |
| `/api/loans`   | POST | GET | GET `/<id>` | PUT `/<id>` | DELETE `/<id>` |

## Запуск

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python run.py
```

## Тесты

```bash
.venv\Scripts\python -m pytest -v
```

## Ветки

- `main` — стабильная версия, сборка из неё разворачивается (CD)
- `dev` — интеграционная ветка (CI)
- `feature/*` — разработка новых функций (CI)
