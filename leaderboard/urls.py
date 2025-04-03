from django.urls import path
from . import views

urlpatterns = [
    path("student/leaderboard/", views.view_leaderboard, name="view_leaderboard"),
]