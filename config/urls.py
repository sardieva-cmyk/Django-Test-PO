from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from blog.views import BlogListView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("tasks/", include("crud.urls")),
    path("tours/", include("tours.urls")),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="account_login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="account_logout"),
    path("", BlogListView.as_view()),
    path("blogs/", include("blog.urls")),
]
