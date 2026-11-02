import importlib
import inspect
import unittest

from docx import Document
from docx.shared import Pt
from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Экспортирует тесты проекта в файл Word (.docx)"

    def add_arguments(self, parser):
        parser.add_argument("--output", type=str, default="Django_Tests.docx")

    def handle(self, *args, **options):
        output_file = options["output"]
        document = Document()
        document.add_heading("Документация тестов Django", level=0)

        for app_config in apps.get_app_configs():
            module_name = f"{app_config.name}.tests"
            try:
                test_module = importlib.import_module(module_name)
            except ModuleNotFoundError as exc:
                if exc.name == module_name:
                    continue
                raise

            test_classes = inspect.getmembers(test_module, inspect.isclass)
            test_classes = [
                (name, test_class)
                for name, test_class in test_classes
                if issubclass(test_class, unittest.TestCase)
                and test_class is not unittest.TestCase
                and test_class.__module__ == test_module.__name__
            ]
            if not test_classes:
                continue

            document.add_heading(f"Приложение: {app_config.name}", level=1)
            for class_name, test_class in test_classes:
                document.add_heading(f"Класс: {class_name}", level=2)
                for method_name in sorted(dir(test_class)):
                    if not method_name.startswith("test_"):
                        continue
                    method = getattr(test_class, method_name)
                    if not callable(method):
                        continue
                    document.add_heading(f"Тест: {method_name}", level=3)
                    document.add_paragraph(
                        f"Описание: {method.__doc__ or 'Без описания'}"
                    )

                    try:
                        source = inspect.getsource(method)
                    except (OSError, TypeError):
                        continue
                    paragraph = document.add_paragraph()
                    run = paragraph.add_run(source)
                    run.font.name = "Consolas"
                    run.font.size = Pt(9.5)

        document.save(output_file)
        self.stdout.write(self.style.SUCCESS(f"Сохранено в {output_file}"))
