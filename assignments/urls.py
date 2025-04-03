
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('instructor/create-assignment/', views.create_assignment, name="create_assignment"),
    path("instructor/delete-assignment/<int:assignment_id>/", views.delete_assignment, name="delete_assignment"),
    path("student/submit-assignment/<int:assignment_id>/", views.submit_assignment, name='submit_assignment'),
    path("instructor/grade-assignment/", views.grade_assignment, name='grade_assignment'),
    path("instructor/download-submission/<int:submission_id>/", views.download_submission, name="download_submission"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)