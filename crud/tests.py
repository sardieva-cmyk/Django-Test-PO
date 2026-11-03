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

    def test_detail_view_shows_task(self):
        response = self.client.get(
            reverse("crud:task_detail", kwargs={"pk": self.task.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.title)
        self.assertContains(response, self.task.description)

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

    def test_update_view_changes_task(self):
        response = self.client.post(
            reverse("crud:task_update", kwargs={"pk": self.task.pk}),
            {"title": "Обновленная задача", "description": "Новое описание"},
        )

        self.assertRedirects(response, reverse("crud:task_list"))
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Обновленная задача")
        self.assertEqual(self.task.description, "Новое описание")

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
