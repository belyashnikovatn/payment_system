# Payment System

Сервис для платёжной системы, реализующий REST API для управления пользователями, аккаунтами, платежами и обработкой вебхуков.

---

## Стек технологий

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (с использованием [SQLAlchemy](https://www.sqlalchemy.org/))
- **Authentication**: JWT (JSON Web Tokens)
- **Environment Management**: [python-dotenv](https://pypi.org/project/python-dotenv/)
- **Containerization**: [Docker](https://www.docker.com/) и [docker-compose](https://docs.docker.com/compose/)

---

## Функционал

### Для пользователей:
- Аутентификация через email и пароль.
- Получение информации о себе (ID, email, полное имя).
- Просмотр списка своих аккаунтов и балансов.
- Просмотр списка своих платежей.  

### Для администраторов:
- Аутентификация через email и пароль.
- Получение информации о себе (ID, email, полное имя).
- Управление пользователями (создание, удаление, обновление).
- Просмотр списка пользователей и их аккаунтов с балансами.

### Обработка платежей:  
- Обработка вебхуков от сторонних платёжных систем.
- Проверка подписи вебхука.
- Создание счёта, если его нет.
- Создание транзакции и пополнение баланса пользователя.

---
## Развёртывание
### С использованием Docker Compose
1. Убедитесь, что у вас установлены Docker.
2. Создайте файл .env в корне проекта и заполните его (пример ниже).
3. Запустите приложение:
```bash
docker compose up --build
```
4. Приложение будет доступно по адресу: http://localhost:8000.

### Без Docker Compose
1. Убедитесь, что у вас установлен Python 3.9.
1. Убедитесь, что у вас установлен и запущен PostgreSQL, создайте базу и подключение со следующими настройками.

| Параметр       | Значение            |
|----------------|---------------------|
| Name           | fastapi_app         |
| Host name/address | 127.0.0.1         |
| Port           | 5432                |
| Username       | postgres            |
| Password       | (your_password)     |

2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Создайте файл .env в корне проекта и заполните его (пример ниже).
4. Запустите приложение:
```bash
python -m app.main
```
5. Приложение будет доступно по адресу: http://localhost:8000.

--- 
## Тестирование
### Локально
1. Установите зависимости для тестирования:  
```bash
pip install pytest pytest-asyncio
```

2. Запустите тесты: 
```bash 
python -m pytest tests/
```
### В Docker
```bash
docker compose exec app pytest tests
```

---

## Пример .env файла
```
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
# Строка подключения при запуске приложения в Docker
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/fastapi_app
# Строка подключения при запуске приложения локально
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/fastapi_app

```
---
## API Маршруты
Пользовательские маршруты:
- GET /users/me – Получить информацию о текущем пользователе.
- GET /users/me/accounts – Получить список аккаунтов текущего пользователя.
- GET /users/me/transactions – Получить список транзакций текущего пользователя.   

Администраторские маршруты:
- POST /admin/users – Создать нового пользователя.
- DELETE /admin/users/{user_id} – Удалить пользователя.
- PUT /admin/users/{user_id} – Обновить данные пользователя.  

Обработка вебхуков:
- POST /webhook/payment – Обработать входящий платёж.
---
## Разработчик
[Беляшникова Таня](https://github.com/belyashnikovatn)   
Требования - [ТЗ](https://docs.google.com/document/d/1-fvs0LaX2oWPjO6w6Bpglz1Ndy_KrNV7NeNgRlks94k/edit?tab=t.0)

---
## Заметки
- Убедитесь, что переменные окружения настроены корректно.
- Для продакшн-окружения используйте безопасные значения SECRET_KEY и DATABASE_URL.