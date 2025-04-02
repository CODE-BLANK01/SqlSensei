
from django.urls import path
from .views import sql_query_view


urlpatterns = [
    path('query/', sql_query_view, name='sql_query'),
]