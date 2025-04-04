from django import forms
from .models import CourseEnrollment, Course

class CourseEnrollmentForm(forms.ModelForm):
    class Meta: 
        model = CourseEnrollment
        fields = ['course_id']
        widgets = {
            'course_id': forms.HiddenInput()
        }

class CourseForm(forms.ModelForm): 
    class Meta:
        model = Course
        fields = ["course_title", "course_description", "course_token", "course_start_date", "course_end_date", "enrollment_status"]
        widgets = {
            "course_start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "course_end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "enrollment_status": forms.Select(choices=[(True, "Open"), (False, "Closed")], attrs={"class": "form-control"})
        }