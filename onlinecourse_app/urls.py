from django.urls import path
from . import views

app_name = 'onlinecourse_app'

urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    
    # Course details page
    path('course/<int:course_id>/', views.course_details, name='course_details'),
    
    # Exam page
    path('course/<int:course_id>/exam/', views.take_exam, name='take_exam'),
    
    # TASK 6 REQUIREMENT: submit path
    path('course/<int:course_id>/submit/', views.submit, name='submit'),
    
    # TASK 6 REQUIREMENT: show_exam_result path
    path('result/<int:submission_id>/', views.show_exam_result, name='show_exam_result'),
    
    # Optional: API endpoint for submission details
    path('api/submission/<int:submission_id>/', views.get_submission_details, name='submission_details'),
]

# URL Pattern Explanations:
# 1. path('course/<int:course_id>/submit/', views.submit, name='submit')
#    - URL pattern for submitting exams
#    - <int:course_id>: Captures course ID as integer
#    - Points to views.submit function
#    - Named 'submit' for reverse URL lookups
#
# 2. path('result/<int:submission_id>/', views.show_exam_result, name='show_exam_result')
#    - URL pattern for displaying exam results
#    - <int:submission_id>: Captures submission ID as integer
#    - Points to views.show_exam_result function
#    - Named 'show_exam_result' for reverse URL lookups
