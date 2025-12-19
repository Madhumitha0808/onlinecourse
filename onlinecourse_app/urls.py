from django.urls import path
from . import views

app_name = 'onlinecourse_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('course/<int:course_id>/', views.course_details, name='course_details'),
    path('course/<int:course_id>/exam/', views.take_exam, name='take_exam'),
    path('course/<int:course_id>/submit/', views.submit, name='submit'),  # TASK 5 & 6
    path('result/<int:submission_id>/', views.show_exam_result, name='show_exam_result'),  # TASK 5 & 6
    path('api/submission/<int:submission_id>/', views.get_submission_details, name='submission_details'),
]
