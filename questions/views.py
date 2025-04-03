from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import QuestionForm
from users.models import User
from .models import Question, QuestionAttempt
from django.http import JsonResponse, HttpResponse
import openai, os
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.timezone import now

# Create your views here.
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

def attempt_question(request, question_id):
    if "user_id" not in request.session:
        return redirect("login")

    question = get_object_or_404(Question, question_id=question_id)
    return render(request, "users/attempt_question.html", {"question": question})

def all_questions(request):
    if "user_id" not in request.session:
        return redirect("login")

    questions = Question.objects.filter(access_type="Public")

    return render(request, "users/all_questions.html", {"questions": questions})



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