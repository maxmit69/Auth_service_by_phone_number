#!/bin/bash

# Путь к вашему проекту
PROJECT_DIR="/home/sergei/PycharmProjects/Auth_service_by_phone_number"

# Лог-файл
#LOG_FILE="$PROJECT_DIR/cron_job.log"

# Полный путь к Poetry
POETRY_PATH="/home/sergei/.local/bin/poetry"

# Функция для логирования сообщений
#log_message() {
#    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" >> "$LOG_FILE"
#}

# Логируем начало выполнения скрипта
#log_message "Запуск скрипта cron job"

# Перейти в директорию проекта
cd $PROJECT_DIR || { log_message "Не удалось перейти в директорию $PROJECT_DIR"; exit 1; }

# Получить путь к виртуальной среде Poetry
POETRY_ENV_PATH=$($POETRY_PATH env info --path)

# Проверка, что путь к виртуальной среде не пустой
#if [ -z "$POETRY_ENV_PATH" ]; then
#    log_message "Не удалось получить путь к виртуальной среде Poetry"
#    exit 1
#fi

# Активировать виртуальную среду Poetry
source "$POETRY_ENV_PATH/bin/activate" || { log_message "Не удалось активировать виртуальную среду Poetry"; exit 1; }

# Логируем запуск cron jobs
#log_message "Запуск cron jobs"

# Запустить cron jobs
$POETRY_PATH run python manage.py runcrons || { log_message "Ошибка при запуске cron jobs"; exit 1; }

# Логируем успешное завершение
#log_message "Скрипт cron job выполнен успешно"

# Деактивировать виртуальную среду
deactivate || { log_message "Не удалось деактивировать виртуальную среду"; exit 1; }

