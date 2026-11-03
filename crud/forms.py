from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"maxlength": 200}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }
