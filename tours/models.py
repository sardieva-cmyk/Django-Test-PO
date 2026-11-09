from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class TouristProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tourist_profile",
        verbose_name="Пользователь",
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name="Телефон")

    class Meta:
        verbose_name = "профиль туриста"
        verbose_name_plural = "профили туристов"

    def __str__(self):
        return f"Профиль: {self.user}"


class TourCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")

    class Meta:
        ordering = ["name"]
        verbose_name = "категория тура"
        verbose_name_plural = "категории туров"

    def __str__(self):
        return self.name


class Tour(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Длительность (минут)",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена",
    )
    categories = models.ManyToManyField(
        TourCategory,
        related_name="tours",
        verbose_name="Категории",
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "тур"
        verbose_name_plural = "туры"

    def __str__(self):
        return self.title


class Booking(models.Model):
    tourist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tour_bookings",
        verbose_name="Турист",
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Тур",
    )
    tour_date = models.DateField(verbose_name="Дата тура")
    start_time = models.TimeField(verbose_name="Время начала")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")

    class Meta:
        ordering = ["tour_date", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["tourist", "tour_date", "start_time"],
                name="one_tour_per_tourist_time_slot",
            )
        ]
        verbose_name = "бронирование"
        verbose_name_plural = "бронирования"

    def __str__(self):
        return f"{self.tourist} — {self.tour} ({self.tour_date} {self.start_time})"

    def clean(self):
        if self.tour_date and self.tour_date < timezone.localdate():
            raise ValidationError({"tour_date": "Нельзя забронировать прошедшую дату."})


class Review(models.Model):
    tourist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tour_reviews",
        verbose_name="Автор",
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Тур",
    )
    text = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отзыва")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"

    def __str__(self):
        return f"Отзыв {self.tourist} о туре «{self.tour}»"

    def clean(self):
        if (
            self.tour_id
            and self.tourist_id
            and not Booking.objects.filter(
                tourist_id=self.tourist_id,
                tour_id=self.tour_id,
                tour_date__lt=timezone.localdate(),
            ).exists()
        ):
            raise ValidationError(
                "Оставить отзыв можно только о туре, в котором вы уже были."
            )
