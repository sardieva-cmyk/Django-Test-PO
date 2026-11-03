from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "задача"
        verbose_name_plural = "задачи"

    def __str__(self):
        return self.title
