# users/urls.py
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("instructor/dashboard/", views.instructor_dashboard, name="instructor_dashboard"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path('course-enrollment/', include('courses.urls')),
    path('instructor/get-questions/<int:assignment_id>/', views.get_assignment_questions, name='get_assignment_questions'),
    path("student/messages/send/", views.send_message, name="send_message"),
    path("send-code/", views.send_verification_code, name="send_verification_code")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)