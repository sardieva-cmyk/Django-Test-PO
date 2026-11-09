from django.urls import path

from .views import (
    BookingCreateView,
    ReviewCreateView,
    SignUpView,
    TourDetailView,
    TourListView,
)


app_name = "tours"

urlpatterns = [
    path("", TourListView.as_view(), name="tour_list"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("<int:pk>/", TourDetailView.as_view(), name="tour_detail"),
    path("<int:pk>/book/", BookingCreateView.as_view(), name="booking_create"),
    path("<int:pk>/review/", ReviewCreateView.as_view(), name="review_create"),
]
