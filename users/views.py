from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, hashers
from .forms import RegisterForm, LoginForm
from .models import User
from courses.models import Course, CourseEnrollment
from assignments.models import Assignment, AssignmentSubmission
from questions.models import Question, AssignmentQuestion
from chat.models import Message
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Subquery, OuterRef
from django.contrib.auth.decorators import login_required
from django.db import connection

# Registers a new user by saving to the User table
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})

# Authenticates user by querying the User table and checking credentials which were entered dynamically in textbox
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
                        return redirect('/users/instructor/dashboard/?show_home=true')
                    elif user.role == "Student":
                        return redirect('/users/student/dashboard/?show_home=true')
                    else:
                        return redirect("welcome")
            except User.DoesNotExist:
                return render(request, "users/login.html", {"form": form, "error": "Invalid credentials"})
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})

# Logs the logged in user out of the current session
def logout_view(request):
    logout(request)
    return redirect("login")

# Loads instructor-specific dynamically selected data from multiple models for dashboard rendering
@login_required(login_url='/users/login/')  # Redirects to login if user is not authenticated
def instructor_dashboard(request):

    user_id = request.session.get("user_id")
    instructor = User.objects.get(user_id=user_id)
    allQuestions = Question.objects.all()
    submissions = AssignmentSubmission.objects.filter(review_status="Not Graded")
    #pending_enrollments = CourseEnrollment.get_pending_enrollments_for_instructor(user_id)
    pending_enrollments = CourseEnrollment.objects.filter(
    enrollment_status='Pending',
    course_id__instructor=request.user
    )


    query = request.session.get("query", "")
    sql_query = request.session.get("sql_query", "")
    columns = request.session.get("columns", [])
    results = request.session.get("results", [])
    error = request.session.get("error", "")
    courses = request.session.get("courses", [])
    assignments = request.session.get("assignments", [])
    questions = request.session.get("questions", [])
    leaderboard_data = request.session.get('leaderboard_data', [])

    request.session.pop("query", None)
    request.session.pop("sql_query", None)
    request.session.pop("columns", None)
    request.session.pop("results", None)
    request.session.pop("error", None)
    request.session.pop("courses", None)
    request.session.pop("assignments", None)
    request.session.pop("questions", None)
    request.session.pop("leaderboard_data", None)

    users = User.objects.exclude(user_id=user_id)
    messages = Message.objects.filter(receiver=request.user).order_by('-message_date')
    if not courses:
        courses = Course.objects.filter(instructor=user_id)
    if not questions:
        questions = Question.objects.filter(instructor=user_id)

    assignment_data = []
    for assignment in assignments:
        assignment_questions = AssignmentQuestion.objects.filter(assignment=assignment['assignment_id'])
        questionsAssignment = [aq.question for aq in assignment_questions]
        
        assignment_data.append({
            'assignment': assignment,
            'questionsAssignment': questionsAssignment
        })

    return render(request, "users/instructor_dashboard.html", {
        "courses": courses,
        "assignments": assignment_data,
        "questions": questions,
        "allQuestions": allQuestions,
        "pending_enrollments": pending_enrollments,
        "user_name": instructor.full_name,
        "show_manage_courses": True,
        "query": query,
        "sql_query": sql_query,
        "columns": columns,
        "results": results,
        "error": error,
        "users": users,
        "messages": messages,
        "submissions":submissions,
        "leaderboard": leaderboard_data,
    })

# Loads student-specific dynamically selected data from multiple models for dashboard rendering
@login_required(login_url='/users/login/')
def student_dashboard(request):

    user_id = request.session.get("user_id")
    student = User.objects.get(user_id = user_id)
    enrolled_courses = CourseEnrollment.objects.filter(student_id=student).values_list('course_id', flat=True)

    query = request.session.get("query", "")
    sql_query = request.session.get("sql_query", "")
    columns = request.session.get("columns", [])
    results = request.session.get("results", [])
    error = request.session.get("error", "")
    leaderboard_data = request.session.get('leaderboard_data', [])

    # Subquery to find course IDs where the current student has an 'Approved' enrollment.
    # This is used with OuterRef to later filter the Course table for only those approved enrollments.
    approved_course_ids = CourseEnrollment.objects.filter(
    student_id=student,
    enrollment_status='Approved',
    course_id=OuterRef('course_id')
    ).values('course_id')
    approved_courses = Course.objects.filter(course_id__in=Subquery(approved_course_ids))

    request.session.pop("query", None)
    request.session.pop("sql_query", None)
    request.session.pop("columns", None)
    request.session.pop("results", None)
    request.session.pop("error", None)
    request.session.pop("users", None)
    request.session.pop("errmessagesor", None)
    
    messages = Message.objects.filter(receiver=request.user).order_by('-message_date')
    users = User.objects.exclude(user_id=user_id) 
    # Exclude those courses from the available list which are already requested enrollment
    available_courses = Course.objects.exclude(course_id__in=enrolled_courses).filter(enrollment_status=True)
    return render(request, "users/student_dashboard.html", {
        "courses": available_courses, 
        "user_name": student.full_name,
        "query": query,
        "sql_query": sql_query,
        "columns": columns,
        "results": results,
        "error": error,
        "leaderboard": leaderboard_data,
        "users": users,
        "messages": messages,
        "approved_courses":approved_courses
    })

# Returns list of questions for a dynamically selected assignment
@login_required(login_url='/users/login/')
def get_assignment_questions(request, assignment_id):
    # Fetch the questions for the given assignment
    assignment_questions = AssignmentQuestion.objects.filter(assignment_id=assignment_id)
    questions = [aq.question.question_title for aq in assignment_questions]
    
    return JsonResponse({'questions': questions})

# Handles dynamic message creation and stores it in the database. Uses Dynamic SQL
@login_required(login_url='/users/login/')
def send_message(request):
    user_id = request.session.get("user_id")
    user = User.objects.get(user_id = user_id)
    user_role = user.role.lower()

    if user_role == "student":
        url = "/users/student/dashboard/?show_messages=true"
    elif user_role == "instructor":
        url = "/users/instructor/dashboard/?show_messages=true" 
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        message_content = request.POST.get("message_content")
        get_object_or_404(User, pk=receiver_id)
        
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Messages (sender_id, receiver_id, message_content, message_date)
                VALUES (%s, %s, %s, NOW())
            """
            cursor.execute(sql, [user_id, receiver_id, message_content])
        return redirect(url)
    return redirect(url)
