from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AssignmentForm
from questions.models import AssignmentQuestion, Question
from django.contrib import messages
from courses.models import Course
from django.urls import reverse
from users.models import User
from .models import Assignment, AssignmentSubmission
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, FileResponse
import os

# Create your views here.
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

def delete_assignment(request, assignment_id):
    if "user_id" not in request.session:
        return redirect("login")

    assignment = get_object_or_404(Assignment, assignment_id=assignment_id)
    assignment.delete()
    messages.success(request, "Assignment deleted successfully.")
    return redirect(reverse("instructor_dashboard") + '?show_manage_assignments=true')

def submit_assignment(request, assignment_id):
    # Get the current student from request
    if "user_id" not in request.session:
        return redirect("login")
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
            submitted_answer=zip_file,  # Storing the uploaded file
            submission_status='Submitted',  # Status will be Pending initially
            review_status='Not Graded'  # Set as Not Graded initially
        )
        submission.save()
        course_id = assignment.course.course_id
        messages.success(request, "Assignment submitted successfully!")

        return redirect('course_dashboard', course_id=course_id)

    return HttpResponse("Invalid request", status=400)

def grade_assignment(request):
    # Fetch all submissions that are 'Not Graded'
    submissions = AssignmentSubmission.objects.filter(review_status="Not Graded")

    if request.method == 'POST':
        submission_id = request.POST.get("submission_id")
        grade = request.POST.get("grade")

        try:
            submission = AssignmentSubmission.objects.get(submission_id=submission_id)
            submission.grade = grade
            submission.review_status = "Graded"
            submission.save()
            messages.success(request, f"Graded assignment for {submission.student.full_name} successfully!")
        except AssignmentSubmission.DoesNotExist:
            messages.error(request, "Submission not found!")

        return redirect('grade_assignment')  # Refresh the page after grading

    return render(request, 'users/grade_assignment.html', {"submissions": submissions})

def download_submission(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, submission_id=submission_id)

    print("Type of submitted_answer:", type(submission.submitted_answer))  # Debugging
    print("Value of submitted_answer:", submission.submitted_answer)
    if not submission.submitted_answer:
        return HttpResponse("File not found", status=404)

    # Ensure we get the actual file path
    file_path = submission.submitted_answer.path  # This should work if using FileField properly

    if not os.path.exists(file_path):
        return HttpResponse("File does not exist on the server", status=404)

    # Open and return the file response
    return FileResponse(open(file_path, "rb"), as_attachment=True, filename=os.path.basename(file_path))