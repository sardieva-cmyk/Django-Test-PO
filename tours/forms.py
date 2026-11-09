from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Booking, Review, TouristProfile

User = get_user_model()


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
