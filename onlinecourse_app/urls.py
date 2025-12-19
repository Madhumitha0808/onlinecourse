from django.urls import path
from . import views

app_name = 'onlinecourse_app'

urlpatterns = [
    # We'll add actual paths in Task 5 & 6
    path('', views.index, name='index'),
]