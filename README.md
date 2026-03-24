# Магазин обуви

[![Maintainability](https://qlty.sh/gh/anananmd/projects/shoe_store_practice_1/maintainability.svg)](https://qlty.sh/gh/anananmd/projects/shoe_store_practice_1)

Десктопное приложение для управления магазином обуви с поддержкой ролей пользователей, корзины, заказов и импорта данных из Excel.

## Возможности

- Авторизация пользователей (admin, manager, client, guest)
- Просмотр товаров
- Поиск, фильтрация и сортировка товаров
- Корзина для клиента и гостя
- Оформление заказа
- Просмотр заказов
- Просмотр состава заказа
- Добавление, редактирование и удаление товаров (по ролям)
- Импорт данных из Excel
- Отображение изображений товаров

## Роли пользователей

- admin — полный доступ
- manager — управление заказами
- client — покупка товаров
- guest — просмотр и покупка без регистрации

## Запуск проекта

Создать виртуальное окружение:

python -m venv .venv

Активировать:

Mac / Linux:
source .venv/bin/activate

Установить зависимости:

pip install -r requirements.txt

Запустить приложение:

python main.py

## Импорт данных

Файлы для импорта должны находиться в папке:

import_data/

Поддерживаемые файлы:
- Tovar.xlsx
- user_import.xlsx
- Заказ_import.xlsx
- Пункты выдачи_import.xlsx

Запуск импорта:

python -m app.import_excel

## Проверка кода

python -m flake8 .

## Стек технологий

- Python 3.10
- PySide6
- SQLite
- pandas
- openpyxl
