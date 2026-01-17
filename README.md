Установка и настройка PosgreSQL на Linux:

Обновляем пакеты
# sudo apt update

Устанавливаем PostgreSQL
# sudo apt install postgresql postgresql-contrib

Устанавливаем клиентские библиотеки для Python
# sudo apt install libpq-dev python3-dev

Устанавливаем psycopg2 для Django
# pip install psycopg2-binary

Проверяем статус PostgreSQL
# sudo systemctl status postgresql

Запускаем PostgreSQL (если не запущен)
# sudo systemctl start postgresql
# sudo systemctl enable postgresql


Переключаемся на пользователя postgres
# sudo -u postgres psql

В psql создаем базу данных и пользователя
# CREATE DATABASE pantheon_db;
# CREATE USER pantheon_user WITH PASSWORD 'your_secure_password_here';
# ALTER ROLE pantheon_user SET client_encoding TO 'utf8';
# ALTER ROLE pantheon_user SET default_transaction_isolation TO 'read committed';
# ALTER ROLE pantheon_user SET timezone TO 'UTC';
# GRANT ALL PRIVILEGES ON DATABASE pantheon_db TO pantheon_user;

Выходим из psql
# \q

Создание Django проекта на Linux

Установка Python3 и pip (если еще не установлены)
# sudo apt install python3 python3-pip python3-venv -y

Установка виртуального окружения (рекомендуется)
# pip3 install virtualenv

Создание папки для проекта
# mkdir mydjango_project
# cd mydjango_project

Создание виртуального окружения
# python3 -m venv venv

Активация виртуального окружения
# source venv/bin/activate
Теперь в терминале должно отображаться (venv)

Установка Django
# pip install django

Создание проекта
# django-admin startproject acme_project

Проверка структуры
# ls -la
Должны увидеть: manage.py, myproject/, venv/

Применение миграций
# python manage.py migrate

Создание суперпользователя (администратора)
# python manage.py createsuperuser

Запуск сервера
# python manage.py runserver

Теперь откройте браузер и перейдите по адресу:
# http://127.0.0.1:8000 - главная страница Django
# http://127.0.0.1:8000/admin - административная панель

Дальше в Django проекте добавляем / изменяем папки и файлы
