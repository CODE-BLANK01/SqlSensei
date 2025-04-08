from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import QuestionForm
from users.models import User
from .models import Question, QuestionAttempt
from django.http import JsonResponse
import openai, os
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.db import connection

# Handles form submission and saves a new question authored by the instructor to the database. Uses Dynamic SQL
@login_required(login_url='/users/login/')
def create_question(request):
    if request.method == "POST":
        question_title = request.POST.get("question_title")
        topic = request.POST.get("topic")
        difficulty_level = request.POST.get("difficulty_level")
        description = request.POST.get("description")
        access_type = request.POST.get("access_type")
        
        # New fields for LeetCode-like experience
        schema_sql = request.POST.get("schema_sql")
        sample_data_sql = request.POST.get("sample_data_sql")
        expected_output = request.POST.get("expected_output")
        
        # Get user_id from session and fetch the instructor (creator)
        user_id = request.session.get("user_id")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id
                FROM Users
                WHERE user_id = %s
                """, [user_id])
            created_by = cursor.fetchone()
            if created_by:
                # Insert into Question table with new fields
                cursor.execute("""
                    INSERT INTO Questions (
                        question_title, topic, difficulty_level, description,
                        schema_sql, sample_data_sql, expected_output, 
                        access_type, instructor_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        question_title, topic, difficulty_level, description,
                        schema_sql, sample_data_sql, expected_output, 
                        access_type, user_id
                    ])
                messages.success(request, "SQL Challenge created successfully.")
                return redirect(reverse("view_instructor_questions") + "?show_manage_questions=true")
            else:
                messages.error(request, "Instructor not found.")
                return redirect(reverse("view_instructor_questions") + "?show_manage_questions=true")
    else:
        form = QuestionForm()

# Deletes a question entry from the database using the dynamically selected question_id from GUI. Uses Dynamic SQL
@login_required(login_url='/users/login/')
def delete_question(request, question_id):
    with connection.cursor() as cursor:
        # Delete the question from the Question table based on the question_id
        cursor.execute("""
            DELETE FROM Questions 
            WHERE question_id = %s
        """, [question_id])
        
    messages.success(request, "Question deleted successfully.")
    return redirect(reverse('view_instructor_questions') + '?show_manage_questions=true')


# Retrieves a specific question from the database that was dynamically selected from GUI to display for student attempt
@login_required(login_url='/users/login/')
def attempt_question(request, question_id):
    source = request.GET.get('source', '')
    question = get_object_or_404(Question, question_id=question_id)
    if source == 'assignment':
        return render(request, "users/attempt_question_simplified.html", {"question": question})
    else:
        return render(request, "users/attempt_question.html", {"question": question})

# Fetches all public questions from the database to show on the all-questions page. Uses Dynamic SQL
@login_required(login_url='/users/login/')
def all_questions(request):
    with connection.cursor() as cursor:
        # Fetch all questions where access_type is 'Public'
        cursor.execute("""
            SELECT question_id, question_title, topic, difficulty_level, description, access_type
            FROM Questions
            WHERE access_type = %s
        """, ['Public'])

        rows = cursor.fetchall()

        # Create a list of dictionaries for the questions
        questions = [{
            'question_id': row[0],
            'question_title': row[1],
            'topic': row[2],
            'difficulty_level': row[3],
            'description': row[4],
            'access_type': row[5]
        } for row in rows]

    return render(request, "users/all_questions.html", {"questions": questions})


# Evaluates a dynamically selected question with student's query using OpenAI against the questions description and stores feedback and attempt details in the database
@csrf_exempt
def evaluate_query(request):
    print("Received request at /users/evaluate_query/")  # Debugging step 1
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Request body:", data)  # Debugging step 2
            
            question_id = data.get("question_id")
            student_query = data.get("query")

            if not question_id or not student_query:
                print("Error: Missing question_id or query")  # Debugging step 3
                return JsonResponse({"error": "Missing question_id or query"}, status=400)

            # Get the question description
            question = get_object_or_404(Question, question_id=question_id)
            print("Retrieved question:", question.description)  # Debugging step 4

            # Create a prompt for OpenAI
            prompt = f"""
            Given the SQL question description:
            "{question.description}"

            The student wrote this SQL query:
            "{student_query}"

            Provide constructive feedback on the correctness of the query, highlight any errors, and suggest improvements. First word should be correct or incorrect.
            """

            print("Generated OpenAI prompt:\n", prompt)  # Debugging step 5

            # Use OpenAI Client to send the request
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )

            print("OpenAI response received.")  # Debugging step 6

            feedback = response.choices[0].message.content
            attempt_success = feedback.startswith("Correct")
            print("Extracted feedback:", feedback)  # Debugging step 7

            # Save attempt in the database
            user_id = request.session.get("user_id")
            student = User.objects.get(user_id=user_id)
            question_attempt = QuestionAttempt.objects.create(
                student=student,
                question=question,
                attempt_date=now(),
                attempt_number=1,
                student_query=student_query,
                feedback=feedback,
                attempt_success=attempt_success
            )

            return JsonResponse({"feedback": feedback})

        except json.JSONDecodeError:
            print("Error: Invalid JSON format")  # Debugging step 8
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except openai.OpenAIError as e:
            print(f"OpenAI API Error: {str(e)}")  # Debugging step 9
            return JsonResponse({"error": f"OpenAI API error: {str(e)}"}, status=500)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # Debugging step 10
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    print("Error: Invalid request method")  # Debugging step 11
    return JsonResponse({"error": "Invalid request method"}, status=405)

# Displays a list of questions, filtered by difficulty level, access type based on dynamically selected query parameters.
# Uses Dynamic SQL
def question_list(request):
    # Get query parameters for filtering
    difficulty = request.GET.get('difficulty_level', None)
    access_type = request.GET.get('access_type', None)

    # Base query for fetching questions
    query = """
        SELECT question_id, question_title, topic, difficulty_level, description, access_type
        FROM Question
        WHERE 1=1
    """
    # List to hold parameters for the query
    params = []

    # Apply filters based on the query parameters if they exist
    if difficulty:
        query += " AND difficulty_level = %s"
        params.append(difficulty)
    
    if access_type:
        query += " AND access_type = %s"
        params.append(access_type)

    # Execute the query with the appropriate parameters
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Create a list of dictionaries for the questions
        questions = [{
            'question_id': row[0],
            'question_title': row[1],
            'topic': row[2],
            'difficulty_level': row[3],
            'description': row[4],
            'access_type': row[5]
        } for row in rows]

    # Pass the filtered questions to the template
    return render(request, "users/all_questions.html", {"questions": questions})

# Fetch the questions created by the logged in instructor user and display it to them. Uses Dynamic SQL
@login_required(login_url='/users/login/')
def view_instructor_questions(request):
    user_id = request.session.get("user_id")
   
    # Fetch all courses data using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT question_id, question_title, topic, difficulty_level,
                   description, instructor_id, created_date, access_type
            FROM Questions
            WHERE instructor_id = %s
        """, [user_id])

        rows = cursor.fetchall()

        # Convert to list of dictionaries
        questions = [{
            'question_id': row[0],
            'question_title': row[1],
            'topic': row[2],
            'difficulty_level': row[3],
            'description': row[4],
            'instructor_id': row[5],
            'created_date': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None,
            'access_type': row[7]
        } for row in rows]

    # Save the courses data to session
    request.session['questions'] = questions
    
    # Redirect to the appropriate dashboard with courses data
    return redirect(reverse("instructor_dashboard") + '?show_manage_questions=true')