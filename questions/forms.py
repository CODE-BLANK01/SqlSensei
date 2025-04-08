from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_title', 'topic', 'difficulty_level', 'description', 
                 'schema_sql', 'sample_data_sql', 'expected_output',  'access_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'schema_sql': forms.Textarea(attrs={'rows': 6, 'class': 'code-editor'}),
            'sample_data_sql': forms.Textarea(attrs={'rows': 6, 'class': 'code-editor'}),
            'expected_output': forms.Textarea(attrs={'rows': 4}),
        }