from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, hashers
from django.contrib import messages
from .forms import RegisterForm, LoginForm, CourseForm, AssignmentForm
from .models import User, Instructor, Student
from courses.models import Course
from assignments.models import Assignment
from django.urls import reverse

# ------------------------------
# Auth Views
# ------------------------------

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            try:
                user = User.objects.get(username=username)
                if hashers.check_password(password, user.password):
                    request.session["user_id"] = user.user_id
                    request.session["username"] = user.username
                    request.session["role"] = user.role
                    request.session.save()
                    login(request, user)

                    if user.role == "Instructor":
                        return redirect("instructor_dashboard")
                    elif user.role == "Student":
                        return redirect("student_dashboard")
                    else:
                        return redirect("welcome")
            except User.DoesNotExist:
                return render(request, "users/login.html", {"form": form, "error": "Invalid credentials"})
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def welcome_view(request):
    username = request.session.get("username")
    role = request.session.get("role")
    return render(request, "users/welcome.html", {"username": username, "role": role})

# ------------------------------
# Dashboards
# ------------------------------

def instructor_dashboard(request):
    if "user_id" not in request.session:
        return redirect("login")

    user_id = request.session.get("user_id")
    instructor = User.objects.get(user_id=user_id)
    courses = Course.objects.filter(instructor=user_id)
    assignments = Assignment.objects.filter(instructor=user_id)

    return render(request, "users/instructor_dashboard.html", {
        "courses": courses,
        "assignments": assignments,
        "user_name": instructor.full_name,
        "show_manage_courses": True
    })


def student_dashboard(request):
    if "user_id" not in request.session:
        return redirect("login")
    return render(request, "users/student_dashboard.html")


# ------------------------------
# Course & Assignment Management
# ------------------------------

def create_course(request):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            instructor = User.objects.get(user_id=request.session.get("user_id"))
            course.instructor = instructor
            course.save()
            return redirect(reverse("instructor_dashboard") + "?show_manage_courses=true")
    else:
        form = CourseForm()

    return render(request, "users/instructor_dashboard.html", {
        "form": form,
        "show_form": True,
        "show_manage_courses": True
    })


def create_assignment(request):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            course_id = request.POST.get("course_id")
            course = get_object_or_404(Course, course_id=course_id)
            instructor = User.objects.get(user_id=request.session.get("user_id"))
            assignment.course = course
            assignment.instructor = instructor
            assignment.save()
            messages.success(request, "Assignment created successfully.")
            return redirect(reverse("instructor_dashboard") + "?show_manage_assignments=true")
    else:
        form = AssignmentForm()

    return render(request, "users/instructor_dashboard.html", {
        "form": form,
        "show_form": True,
        "show_manage_courses": True
    })


def delete_course(request, course_id):
    if "user_id" not in request.session:
        return redirect("login")

    course = get_object_or_404(Course, course_id=course_id)
    course.delete()
    messages.success(request, "Course deleted successfully.")
    return redirect(reverse("instructor_dashboard") + '?show_manage_courses=true')


def delete_assignment(request, assignment_id):
    if "user_id" not in request.session:
        return redirect("login")

    assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
    assignment.delete()
    messages.success(request, "Assignment deleted successfully.")
    return redirect(reverse("instructor_dashboard") + '?show_manage_assignments=true')
