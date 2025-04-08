from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AssignmentForm
from questions.models import AssignmentQuestion, Question
from django.contrib import messages
from courses.models import Course
from django.db import connection
from django.urls import reverse
from users.models import User
from .models import Assignment, AssignmentSubmission
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, FileResponse
import os
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

@login_required(login_url='/users/login/')
def create_assignment(request):
    """
    Creates a new assignment and links selected questions to it.
    Uses dynamic SQL to insert into Assignments and Assignment_Questions tables.
    """
    if request.method == "POST":
        
        form = AssignmentForm(request.POST)
        selected_questions = request.POST.get("questions", "").split(",")
        
        if form.is_valid():
            assignment_title = form.cleaned_data["assignment_title"]
            description = form.cleaned_data["description"]
            deadline = form.cleaned_data["deadline"]
            release_date = now()            
            course_id = request.POST.get("course_id")
            instructor_id = request.session.get("user_id")

            course = get_object_or_404(Course, course_id=course_id)
            instructor = get_object_or_404(User, user_id=instructor_id)

            with connection.cursor() as cursor:
                # Insert into Assignments table
                insert_query = """
                    INSERT INTO Assignments (assignment_title, description, release_date, deadline, course_id, instructor_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, [assignment_title, description, release_date, deadline, course.course_id, instructor.user_id])

                # Get the ID of the newly inserted assignment
                assignment_id = cursor.lastrowid

                # Insert selected questions into AssignmentQuestion table
                for question_id in selected_questions:
                    if question_id.strip():
                        cursor.execute("SELECT COUNT(*) FROM Questions WHERE question_id = %s", [question_id])
                        if cursor.fetchone()[0] > 0:
                            cursor.execute("""
                                INSERT INTO Assignment_Questions (assignment_id, question_id)
                                VALUES (%s, %s)
                            """, [assignment_id, question_id])

            return redirect(reverse("view_assignments") + "?show_manage_assignments=true")
    
    else:
        form = AssignmentForm()

    return render(request, "users/instructor_dashboard.html", {
        "form": form,
        "show_form": True,
        "show_manage_assignments": True
    })

@login_required(login_url='/users/login/')
def delete_assignment(request, assignment_id):
    """
    Deletes the assignment with the given ID.
    Uses dynamic SQL to delete from the Assignments table.
    """
    
    query = "DELETE FROM Assignments WHERE assignment_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, [assignment_id])
    
    return redirect(reverse("view_assignments") + '?show_manage_assignments=true')

@login_required(login_url='/users/login/')
def submit_assignment(request, assignment_id):
    """
    Handles file upload and saves a student's assignment submission.
    """

    user_id = request.session.get("user_id")
    student = User.objects.get(user_id = user_id)
    
    try:
        assignment = Assignment.objects.get(pk=assignment_id)
    except ObjectDoesNotExist:
        return HttpResponse("Assignment not found", status=404)

    if request.method == 'POST' and request.FILES.get('zipFile'):
        zip_file = request.FILES['zipFile']
        print("Type of zip_file:", type(zip_file))
        # Create an AssignmentSubmission entry
        submission = AssignmentSubmission(
            assignment=assignment,
            student=student,
            submitted_answer=zip_file,
            submission_status='Submitted',
            review_status='Not Graded'
        )
        submission.save()
        course_id = assignment.course.course_id
        messages.success(request, "Submitted Successfully.")
        return redirect('course_dashboard', course_id=course_id)

    return HttpResponse("Invalid request", status=400)


@login_required(login_url='/users/login/')
def grade_assignment(request):
    """
    Displays ungraded submissions and allows the instructor to grade them.
    Uses dynamic SQL to fetch and update Assignment_Submissions.
    """

    submissions = []
    # Fetch all submissions that are 'Not Graded' using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.submission_id, s.student_id, u.full_name, a.assignment_title, s.grade, s.review_status
        FROM Assignment_Submissions s
        JOIN Users u ON s.student_id = u.user_id
        JOIN Assignments a ON a.assignment_id = s.assignment_id
        WHERE s.review_status = %s
        AND s.submission_date = (
            SELECT MAX(submission_date)
            FROM Assignment_Submissions
            WHERE assignment_id = s.assignment_id
            AND student_id = s.student_id
        )
    """, ["Not Graded"])
        
        rows = cursor.fetchall()
        for row in rows:
            submissions.append({
                "submission_id": row[0],
                "student_id": row[1],
                "student_name": row[2],
                "assignment_title": row[3],
                "grade": row[4],
                "review_status": row[5],
            })

    if request.method == 'POST':
        submission_id = request.POST.get("submission_id")
        grade = request.POST.get("grade")

        with connection.cursor() as cursor:
            # Check if submission exists
            cursor.execute("SELECT student_id FROM Assignment_Submissions WHERE submission_id = %s", [submission_id])
            result = cursor.fetchone()
            if not result:
                messages.error(request, "Submission not found!")
                return redirect('grade_assignment')

            student_id = result[0]

            # Update the grade and review_status
            cursor.execute("""
                UPDATE Assignment_Submissions
                SET grade = %s, review_status = %s
                WHERE submission_id = %s
            """, [grade, "Graded", submission_id])

            # Get the student's full name for the message
            cursor.execute("SELECT full_name FROM Users WHERE user_id = %s", [student_id])
            student_name = cursor.fetchone()[0] if cursor.rowcount > 0 else "Student"

        return redirect('grade_assignment')

    return render(request, 'users/grade_assignment.html', {"submissions": submissions})

# Fetches and returns the submitted assignment file from the server for download
@login_required(login_url='/users/login/')
def download_submission(request, submission_id):
    """
    Serves the submitted file for the given submission ID as a downloadable response.
    Uses FileResponse to return the file if it exists on disk.
    """
    submission = get_object_or_404(AssignmentSubmission, submission_id=submission_id)

    if not submission.submitted_answer:
        return HttpResponse("File not found", status=404)

    file_path = submission.submitted_answer.path  # This should work if using FileField properly

    if not os.path.exists(file_path):
        return HttpResponse("File does not exist on the server", status=404)

    # Open and return the file response
    return FileResponse(open(file_path, "rb"), as_attachment=True, filename=os.path.basename(file_path))

@login_required(login_url='/users/login/')
def view_assignments(request):
    """
    Retrieves and stores assignments created by the logged-in instructor.
    Uses dynamic SQL to fetch assignment and course data.
    """
    user_id = request.session.get("user_id")
   
     # Fetch all assignments data using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT assignment_id, assignment_title, description, deadline, release_date, a.instructor_id, c.course_title
            FROM Assignments a
            JOIN Courses c ON c.course_id = a.course_id
            WHERE a.instructor_id = %s
        """, [user_id])

        rows = cursor.fetchall()

    # Create a list of dictionaries for the assignments
    assignments = [{
        'assignment_id': row[0],
        'assignment_title': row[1],
        'description': row[2],
        'deadline': row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None,  # Convert datetime to string
        'release_date': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None,  # Convert datetime to string
        'instructor_id': row[5],
        'course_title': row[6]  # You can fetch the course details if needed
    } for row in rows]

    # Save the leaderboard data to session
    request.session['assignments'] = assignments
    
    # Redirect to the appropriate dashboard with leaderboard data
    return redirect(reverse("instructor_dashboard") + '?show_manage_assignments=true')