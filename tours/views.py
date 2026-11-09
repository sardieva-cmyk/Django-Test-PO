from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import BookingForm, ReviewForm, SignUpForm
from .models import Booking, Tour


class TourListView(ListView):
    model = Tour
    template_name = "tours/tour_list.html"
    context_object_name = "tours"

    def get_queryset(self):
        return Tour.objects.prefetch_related("categories")


class TourDetailView(DetailView):
    model = Tour
    template_name = "tours/tour_detail.html"
    context_object_name = "tour"

    def get_queryset(self):
        return Tour.objects.prefetch_related("categories", "reviews__tourist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["can_review"] = user.is_authenticated and Booking.objects.filter(
            tourist=user,
            tour=self.object,
            tour_date__lt=timezone.localdate(),
        ).exists()
        return context


class SignUpView(View):
    template_name = "tours/signup.html"

    def get(self, request):
        return render(request, self.template_name, {"form": SignUpForm()})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("tours:tour_list")
        return render(request, self.template_name, {"form": form})


@method_decorator(login_required(login_url="account_login"), name="dispatch")
class BookingCreateView(View):
    template_name = "tours/booking_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.tour = get_object_or_404(Tour, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, data=None):
        return BookingForm(data, tourist=self.request.user, tour=self.tour)

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {"form": self.get_form(), "tour": self.tour},
        )

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
            except IntegrityError:
                form.add_error(
                    None,
                    "На эту дату и время у вас уже забронирован другой тур.",
                )
            else:
                return redirect("tours:tour_detail", pk=self.tour.pk)
        return render(
            request,
            self.template_name,
            {"form": form, "tour": self.tour},
        )


@method_decorator(login_required(login_url="account_login"), name="dispatch")
class ReviewCreateView(View):
    template_name = "tours/review_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.tour = get_object_or_404(Tour, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, data=None):
        return ReviewForm(data, tourist=self.request.user, tour=self.tour)

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {"form": self.get_form(), "tour": self.tour},
        )

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tours:tour_detail", pk=self.tour.pk)
        return render(
            request,
            self.template_name,
            {"form": form, "tour": self.tour},
        )
