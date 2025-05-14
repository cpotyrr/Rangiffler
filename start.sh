#!/bin/bash

# Функция для проверки и создания виртуального окружения
setup_venv() {
    if [ ! -d ".rangiffler" ]; then
        echo "Creating Python virtual environment..."
        # Проверяем наличие Python
        if [ "$(uname -s)" == "Darwin" ]; then
            which python3 || brew install python3
        else
            which python3 || sudo apt-get install python3
        fi

        python3 -m venv .rangiffler
        source .rangiffler/bin/activate
        pip install -r requirements.txt
    else
        echo "Virtual environment already exists, activating..."
        source .rangiffler/bin/activate
    fi
}

# Функция для проверки и создания Docker контейнера
setup_docker() {
    # Проверяем наличие Docker
    which docker || {
        echo "Docker is not installed."
        exit 1
    }

    # Проверяем существует ли контейнер
    if [ ! "$(docker ps -a | grep auth_db)" ]; then
        echo "Creating and starting auth_db container..."
        docker build -t auth_db .
        docker run -d --name auth_db -p 5432:5432 auth_db
    else
        # Проверяем запущен ли контейнер
        if [ ! "$(docker ps | grep auth_db)" ]; then
            echo "Starting existing auth_db container..."
            docker start auth_db
        else
            echo "Container auth_db is already running"
        fi
    fi
}

# Функция для запуска фронтенда
start_frontend() {
    echo "Starting frontend..."
    cd gql-client/ || exit
    npm i
    npm run dev &
    cd - || exit
}

# Функция для запуска бэкенд сервисов
start_backend() {
    echo "Starting backend services..."
    uvicorn gateway.main:app --port 8000 --reload &
    uvicorn auth.main:app --port 9000 --reload &
}

# Функция для вывода информации о запущенных процессах
show_info() {
    echo "
Services started:
- Frontend: http://127.0.0.1:3001
- Gateway: http://127.0.0.1:8000
- Auth Service: http://127.0.0.1:9000
- Database: localhost:5432

To stop all services:
1. Press Ctrl+C in this terminal
2. Run: docker stop auth_db (if you want to stop the database)

To see logs:
- Frontend: tail -f gql-client/npm-debug.log
- Gateway: tail -f gateway.log
- Auth: tail -f auth.log
"
}

# Основной скрипт
echo "Starting Rangiffler services..."

# Настройка логирования
exec 1> >(tee -a rangiffler.log)
exec 2>&1

# Запуск всех компонентов
setup_venv
setup_docker
start_frontend
start_backend

# Показываем информацию
show_info

# Ждем сигнал завершения
echo "Press Ctrl+C to stop all services..."
trap 'cleanup' INT
cleanup() {
    echo "Stopping all services..."
    pkill -f "uvicorn"
    pkill -f "npm run dev"
    exit 0
}
wait
