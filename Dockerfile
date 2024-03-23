# Используйте официальный образ Python с вашей предпочтительной версией Python
FROM python:3.9
# Копируйте текущий каталог в рабочую директорию внутри контейнера
ADD . .
# Установите все необходимые пакеты, указанные в requirements.txt
RUN ADD . .pip3 install --no-cache-dir -r requirements.txt
# Запустите приложение при запуске контейнера
CMD ["python3", "./startproject.py"]
