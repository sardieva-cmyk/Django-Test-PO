from django.db.models import F
from django.views.generic import DetailView, ListView

from .models import Blog


class BlogListView(ListView):
    model = Blog
    template_name = "blog/blog_list.html"
    context_object_name = "blogs"


class BlogDetailView(DetailView):
    model = Blog
    template_name = "blog/blog_detail.html"
    context_object_name = "blog"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        Blog.objects.filter(pk=obj.pk).update(views_count=F("views_count") + 1)
        obj.refresh_from_db(fields=["views_count"])
        return obj
