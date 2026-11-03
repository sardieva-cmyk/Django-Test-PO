from django.test import TestCase
from django.urls import reverse

from .models import Blog


class BlogListDetailTest(TestCase):
    def setUp(self):
        self.blog1 = Blog.objects.create(
            title="Первая статья",
            content="Текст первой статьи",
        )
        self.blog2 = Blog.objects.create(
            title="Вторая статья",
            content="Текст второй статьи",
        )

    def test_list_view_returns_content_and_200(self):
        response = self.client.get(reverse("blog_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Первая статья")
        self.assertContains(response, "Вторая статья")

    def test_blog_urls_are_mounted_under_blogs(self):
        self.assertEqual(reverse("blog_list"), "/blogs/")
        self.assertEqual(
            reverse("blog_detail", kwargs={"pk": self.blog1.pk}),
            f"/blogs/{self.blog1.pk}/",
        )

    def test_list_view_context_contains_correct_ids(self):
        response = self.client.get(reverse("blog_list"))
        blogs = response.context["blogs"]
        self.assertEqual(blogs.get(id=self.blog1.id).id, self.blog1.id)

    def test_list_view_contains_valid_detail_urls(self):
        response = self.client.get(reverse("blog_list"))
        url_1 = reverse("blog_detail", kwargs={"pk": self.blog1.pk})
        url_2 = reverse("blog_detail", kwargs={"pk": self.blog2.pk})
        self.assertContains(response, url_1)
        self.assertContains(response, url_2)

    def test_detail_view_returns_correct_data_by_id(self):
        url = reverse("blog_detail", kwargs={"pk": self.blog1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["blog"].title, "Первая статья")
        self.assertContains(response, "Текст первой статьи")

    def test_detail_view_nonexistent_id_returns_404(self):
        url = reverse("blog_detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class BlogPopularityTDDTest(TestCase):
    def setUp(self):
        self.blog = Blog.objects.create(
            title="Популярная статья",
            content="Контент статьи",
        )

    def test_new_blog_initial_views_count_is_zero(self):
        self.assertEqual(self.blog.views_count, 0)

    def test_detail_view_increments_views_count_by_one(self):
        url = reverse("blog_detail", kwargs={"pk": self.blog.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.blog.refresh_from_db()
        self.assertEqual(self.blog.views_count, 1)

    def test_each_detail_view_increments_views_count(self):
        url = reverse("blog_detail", kwargs={"pk": self.blog.pk})

        self.client.get(url)
        self.client.get(url)

        self.blog.refresh_from_db()
        self.assertEqual(self.blog.views_count, 2)
