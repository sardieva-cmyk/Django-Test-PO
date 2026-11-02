from django.urls import path

from .views import BlogDetailView, BlogListView


urlpatterns = [
    path("", BlogListView.as_view(), name="blog_list"),
    path("blogs/", BlogListView.as_view()),
    path("blogs/<int:pk>/", BlogDetailView.as_view(), name="blog_detail"),
]
