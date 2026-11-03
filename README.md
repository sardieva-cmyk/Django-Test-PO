# Django Blog

Минимальный Django-проект со списком статей, страницами деталей и счетчиком
просмотров. Каждый GET-запрос к странице статьи атомарно увеличивает
`views_count` на единицу.

Приложение `crud` содержит пример полного CRUD для задач: создание, просмотр,
редактирование и удаление. Список задач доступен по адресу
`http://127.0.0.1:8000/tasks/`.

## Запуск в Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Список статей доступен по адресу `http://127.0.0.1:8000/blogs/`, а также на
корневой странице сайта.

## Проверки

Запустите все тесты командой `python manage.py test`. Они проверяют страницы
блога и счетчик просмотров, а также CRUD-операции для задач. Чтобы записать все
обнаруженные Django тесты и их исходный код в Word-файл, выполните:

```powershell
python manage.py export_tests_to_docx --output Django_Tests.docx
```
