#!/bin/bash

# Путь к виртуальному окружению
VENV_DIR="venv"
# Путь к исполняемому файлу
MAIN_SCRIPT="src/main.py"
# Имя файла PID
PID_FILE="bot.pid"

function install_dependencies() {
    echo "🔧 Установка зависимостей..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install python-telegram-bot
    echo "✅ Зависимости установлены."
}

function start_bot() {
    echo "🚀 Запуск бота..."
    if [ -f "$PID_FILE" ]; then
        echo "⚠️ Бот уже запущен (PID $(cat $PID_FILE))."
        exit 1
    fi

    source "$VENV_DIR/bin/activate"
    nohup python "$MAIN_SCRIPT" > bot.log 2>&1 &
    echo $! > "$PID_FILE"
    echo "✅ Бот запущен (PID $(cat $PID_FILE))."
}

function stop_bot() {
    echo "🛑 Остановка бота..."
    if [ ! -f "$PID_FILE" ]; then
        echo "⚠️ Бот не запущен или файл PID отсутствует."
        exit 1
    fi

    PID=$(cat "$PID_FILE")
    kill "$PID"
    rm "$PID_FILE"
    echo "✅ Бот остановлен (PID $PID)."
}

case "$1" in
    install)
        install_dependencies
        ;;
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    *)
        echo "Использование: $0 {install|start|stop}"
        exit 1
        ;;
esac