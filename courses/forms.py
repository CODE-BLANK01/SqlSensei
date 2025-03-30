from django import forms
from .models import CourseEnrollment

class CourseEnrollmentForm(forms.ModelForm):
    class Meta: 
        model = CourseEnrollment
        fields = ['course_id']
        widgets = {
            'course_id': forms.HiddenInput()
        }