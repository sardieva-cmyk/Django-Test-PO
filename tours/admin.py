from django.contrib import admin

from .models import Booking, Review, Tour, TourCategory, TouristProfile


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "duration_minutes")
    list_filter = ("categories",)
    filter_horizontal = ("categories",)


admin.site.register(TourCategory)
admin.site.register(TouristProfile)
admin.site.register(Booking)
admin.site.register(Review)
