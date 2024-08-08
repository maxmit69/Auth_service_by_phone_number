# Auth Service by Phone Number

Этот проект предоставляет сервис аутентификации по номеру телефона. В проекте используется Django, Django REST Framework
и Postgres в качестве базы данных. Для управления зависимостями используется Poetry, а для контейнеризации - Docker.

## Основные возможности

- Регистрация пользователя по номеру телефона
- Верификация кода подтверждения
- Активация инвайт-кода в профиле пользователя

## Требования

- [Python3.12](https://www.python.org/downloads/release/python-3120/)
- [Django](https://docs.djangoproject.com/en/stable/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Docker](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Poetry](https://python-poetry.org/docs/)

## Установка

### С использованием Poetry

1. Клонируйте репозиторий:

   ```Bash
    git clone https://github.com/maxmit69/Auth_service_by_phone_number.git
    cd Auth_service_by_phone_number

2. Установите Poetry:

    ```Bash
    pip install poetry

3. Установите зависимости:

    ```Bash
    poetry install
   
4. Создайте файл .env в корне проекта и добавьте необходимые переменные окружения. Пример:

    ```sh
    SECRET_KEY=your_secret_key
    DEBUG=True
    DATABASE_URL=postgres://user:password@localhost:5432/yourdatabase
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   

### С использованием Docker

1. Клонируйте репозиторий:

    ```hs
   git clone https://github.com/maxmit69/Auth_service_by_phone_number.git
    cd Auth_service_by_phone_number

2. Постройте и запустите контейнеры:

    ```hs
   docker-compose up --build
   
3. Остановить все сервисы с помощью команды:

    ```sh
   docker-compose down

## Запуск

### С использованием Poetry

1. Примените миграции:

   ```sh
   poetry run python manage.py migrate

2. Запустите сервер разработки:

   ```sh
   poetry run python manage.py runserver

### С использованием Docker

Контейнеры будут автоматически применять миграции и запускать сервер при выполнении команды docker-compose up --build.

## Тестирование

### С использованием Poetry

1. Запустите тесты:

   ```sh
   poetry run python manage.py test
   
### Для получения покрытия тестами используйте coverage:

1. Установите coverage:

    ```sh
   poetry add --dev coverage

2. Запустите тесты с покрытием:

    ```sh
   poetry run coverage run --source='.' manage.py test

3. Сгенерируйте отчет:

    ```sh
   poetry run coverage html

4. Откройте отчет:

    ```sh
   open htmlcov/index.html

### С использованием Docker

1. Выполните тесты в контейнере:

   ```sh
   docker-compose exec web python manage.py test

## API Эндпоинты

### Регистрация

- URL: /api/register/
- Метод: POST
- Тело запроса:

   ```json
  {
    "phone_number": "+1234567890"
  }

- Ответ:

   ```json
  {
    "message": "Код подтверждения отправлен"
  }

### Подтверждение кода

- URL: /api/verify/
- Метод: POST
- Тело запроса:

   ```json
  {
    "phone_number": "+1234567890",
    "code": "1234"
  }

- Ответ:

    Происходит имитация отправки SMS с кодом подтверждения ответа в консоль!!!

   ```json
  {
    "message": "Пользователь активирован"
  }
  
### Профиль пользователя

- URL: /api/profile/<uuid:id>/
- Метод: GET
- Ответ:

   ```json
  {
    "id": "user-uuid",
    "phone_number": "+1234567890",
    "invite_code": "invite-code",
    "referred_by": "referred-user",
    "referred_users": ["+0987654321"],
    "used_invite_code": "used-invite-code"
   }

### Активация инвайт-кода

- URL: /api/profile/<uuid:id>/
- Метод: PATCH
- Тело запроса:

   ```json
   {
     "used_invite_code": "string"
   }
  
- Ответ:

    ```json
   {
     "id": "user-uuid",
     "phone_number": "+1234567890",
     "invite_code": "invite-code",
     "referred_by": "referred-user",
     "referred_users": ["+0987654321"],
     "used_invite_code": "used-invite-code"
   }

## Реализовать интерфейс на Django Templates для базового тестирования функционала

### Регистрация

- URL: /register/

### Подтверждение кода

- URL: /verify/

### Активация инвайт-кода

- URL: /profile/<uuid:id>/

## Лицензия
Этот проект лицензирован под лицензией MIT. См. файл LICENSE для подробностей.
