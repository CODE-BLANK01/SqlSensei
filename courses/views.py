from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import CourseEnrollmentForm
from .models import CourseEnrollment, Course
from users.models import User

# Create your views here.
def apply_for_course(request):
    if request.method == 'POST':
        form = CourseEnrollmentForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course_id']
            student = User.objects.get(user_id=request.session['user_id'])

            # 防止重复报名
            existing = CourseEnrollment.objects.filter(student_id=student, course_id=course).exists()
            if existing:
                messages.warning(request, "You already applied for this course.")
            else:
                enrollment = form.save(commit=False)
                enrollment.student_id = student
                enrollment.enrollment_status = 'Pending'
                enrollment.save()
                messages.success(request, "Enrollment submitted.")

        return redirect('/users/student/dashboard/?show_course_enrollments=true')