from django.contrib import admin
from django.urls import include, path

from blog.views import BlogListView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("tasks/", include("crud.urls")),
    path("", BlogListView.as_view()),
    path("blogs/", include("blog.urls")),
]
