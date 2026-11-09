from datetime import time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Booking, Review, Tour, TourCategory, TouristProfile

User = get_user_model()


class TourStartupTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tourist",
            password="test-password-123",
            email="tourist@example.com",
        )
        self.profile = TouristProfile.objects.create(user=self.user, phone="+77001234567")
        self.horse_category = TourCategory.objects.create(name="Конный")
        self.walking_category = TourCategory.objects.create(name="Пеший")
        self.tour = Tour.objects.create(
            title="Конная прогулка",
            description="Прогулка по горной тропе",
            duration_minutes=120,
            price=Decimal("15000.00"),
        )
        self.tour.categories.add(self.horse_category, self.walking_category)

    def booking_url(self, tour=None):
        return reverse("tours:booking_create", args=[(tour or self.tour).pk])

    def review_url(self, tour=None):
        return reverse("tours:review_create", args=[(tour or self.tour).pk])

    def test_tour_list_shows_tours_and_categories(self):
        response = self.client.get(reverse("tours:tour_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tour.title)
        self.assertContains(response, "Конный")
        self.assertContains(response, "Пеший")

    def test_tour_detail_shows_description_and_categories(self):
        response = self.client.get(
            reverse("tours:tour_detail", args=[self.tour.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tour.description)
        self.assertContains(response, "Конный")

    def test_tour_detail_returns_404_for_missing_tour(self):
        response = self.client.get(reverse("tours:tour_detail", args=[9999]))

        self.assertEqual(response.status_code, 404)

    def test_tour_categories_have_many_to_many_relationship(self):
        self.assertEqual(self.tour.categories.count(), 2)
        self.assertIn(self.tour, self.horse_category.tours.all())
        self.assertIn(self.tour, self.walking_category.tours.all())

    def test_tour_can_be_assigned_to_motor_category(self):
        motor_category = TourCategory.objects.create(name="Мото")
        motor_tour = Tour.objects.create(
            title="Мотопрогулка",
            description="Маршрут по степи",
            duration_minutes=180,
            price=Decimal("20000.00"),
        )
        motor_tour.categories.add(motor_category)

        self.assertIn(motor_category, motor_tour.categories.all())
        self.assertIn(motor_tour, motor_category.tours.all())

    def test_signup_post_creates_user_and_one_to_one_profile(self):
        response = self.client.post(
            reverse("tours:signup"),
            {
                "username": "new-tourist",
                "email": "new@example.com",
                "phone": "+77009876543",
                "password1": "Strong-password-9021",
                "password2": "Strong-password-9021",
            },
        )

        new_user = User.objects.get(username="new-tourist")
        self.assertRedirects(response, reverse("tours:tour_list"))
        self.assertEqual(new_user.email, "new@example.com")
        self.assertEqual(new_user.tourist_profile.phone, "+77009876543")
        self.assertEqual(TouristProfile.objects.filter(user=new_user).count(), 1)

    def test_signup_post_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("tours:signup"),
            {
                "username": "new-tourist",
                "email": "new@example.com",
                "phone": "",
                "password1": "Strong-password-9021",
                "password2": "Different-password-9021",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="new-tourist").exists())

    def test_login_post_authenticates_tourist(self):
        response = self.client.post(
            reverse("account_login"),
            {"username": "tourist", "password": "test-password-123"},
        )

        self.assertRedirects(response, reverse("tours:tour_list"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_post_ends_tourist_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("account_logout"))

        self.assertRedirects(response, reverse("tours:tour_list"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_booking_get_renders_submission_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.booking_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="tour_date"')
        self.assertContains(response, 'name="start_time"')

    def test_booking_post_saves_tourist_tour_date_and_time(self):
        self.client.force_login(self.user)
        tour_date = timezone.localdate() + timedelta(days=2)
        response = self.client.post(
            self.booking_url(),
            {"tour_date": tour_date.isoformat(), "start_time": "10:30"},
        )

        booking = Booking.objects.get()
        self.assertRedirects(
            response,
            reverse("tours:tour_detail", args=[self.tour.pk]),
        )
        self.assertEqual(booking.tourist, self.user)
        self.assertEqual(booking.tour, self.tour)
        self.assertEqual(booking.tour_date, tour_date)
        self.assertEqual(booking.start_time, time(10, 30))

    def test_tourist_cannot_book_a_second_tour_for_same_date_and_time(self):
        other_tour = Tour.objects.create(
            title="Пешая прогулка",
            description="По лесной тропе",
            duration_minutes=90,
            price=Decimal("8000.00"),
        )
        tour_date = timezone.localdate() + timedelta(days=2)
        Booking.objects.create(
            tourist=self.user,
            tour=self.tour,
            tour_date=tour_date,
            start_time=time(10, 30),
        )
        self.client.force_login(self.user)

        response = self.client.post(
            self.booking_url(other_tour),
            {"tour_date": tour_date.isoformat(), "start_time": "10:30"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже забронирован другой тур")
        self.assertEqual(Booking.objects.count(), 1)

    def test_booking_unique_constraint_blocks_duplicate_slot_in_database(self):
        tour_date = timezone.localdate() + timedelta(days=2)
        Booking.objects.create(
            tourist=self.user,
            tour=self.tour,
            tour_date=tour_date,
            start_time=time(10, 30),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Booking.objects.create(
                    tourist=self.user,
                    tour=self.tour,
                    tour_date=tour_date,
                    start_time=time(10, 30),
                )

    def test_same_tourist_can_book_another_time_or_date(self):
        tour_date = timezone.localdate() + timedelta(days=2)
        Booking.objects.create(
            tourist=self.user,
            tour=self.tour,
            tour_date=tour_date,
            start_time=time(10, 30),
        )
        second_booking = Booking.objects.create(
            tourist=self.user,
            tour=self.tour,
            tour_date=tour_date,
            start_time=time(11, 30),
        )

        self.assertEqual(self.user.tour_bookings.count(), 2)
        self.assertEqual(second_booking.tour, self.tour)

    def test_different_tourists_can_book_the_same_time_slot(self):
        other_user = User.objects.create_user(username="another")
        tour_date = timezone.localdate() + timedelta(days=2)
        Booking.objects.create(
            tourist=self.user,
            tour=self.tour,
            tour_date=tour_date,
            start_time=time(10, 30),
        )
        Booking.objects.create(
            tourist=other_user,
            tour=self.tour,
            tour_date=tour_date,
            start_time=time(10, 30),
        )

        self.assertEqual(Booking.objects.count(), 2)

    def test_booking_post_rejects_past_date(self):
        self.client.force_login(self.user)
        past_date = timezone.localdate() - timedelta(days=1)
        response = self.client.post(
            self.booking_url(),
            {"tour_date": past_date.isoformat(), "start_time": "10:30"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), 0)

    def test_booking_submission_requires_login(self):
        response = self.client.post(
            self.booking_url(),
            {
                "tour_date": (timezone.localdate() + timedelta(days=2)).isoformat(),
                "start_time": "10:30",
            },
        )

        self.assertRedirects(
            response,
            f"{reverse('account_login')}?next={self.booking_url()}",
        )
        self.assertEqual(Booking.objects.count(), 0)

    def test_review_submission_requires_login(self):
        response = self.client.post(self.review_url(), {"text": "Отличный тур"})

        self.assertRedirects(
            response,
            f"{reverse('account_login')}?next={self.review_url()}",
        )
        self.assertEqual(Review.objects.count(), 0)

    def test_review_post_saves_comment_for_completed_tour(self):
        Booking.objects.create(
            tourist=self.user,
            tour=self.tour,
            tour_date=timezone.localdate() - timedelta(days=2),
            start_time=time(10, 30),
        )
        self.client.force_login(self.user)

        response = self.client.post(self.review_url(), {"text": "Очень понравилось!"})

        review = Review.objects.get()
        self.assertRedirects(
            response,
            reverse("tours:tour_detail", args=[self.tour.pk]),
        )
        self.assertEqual(review.tourist, self.user)
        self.assertEqual(review.tour, self.tour)
        self.assertEqual(review.text, "Очень понравилось!")

    def test_tourist_can_leave_multiple_comments_about_completed_tours(self):
        Booking.objects.create(
            tourist=self.user,
            tour=self.tour,
            tour_date=timezone.localdate() - timedelta(days=2),
            start_time=time(10, 30),
        )
        self.client.force_login(self.user)

        first_response = self.client.post(
            self.review_url(),
            {"text": "Первая заметка"},
        )
        second_response = self.client.post(
            self.review_url(),
            {"text": "Вторая заметка"},
        )

        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(second_response.status_code, 302)
        self.assertEqual(self.user.tour_reviews.count(), 2)

    def test_review_post_rejects_unvisited_tour(self):
        self.client.force_login(self.user)

        response = self.client.post(self.review_url(), {"text": "Отличный тур"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "только о туре, в котором вы уже были")
        self.assertEqual(Review.objects.count(), 0)

    def test_review_post_rejects_future_booking(self):
        Booking.objects.create(
            tourist=self.user,
            tour=self.tour,
            tour_date=timezone.localdate() + timedelta(days=2),
            start_time=time(10, 30),
        )
        self.client.force_login(self.user)

        response = self.client.post(self.review_url(), {"text": "Отличный тур"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 0)

    def test_review_post_rejects_empty_comment(self):
        Booking.objects.create(
            tourist=self.user,
            tour=self.tour,
            tour_date=timezone.localdate() - timedelta(days=2),
            start_time=time(10, 30),
        )
        self.client.force_login(self.user)

        response = self.client.post(self.review_url(), {"text": ""})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 0)

    def test_user_has_one_to_one_profile_and_multiple_bookings_and_reviews(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.user.tourist_profile, self.profile)
        self.assertEqual(self.user.tour_bookings.count(), 0)
        self.assertEqual(self.user.tour_reviews.count(), 0)
