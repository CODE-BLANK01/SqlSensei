from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, hashers
from .models import User, Instructor, Student
from courses.models import Course
from assignments.models import Assignment
from questions.models import Question


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    about_me = forms.CharField(widget=forms.Textarea, required=False)  # for Instructors
    grade_level = forms.ChoiceField(choices=[('UnderGraduate', 'UnderGraduate'), ('Graduate', 'Graduate')], required=False)  # for Students

    verification_code = forms.CharField(
        max_length=6,
        required=True,
        label="Email Verification Code", 
        widget=forms.TextInput(attrs={"placeholder": "Enter the code sent to your email"})
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'password', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the role-specific fields based on the role selected
        if self.instance and self.instance.pk:
            # If editing an existing user (this is for the admin case, for instance)
            role = self.instance.role
        else:
            role = self.data.get('role')

        if role == 'Instructor':
            self.fields['about_me'].required = True  # make 'about_me' required for Instructors
            self.fields['grade_level'].widget = forms.HiddenInput()  # hide grade_level for Instructors
        elif role == 'Student':
            self.fields['grade_level'].required = True  # make 'grade_level' required for Students
            self.fields['about_me'].widget = forms.HiddenInput()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        # Create the corresponding Student or Instructor after user is saved
        if user.role == "Student":
            grade_level = self.cleaned_data.get("grade_level")
            Student.objects.create(student=user, grade_level=grade_level)
        elif user.role == "Instructor":
            about_me = self.cleaned_data.get("about_me")
            Instructor.objects.create(instructor=user, about_me=about_me)
        return user

class LoginForm(forms.Form):
    username = forms.EmailField(label="username", widget=forms.EmailInput(attrs={"autofocus": True}))
    password = forms.CharField(widget=forms.PasswordInput)

# class CourseForm(forms.ModelForm): Akshay
#     class Meta:
#         model = Course
#         fields = ["course_title", "course_description", "course_token", "course_start_date", "course_end_date", "enrollment_status"]
#         widgets = {
#             "course_start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
#             "course_end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
#             "enrollment_status": forms.Select(choices=[(True, "Open"), (False, "Closed")], attrs={"class": "form-control"})
#         }

# class AssignmentForm(forms.ModelForm): Akshay
#     class Meta:
#         model = Assignment
#         fields = ['assignment_title', 'description', 'deadline']

# class QuestionForm(forms.ModelForm): Akshay
#     class Meta:
#         model = Question
#         fields = ['question_title', 'topic', 'difficulty_level', 'description', 'access_type']
