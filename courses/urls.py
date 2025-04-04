from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.apply_for_course, name='apply_for_course'),
    path('instructor/create-course/', views.create_course, name="create_course"),
    path('instructor/delete-course/<int:course_id>/', views.delete_course, name="delete_course"),
    path("instructor/approve-student/<int:enrollment_id>/", views.approve_student, name="approve_student"),
    path("instructor/deny-student/<int:enrollment_id>/", views.deny_student, name="deny_student"),
    path("instructor/student-approvals/", views.student_approvals, name='student_approvals'),
    path("student/courses/", views.view_courses, name="view_courses"),
    path("student/course/<int:course_id>/", views.course_dashboard, name='course_dashboard'),
]