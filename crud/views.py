from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import TaskForm
from .models import Task


class TaskListView(ListView):
    model = Task
    template_name = "crud/task_list.html"
    context_object_name = "tasks"


class TaskDetailView(DetailView):
    model = Task
    template_name = "crud/task_detail.html"
    context_object_name = "task"


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = "crud/task_form.html"
    success_url = reverse_lazy("crud:task_list")


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "crud/task_form.html"
    success_url = reverse_lazy("crud:task_list")


class TaskDeleteView(DeleteView):
    model = Task
    template_name = "crud/task_confirm_delete.html"
    success_url = reverse_lazy("crud:task_list")
