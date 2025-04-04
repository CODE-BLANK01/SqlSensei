from django.shortcuts import render, redirect, get_object_or_404
from .models import Leaderboard
from users.models import User

def view_leaderboard(request):
    if "user_id" not in request.session:
        return redirect("login")
    # Fetch the leaderboard data along with the student name from the User table
    leaderboard_data = Leaderboard.objects.all().order_by('-problems_solved')
    
    # Enhance the leaderboard data with student names from the User table
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
    return redirect("/users/student/dashboard/?show_leaderboard=true")