from django.urls import path
from . import views

urlpatterns = [
    path("instructor/create-question/", views.create_question, name="create_question"),
    path("instructor/view-instructor-question/", views.view_instructor_questions, name="view_instructor_questions"),
    path("instructor/delete-question/<int:question_id>/", views.delete_question, name="delete_question"),
    path("student/attempt/<int:question_id>/", views.attempt_question, name="attempt_question"),
    path("student/", views.all_questions, name="all_questions"),
    path("evaluate_query/", views.evaluate_query, name="evaluate_query"),
]