from django.shortcuts import render, redirect, get_object_or_404
from .models import Leaderboard
from users.models import User
from django.contrib.auth.decorators import login_required
from django.db import connection

# Retrieves leaderboard entries and student names by joining Leaderboard and User models. Uses Dynamic SQL
@login_required(login_url='/users/login/')
def view_leaderboard(request):
    user_id = request.session.get("user_id")
    # Fetch user role (student or instructor)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT role 
            FROM Users 
            WHERE user_id = %s
        """, [user_id])
        user_role = cursor.fetchone()[0].lower()

    # Determine the redirect URL based on user role
    if user_role == "student":
        url = "/users/student/dashboard/?show_leaderboard=true"
    elif user_role == "instructor":
        url = "/users/instructor/dashboard/?show_leaderboard=true"

    # Fetch leaderboard data along with corresponding student names using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.full_name, l.problems_solved
            FROM Leaderboard l
            JOIN Users u ON l.student_id = u.user_id
            ORDER BY l.problems_solved DESC
        """)
        rows = cursor.fetchall()

    # Prepare the leaderboard data
    leaderboard_with_names = [{
        "student_name": row[0],  # Student name from Users table
        "problems_solved": row[1],  # Problems solved from Leaderboard table
    } for row in rows]

    # Save the leaderboard data to session
    request.session['leaderboard_data'] = leaderboard_with_names
    
    # Redirect to the appropriate dashboard with leaderboard data
    return redirect(url)