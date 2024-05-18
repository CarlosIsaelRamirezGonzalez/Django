from django.forms import ModelForm # Clase para crear formularios
from .models import Task


class TaskForm(ModelForm):
    class Meta: 
        model = Task
        fields = ['title', 'description', 'important']