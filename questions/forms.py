from django import forms
from .models import Question

class QuestionForm(forms.ModelForm): 
    class Meta:
        model = Question
        fields = ['question_title', 'topic', 'difficulty_level', 'description', 'access_type']