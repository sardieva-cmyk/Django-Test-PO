from django.test import TestCase
from django.urls import reverse

from .models import Task


class TaskCrudTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(
            title="Подготовить отчет",
            description="Собрать результаты",
        )

    def test_list_view_shows_tasks_and_create_link(self):
        response = self.client.get(reverse("crud:task_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
        self.assertContains(response, reverse("crud:task_create"))

    def test_list_view_shows_empty_state(self):
        Task.objects.all().delete()

        response = self.client.get(reverse("crud:task_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Задач пока нет.")

    def test_detail_view_shows_task(self):
        response = self.client.get(
            reverse("crud:task_detail", kwargs={"pk": self.task.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
        self.assertContains(response, self.task.description)

    def test_create_view_renders_form(self):
        response = self.client.get(reverse("crud:task_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Новая задача")
        self.assertContains(response, 'name="title"')

    def test_create_view_saves_task(self):
        response = self.client.post(
            reverse("crud:task_create"),
            {"title": "Новая задача", "description": "Описание"},
        )

        self.assertRedirects(response, reverse("crud:task_list"))
        self.assertTrue(Task.objects.filter(title="Новая задача").exists())

    def test_create_view_rejects_empty_title(self):
        response = self.client.post(
            reverse("crud:task_create"),
            {"title": "", "description": "Описание"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 1)

    def test_create_view_allows_empty_description(self):
        response = self.client.post(
            reverse("crud:task_create"),
            {"title": "Задача без описания", "description": ""},
        )

        self.assertRedirects(response, reverse("crud:task_list"))
        self.assertTrue(
            Task.objects.filter(
                title="Задача без описания",
                description="",
            ).exists()
        )

    def test_update_view_renders_existing_task(self):
        response = self.client.get(
            reverse("crud:task_update", kwargs={"pk": self.task.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Изменить задачу")
        self.assertContains(response, self.task.title)

    def test_update_view_changes_task(self):
        response = self.client.post(
            reverse("crud:task_update", kwargs={"pk": self.task.pk}),
            {"title": "Обновленная задача", "description": "Новое описание"},
        )

        self.assertRedirects(response, reverse("crud:task_list"))
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Обновленная задача")
        self.assertEqual(self.task.description, "Новое описание")

    def test_update_view_rejects_empty_title_without_changing_task(self):
        response = self.client.post(
            reverse("crud:task_update", kwargs={"pk": self.task.pk}),
            {"title": "", "description": "Новое описание"},
        )

        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Подготовить отчет")
        self.assertEqual(self.task.description, "Собрать результаты")

    def test_delete_view_renders_confirmation_without_deleting_task(self):
        response = self.client.get(
            reverse("crud:task_delete", kwargs={"pk": self.task.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_delete_view_removes_task(self):
        response = self.client.post(
            reverse("crud:task_delete", kwargs={"pk": self.task.pk})
        )

        self.assertRedirects(response, reverse("crud:task_list"))
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_detail_view_returns_404_for_missing_task(self):
        response = self.client.get(
            reverse("crud:task_detail", kwargs={"pk": 9999})
        )

        self.assertEqual(response.status_code, 404)

    def test_update_view_returns_404_for_missing_task(self):
        response = self.client.get(reverse("crud:task_update", kwargs={"pk": 9999}))

        self.assertEqual(response.status_code, 404)

    def test_delete_view_returns_404_for_missing_task(self):
        response = self.client.post(reverse("crud:task_delete", kwargs={"pk": 9999}))

        self.assertEqual(response.status_code, 404)
