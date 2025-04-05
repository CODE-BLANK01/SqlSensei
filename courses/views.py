from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import CourseEnrollmentForm, CourseForm
from .models import CourseEnrollment, Course
from users.models import User
from django.utils.timezone import now
from assignments.models import Assignment, AssignmentSubmission
from questions.models import AssignmentQuestion
from django.contrib.auth.decorators import login_required

# Handles course enrollment form submission and saves a new enrollment if not already applied
@login_required(login_url='/users/login/')
def apply_for_course(request):
    if request.method == 'POST':
        form = CourseEnrollmentForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course_id']
            student = User.objects.get(user_id=request.session['user_id'])

            # avoid duplicate application
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

# Creates and saves a new course linked to the currently logged-in instructor        
@login_required(login_url='/users/login/')
def create_course(request):
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

# Deletes a course record from the database based on user selected course from GUI
@login_required(login_url='/users/login/')
def delete_course(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    course.delete()
    messages.success(request, "Course deleted successfully.")
    return redirect(reverse("instructor_dashboard") + '?show_manage_courses=true')

# Approves a selected student's course enrollment from GUI and updates the status and timestamp in the database
@login_required(login_url='/users/login/')
def approve_student(request, enrollment_id):
    enrollment = get_object_or_404(CourseEnrollment, pk=enrollment_id)
    #if request.user.is_staff:  # Ensuring only instructors can approve
    enrollment.enrollment_status = 'Approved'
    enrollment.approval_date = now()
    enrollment.save()
    messages.success(request, "Student approved successfully.")
    return redirect(reverse("instructor_dashboard") + "?show_student_approvals=true")

# Denies a student's course enrollment from GUI and updates the status and timestamp in the database
@login_required(login_url='/users/login/')
def deny_student(request, enrollment_id):
    enrollment = get_object_or_404(CourseEnrollment, pk=enrollment_id)
    
    enrollment.enrollment_status = 'Denied'
    enrollment.approval_date = now()
    enrollment.save()
    messages.error(request, "Student enrollment denied.")
    return redirect(reverse("instructor_dashboard") + "?show_student_approvals=true")

# Redirects to student approvals view (approval logic is handled elsewhere)
@login_required(login_url='/users/login/')
def student_approvals(request):
    # Your logic here (e.g., fetching pending students for approval)
    return redirect(reverse("instructor_dashboard") + "?show_student_approvals=true")

# Redirects to the student's dashboard with a list of available courses
@login_required(login_url='/users/login/')
def view_courses(request):

    # Redirect to the dashboard with leaderboard data
    return redirect("/users/student/dashboard/?show_courses=true")

# Fetches all assignments for a course and the corresponding questions, then renders the course dashboard
@login_required(login_url='/users/login/')
def course_dashboard(request, course_id):
    assignments = Assignment.objects.filter(course=course_id)
    assignment_data = []
    for assignment in assignments:
        assignment_questions = AssignmentQuestion.objects.filter(assignment=assignment)
        questionsAssignment = [aq.question for aq in assignment_questions]
        try:
            submission = AssignmentSubmission.objects.get(assignment=assignment, student=request.user)
            grade = submission.grade
            submission_status = submission.submission_status
            review_status = submission.review_status
        except AssignmentSubmission.DoesNotExist:
            grade = None
            submission_status = "Not Submitted"
            review_status = "Not Graded"

        assignment_data.append({
            'assignment': assignment,
            'questionsAssignment': questionsAssignment,
            'grade': grade,
            'submission_status': submission_status,
            'review_status': review_status
        })
    return render(request, 'users/course_dashboard.html', {
    "course_id": course_id,
    "assignments": assignment_data,})