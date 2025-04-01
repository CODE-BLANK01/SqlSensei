from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, hashers
from django.contrib import messages
from .forms import RegisterForm, LoginForm, CourseForm, AssignmentForm, QuestionForm
from .models import User, Instructor, Student
from courses.models import Course, CourseEnrollment
from assignments.models import Assignment
from questions.models import Question, AssignmentQuestion
from django.urls import reverse
from django.utils.timezone import now
from django.http import JsonResponse

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
    questions = Question.objects.filter(instructor=user_id)
    pending_enrollments = CourseEnrollment.objects.filter(enrollment_status='Pending')

    assignment_data = []
    for assignment in assignments:
        assignment_questions = AssignmentQuestion.objects.filter(assignment=assignment)
        questionsAssignment = [aq.question for aq in assignment_questions]
        
        assignment_data.append({
            'assignment': assignment,
            'questionsAssignment': questionsAssignment
        })

    return render(request, "users/instructor_dashboard.html", {
        "courses": courses,
        "assignments": assignment_data,
        "questions": questions,
        "pending_enrollments": pending_enrollments,
        "user_name": instructor.full_name,
        "show_manage_courses": True
    })


def student_dashboard(request):
    if "user_id" not in request.session:
        return redirect("login")
    user_id = request.session.get("user_id")
    student = User.objects.get(user_id = user_id)
    courses = Course.objects.all()
    return render(request, "users/student_dashboard.html", {
        "courses": courses, 
        "user_name": student.full_name
    })


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
        print(request.POST)  # Debugging: Check form data
        selected_questions = request.POST.get("questions", "").split(",")  # Get selected question IDs
        if form.is_valid():
            assignment = form.save(commit=False)
            course_id = request.POST.get("course_id")
            course = get_object_or_404(Course, course_id=course_id)
            instructor = User.objects.get(user_id=request.session.get("user_id"))
            assignment.course = course
            assignment.instructor = instructor
            assignment.save()
            print(f"selected_questions: {selected_questions}")  # Print errors if form is invalid
            # Insert records into Assignment_Questions table
            for question_id in selected_questions:
                if question_id.strip():  # Ensure it's not empty
                    question = get_object_or_404(Question, question_id=int(question_id))
                    AssignmentQuestion.objects.create(assignment=assignment, question=question)


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

def create_question(request):
    if "user_id" not in request.session:
        return redirect('/login/')

    if request.method == "POST":
        form = QuestionForm(request.POST)

        if form.is_valid():
            question = form.save(commit=False)
            user_id = request.session.get("user_id")
            created_by = User.objects.get(user_id=user_id)
            question.instructor = created_by  # Assign the creator
            question.save()
            messages.success(request, "Question created successfully.")
            return redirect(reverse("instructor_dashboard") + "?show_manage_questions=true") 
    else:
        form = QuestionForm()

    return render(request, "create_question.html", {"form": form})

def delete_question(request, question_id):
    if "user_id" not in request.session:
        return redirect('/login/')
    question = Question.objects.filter(question_id=question_id)
    question.delete()
    messages.success(request, "Qurstion deleted successfully.")
    return redirect(reverse('instructor_dashboard') + '?show_manage_questions=true')


def approve_student(request, enrollment_id):
    if "user_id" not in request.session:
        return redirect('/login/')
    enrollment = get_object_or_404(CourseEnrollment, pk=enrollment_id)
    #if request.user.is_staff:  # Ensuring only instructors can approve
    enrollment.enrollment_status = 'Approved'
    enrollment.approval_date = now()
    enrollment.save()
    messages.success(request, "Student approved successfully.")
    return redirect(reverse("instructor_dashboard") + "?show_student_approvals=true")


def deny_student(request, enrollment_id):
    if "user_id" not in request.session:
        return redirect('/login/')
    enrollment = get_object_or_404(CourseEnrollment, pk=enrollment_id)
    if request.user.is_staff:
        enrollment.enrollment_status = 'Denied'
        enrollment.approval_date = now()
        enrollment.save()
        messages.error(request, "Student enrollment denied.")
    return redirect(reverse("instructor_dashboard") + "?show_student_approvals=true")


def student_approvals(request):
    # Your logic here (e.g., fetching pending students for approval)
    return redirect(reverse("instructor_dashboard") + "?show_student_approvals=true")

def get_assignment_questions(request, assignment_id):
    # Fetch the questions for the given assignment
    assignment_questions = AssignmentQuestion.objects.filter(assignment_id=assignment_id)
    questions = [aq.question.question_title for aq in assignment_questions]
    
    return JsonResponse({'questions': questions})