import inspect
import unittest

from django.core.management.base import BaseCommand
from django.test.runner import DiscoverRunner
from docx import Document
from docx.shared import Pt


class Command(BaseCommand):
    help = "Экспортирует обнаруженные Django-тесты проекта в файл Word (.docx)"

    def add_arguments(self, parser):
        parser.add_argument("--output", type=str, default="Django_Tests.docx")

    def handle(self, *args, **options):
        output_file = options["output"]
        document = Document()
        document.add_heading("Документация тестов Django", level=0)
        suite = DiscoverRunner(verbosity=0).build_suite()
        current_app = None
        current_class = None
        test_count = 0

        for test_case in self._iter_test_cases(suite):
            test_class = test_case.__class__
            app_name = test_class.__module__.split(".", 1)[0]
            if app_name != current_app:
                document.add_heading(f"Приложение: {app_name}", level=1)
                current_app = app_name
                current_class = None
            if test_class is not current_class:
                document.add_heading(f"Класс: {test_class.__name__}", level=2)
                current_class = test_class

            method_name = test_case.id().rsplit(".", 1)[-1]
            method = getattr(test_case, method_name)
            document.add_heading(f"Тест: {method_name}", level=3)
            document.add_paragraph(
                f"Описание: {inspect.getdoc(method) or 'Без описания'}"
            )
            try:
                source = inspect.getsource(method)
            except (OSError, TypeError):
                source = None
            if source:
                paragraph = document.add_paragraph()
                run = paragraph.add_run(source)
                run.font.name = "Consolas"
                run.font.size = Pt(9.5)
            test_count += 1

        if not test_count:
            document.add_paragraph("Тесты не найдены.")
        document.save(output_file)
        self.stdout.write(
            self.style.SUCCESS(
                f"Экспортировано тестов: {test_count}. Сохранено в {output_file}"
            )
        )

    @classmethod
    def _iter_test_cases(cls, suite):
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                yield from cls._iter_test_cases(test)
            elif isinstance(test, unittest.TestCase):
                yield test
