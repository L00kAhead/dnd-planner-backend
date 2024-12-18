# Планировщик Вечеринок для Dungeons & Dragons

## Описание

Планировщик вечеринок для Dungeons & Dragons — это веб-приложение, разработанное для помощи игрокам в организации их игровых сессий. Оно позволяет пользователям создавать вечеринки, отправлять приглашения, управлять участниками и получать напоминания о предстоящих событиях.

## Особенности

- Регистрация пользователей и аутентификация
- Операции CRUD для вечеринок
- Приглашение пользователей на вечеринки по электронной почте
- Ответы на приглашения на вечеринки
- Уведомление создателей вечеринок о ответах на приглашения
- Запланированные напоминания о предстоящих вечеринках
- Управление профилем пользователя

## Технологический стек

- **Бэкенд**: FastAPI
- **База данных**: SQLite (с использованием SQLAlchemy)
- **Сервис электронной почты**: Gmail SMTP
- **Контейнеризация**: Docker

## Необходимые компоненты

- **Docker**: убедитесь, что Docker установлен на вашем компьютере. Загрузить Docker
- **Python 3.10+**: требуется, если запускать приложение без Docker.


## Установка

1. **Клонируйте репозиторий:**:
   ```bash
   git clone https://github.com/L00kAhead/dnd-planner-backend
   cd dnd-planner-backend
   ```

2. **Чтобы запустить приложение с помощью Docker**:
   ```bash
   docker-compose up
   docker-compose up -d # deattached mode
   ```
   - **Установите зависимости (если не используете Docker)**:
       ```bash
       python3 -m venv venv
       source /venv/bin/activate
       pip install -r requirements.txt
       uvicorn app.main:app --reload
       ```

## Доступ к API Swagger Docs:
  ```bash
  http://localhost:8000/docs
  ```

## Таблица конечных точек
| Конечная точка | Метод | Описание |
| --- | --- | --- |
| `/` | GET | Корень |
| `/admin/users` | GET | Список пользователей |
| `/admin/users/{user_id}` | DELETE | Удалить пользователя |
| `/auth/signup` | POST | Регистрация |
| `/auth/login` | POST | Вход |
| `/user/me` | GET | Получить текущего пользователя |
| `/user/me` | PUT | Обновить пользователя |
| `/user/me` | DELETE | Удалить учетную запись пользователя |
| `/user/{user_id}` | GET | Получить пользователя по идентификатору |
| `/user/me/invites` | GET | Список приглашений пользователя |
| `/parties/` | GET | Список вечеринок |
| `/parties/` | POST | Создать вечеринку |
| `/parties/{party_id}/respond-invite` | PUT | Ответить на приглашение |
| `/parties/{party_id}` | PUT | Обновить вечеринку |
| `/parties/{party_id}` | DELETE | Удалить вечеринку |
| `/parties/{party_id}/join-request` | POST | Запрос на вступление |
| `/parties/{party_id}/attendees/{user_id}` | DELETE | Удалить участника |
