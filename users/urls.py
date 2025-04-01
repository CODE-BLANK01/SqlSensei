# users/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("welcome/", views.welcome_view, name="welcome"),

    path("instructor/dashboard/", views.instructor_dashboard, name="instructor_dashboard"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),

    path("instructor/create-course/", views.create_course, name="create_course"),
    path("instructor/create-assignment/", views.create_assignment, name="create_assignment"),
    path("instructor/create-question/", views.create_question, name="create_question"),
    path("instructor/delete-course/<int:course_id>/", views.delete_course, name="delete_course"),
    path("instructor/delete-assignment/<int:assignment_id>/", views.delete_assignment, name="delete_assignment"),
    path('course-enrollment/', include('courses.urls')),
    path("instructor/delete-question/<int:question_id>/", views.delete_question, name="delete_question"),
    path("instructor/approve-student/<int:enrollment_id>/", views.approve_student, name="approve_student"),
    path("instructor/deny-student/<int:enrollment_id>/", views.deny_student, name="deny_student"),
    path("instructor/student-approvals/", views.student_approvals, name='student_approvals'),
    path('instructor/get-questions/<int:assignment_id>/', views.get_assignment_questions, name='get_assignment_questions'),
]
