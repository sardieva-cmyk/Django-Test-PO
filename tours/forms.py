from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.db import transaction
import random

from .models import Booking, Review, TouristProfile

User = get_user_model()


class CaptchaLoginForm(AuthenticationForm):
    captcha_answer = forms.IntegerField(
        label="Ответ на задачу",
        help_text="Введите результат примера",
    )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, request=request, **kwargs)
        if request is not None:
            if "login_captcha_answer" not in request.session:
                left = random.randint(1, 9)
                right = random.randint(1, 9)
                request.session["login_captcha"] = f"{left} + {right}"
                request.session["login_captcha_answer"] = left + right

    def clean_captcha_answer(self):
        answer = self.cleaned_data["captcha_answer"]
        expected = self.request.session.get("login_captcha_answer")
        if expected is None or answer != expected:
            raise forms.ValidationError("Неверный ответ на капчу.")
        return answer


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Электронная почта")
    phone = forms.CharField(max_length=30, required=False, label="Телефон")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "phone")

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            TouristProfile.objects.create(user=user, phone=self.cleaned_data["phone"])
        return user


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["tour_date", "start_time"]
        widgets = {
            "tour_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, tourist, tour, **kwargs):
        self.tourist = tourist
        self.tour = tour
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        tour_date = cleaned_data.get("tour_date")
        start_time = cleaned_data.get("start_time")
        if (
            tour_date
            and start_time
            and Booking.objects.filter(
                tourist=self.tourist,
                tour_date=tour_date,
                start_time=start_time,
            ).exists()
        ):
            raise forms.ValidationError(
                "На эту дату и время у вас уже забронирован другой тур."
            )
        return cleaned_data

    def save(self, commit=True):
        booking = super().save(commit=False)
        booking.tourist = self.tourist
        booking.tour = self.tour
        if commit:
            booking.save()
        return booking


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, tourist, tour, **kwargs):
        self.tourist = tourist
        self.tour = tour
        kwargs.setdefault("instance", Review(tourist=tourist, tour=tour))
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        review = super().save(commit=False)
        review.tourist = self.tourist
        review.tour = self.tour
        if commit:
            review.save()
        return review
