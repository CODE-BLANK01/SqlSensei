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
from django.db import connection

# Handles course enrollment form submission and saves a new enrollment for the dynamically selected course by user
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
                

        return redirect('/users/student/dashboard/?show_course_enrollments=true')

# Creates and saves a new course linked to the currently logged-in instructor. Uses Dynamic SQL      
@login_required(login_url='/users/login/')
def create_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course_title = form.cleaned_data['course_title']
            course_description = form.cleaned_data['course_description']
            course_end_date = form.cleaned_data['course_end_date']
            course_start_date = form.cleaned_data['course_start_date']
            enrollment_status = form.cleaned_data['enrollment_status']
            course_token = form.cleaned_data['course_token']
            instructor_id = request.session.get("user_id")

            with connection.cursor() as cursor:
                # Get the instructor's user ID to associate with the course
                cursor.execute("SELECT user_id FROM Users WHERE user_id = %s", [instructor_id])
                instructor_row = cursor.fetchone()
                if not instructor_row:
                    messages.error(request, "Instructor not found.")
                    return redirect(reverse("instructor_dashboard"))
                instructor_id_db = instructor_row[0]

                # Insert course into the Course table
                cursor.execute("""
                    INSERT INTO Courses (course_title, course_description, course_end_date, course_start_date, instructor_id, course_token, enrollment_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [course_title, course_description, course_end_date, course_start_date, instructor_id_db, course_token, enrollment_status])

            messages.success(request, "Course created successfully.")
            return redirect(reverse("view_course") + "?show_manage_courses=true")

    else:
        form = CourseForm()

    return render(request, "users/instructor_dashboard.html", {
        "form": form,
        "show_form": True,
        "show_manage_courses": True
    })

# Deletes a course record from the database based on user selected course from GUI. Uses Dynamic SQL
@login_required(login_url='/users/login/')
def delete_course(request, course_id):
    with connection.cursor() as cursor:
        # Check if the course exists before attempting to delete
        cursor.execute("SELECT COUNT(*) FROM Courses WHERE course_id = %s", [course_id])
        if cursor.fetchone()[0] == 0:
            messages.error(request, "Course not found!")
            return redirect(reverse("instructor_dashboard") + '?show_manage_courses=true')
        # Delete the course
        cursor.execute("DELETE FROM Courses WHERE course_id = %s", [course_id])

    messages.success(request, "Course deleted successfully.")
    return redirect(reverse("view_course") + '?show_manage_courses=true')

# Approves a dynamically selected student's course enrollment from GUI and updates the status and timestamp in the database. Uses Dynamic SQL
@login_required(login_url='/users/login/')
def approve_student(request, enrollment_id):
    with connection.cursor() as cursor:
        # Check if the enrollment exists
        cursor.execute("SELECT COUNT(*) FROM Course_Enrollments WHERE enrollment_id = %s", [enrollment_id])
        if cursor.fetchone()[0] == 0:
            messages.error(request, "Enrollment not found!")
            return redirect(reverse("instructor_dashboard") + "?show_student_approvals=true")
        
        # Update the enrollment status to 'Approved' and set the approval date
        cursor.execute("""
            UPDATE Course_Enrollments
            SET enrollment_status = %s, approval_date = %s
            WHERE enrollment_id = %s
        """, ['Approved', now(), enrollment_id])

    messages.success(request, "Student approved successfully.")
    return redirect(reverse("instructor_dashboard") + "?show_student_approvals=true")

# Denies a student's course enrollment selected dynamically from GUI and updates the status and timestamp in the database. Uses Dynamic SQL
@login_required(login_url='/users/login/')
def deny_student(request, enrollment_id):
    with connection.cursor() as cursor:
        # Check if the enrollment exists
        cursor.execute("SELECT COUNT(*) FROM Course_Enrollments WHERE enrollment_id = %s", [enrollment_id])
        if cursor.fetchone()[0] == 0:
            messages.error(request, "Enrollment not found!")
            return redirect(reverse("instructor_dashboard") + "?show_student_approvals=true")
        
        # Update the enrollment status to 'Denied' and set the approval date
        cursor.execute("""
            UPDATE Course_Enrollments
            SET enrollment_status = %s, approval_date = %s
            WHERE enrollment_id = %s
        """, ['Denied', now(), enrollment_id])

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

# Fetches all assignments for a dynamically selected course from and the corresponding questions, then renders the course dashboard
# Uses Dynamic SQL
@login_required(login_url='/users/login/')
def course_dashboard(request, course_id):
    assignment_data = []

    with connection.cursor() as cursor:
        # Get assignments for the given course_id
        cursor.execute("SELECT * FROM Assignments WHERE course_id = %s", [course_id])
        assignments = cursor.fetchall()

        for assignment in assignments:
            assignment_id = assignment[0]  # Assuming the assignment_id is the first column
            assignment_title = assignment[1]  # Adjust indices as needed

            # Get questions for the current assignment
            cursor.execute("SELECT * FROM Assignment_Questions aq JOIN Questions q ON aq.question_id = q.question_id WHERE aq.assignment_id = %s", [assignment_id])
            questions_assignment = [
                {'question_id': row[3],'question_title': row[4], 'description': row[7]} for row in cursor.fetchall()
            ]
            print(questions_assignment)

            # Get submission details for the current user and assignment
            cursor.execute("""
                SELECT grade, submission_status, review_status 
                FROM Assignment_Submissions 
                WHERE assignment_id = %s 
                AND student_id = %s 
                AND submission_date = (
                    SELECT MAX(submission_date)
                    FROM Assignment_Submissions
                    WHERE assignment_id = %s 
                    AND student_id = %s
                )
            """, [assignment_id, request.user.user_id, assignment_id, request.user.user_id])

            submission = cursor.fetchone()

            if submission:
                grade, submission_status, review_status = submission
            else:
                grade = None
                submission_status = "Not Submitted"
                review_status = "Not Graded"

            # Append assignment data
            assignment_data.append({
                'assignment': {
                    'assignment_id': assignment_id,
                    'assignment_title': assignment_title
                },
                'questionsAssignment': questions_assignment,
                'grade': grade,
                'submission_status': submission_status,
                'review_status': review_status
            })

    return render(request, 'users/course_dashboard.html', {
        "course_id": course_id,
        "assignments": assignment_data,
    })

# Fetch the courses created by the logged in instructor user and display it to them. Uses Dynamic SQL
@login_required(login_url='/users/login/')
def view_course(request):
    user_id = request.session.get("user_id")
   
    # Fetch all courses data using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT course_id, course_title, course_description, instructor_id, course_token, course_start_date, course_end_date
            FROM Courses
            WHERE instructor_id = %s
        """, [user_id])

        rows = cursor.fetchall()

     # Create a list of dictionaries for the courses
        courses = [{
            'course_id': row[0],
            'course_title': row[1],
            'course_description': row[2],
            'instructor_id': row[3],  # Instructor ID is returned for reference
            'course_token': row[4],
            'course_start_date': row[5].strftime('%Y-%m-%d') if row[5] else None,  # Convert date to string
            'course_end_date': row[6].strftime('%Y-%m-%d') if row[6] else None  # Convert date to string
        } for row in rows]

    # Save the courses data to session
    request.session['courses'] = courses
    
    # Redirect to the appropriate dashboard with courses data
    return redirect(reverse("instructor_dashboard") + '?show_manage_courses=true')