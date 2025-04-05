from django.shortcuts import render, redirect, get_object_or_404
from .models import Leaderboard
from users.models import User
from django.contrib.auth.decorators import login_required

# Retrieves leaderboard entries and student names by joining Leaderboard and User models
@login_required(login_url='/users/login/')
def view_leaderboard(request):
    # Fetch leaderboard data sorted by problems solved
    leaderboard_data = Leaderboard.objects.all().order_by('-problems_solved')
    user_id = request.session.get("user_id")
    user = User.objects.get(user_id = user_id)
    user_role = user.role.lower()

    if user_role == "student":
        url = "/users/student/dashboard/?show_leaderboard=true"
    elif user_role == "instructor":
        url = "/users/instructor/dashboard/?show_leaderboard=true"
    
    # For each leaderboard entry, fetch the corresponding student name from the User table
    leaderboard_with_names = []
    for entry in leaderboard_data:
        student = User.objects.get(user_id=entry.student_id)  # Assuming 'student_id' in Leaderboard matches 'user_id' in User table
        leaderboard_with_names.append({
            "student_name": student.full_name,  # Add student name from User table
            "problems_solved": entry.problems_solved,
        })
    
    # Save the leaderboard data with names to the session
    request.session['leaderboard_data'] = leaderboard_with_names
    
    # Redirect to the dashboard with leaderboard data
    return redirect(url)