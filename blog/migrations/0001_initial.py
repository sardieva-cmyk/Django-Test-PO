from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Blog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Заголовок")),
                ("content", models.TextField(verbose_name="Содержимое")),
                (
                    "views_count",
                    models.PositiveIntegerField(default=0, verbose_name="Просмотры/Лайки"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Дата создания"),
                ),
            ],
        ),
    ]
