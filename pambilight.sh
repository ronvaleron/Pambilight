#!/bin/bash
cd /home/ron/Pambilight
# Проверка на запущенное приложение
ps -ef | grep "python pambilight.py" | grep -v "grep" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  # Приложение запущено, останавливаем
  echo "Остановка приложения..."
  pkill -f "pambilight.py"
else
  # Приложение не запущено, запускаем
  echo "Запуск приложения..."
  source ./venv/bin/activate
  python pambilight.py &
fi
