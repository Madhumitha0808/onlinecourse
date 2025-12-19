from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import Course, Lesson, Question, Choice, Submission
from django.contrib.auth.models import User
import json
from datetime import datetime

# Home page view
def index(request):
    """Display all available courses"""
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'user': request.user,
    }
    return render(request, 'onlinecourse_app/index.html', context)

# Course details view
def course_details(request, course_id):
    """Display course details with all lessons"""
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course).order_by('id')
    
    context = {
        'course': course,
        'lessons': lessons,
        'user': request.user,
    }
    return render(request, 'onlinecourse_app/course_details_bootstrap.html', context)

# TASK 5 REQUIREMENT: submit function
def submit(request, course_id):
    """
    Handle exam submission
    This function processes submitted exam answers and calculates the score
    """
    if request.method == 'POST':
        try:
            # Get the course
            course = get_object_or_404(Course, id=course_id)
            
            # Get all questions for this course
            lessons = Lesson.objects.filter(course=course)
            questions = Question.objects.filter(lesson__in=lessons)
            
            # Initialize scoring variables
            total_questions = questions.count()
            correct_answers = 0
            submission_data = []
            
            # Process each question
            for question in questions:
                # Get selected choice ID from POST data
                selected_choice_id = request.POST.get(f'question_{question.id}')
                
                if selected_choice_id:
                    try:
                        selected_choice = Choice.objects.get(id=selected_choice_id)
                        is_correct = selected_choice.is_correct
                        
                        # Find correct choices for this question
                        correct_choices = Choice.objects.filter(question=question, is_correct=True)
                        correct_choice_ids = [str(c.id) for c in correct_choices]
                        
                        # Check if answer is correct
                        if is_correct:
                            correct_answers += 1
                            status = "Correct"
                        else:
                            status = "Incorrect"
                            
                        # Record submission data
                        submission_data.append({
                            'question_id': question.id,
                            'question_text': question.question_text[:100] + "..." if len(question.question_text) > 100 else question.question_text,
                            'selected_choice': selected_choice.choice_text,
                            'correct_choice': correct_choices.first().choice_text if correct_choices.exists() else "No correct choice",
                            'is_correct': is_correct,
                            'status': status,
                            'grade': question.grade
                        })
                        
                    except Choice.DoesNotExist:
                        # Selected choice doesn't exist
                        submission_data.append({
                            'question_id': question.id,
                            'question_text': question.question_text[:100] + "..." if len(question.question_text) > 100 else question.question_text,
                            'selected_choice': "No selection",
                            'correct_choice': "N/A",
                            'is_correct': False,
                            'status': "Not answered",
                            'grade': 0
                        })
                else:
                    # No answer submitted for this question
                    submission_data.append({
                        'question_id': question.id,
                        'question_text': question.question_text[:100] + "..." if len(question.question_text) > 100 else question.question_text,
                        'selected_choice': "No selection",
                        'correct_choice': "N/A",
                        'is_correct': False,
                        'status': "Not answered",
                        'grade': 0
                    })
            
            # Calculate score percentage
            score_percentage = 0
            if total_questions > 0:
                score_percentage = (correct_answers / total_questions) * 100
            
            # Determine if passed (70% or higher)
            passed = score_percentage >= 70
            
            # Create submission record
            submission = Submission.objects.create(
                user=request.user if request.user.is_authenticated else None,
                lesson=lessons.first() if lessons.exists() else None,
                score=score_percentage,
            )
            
            # Add selected choices to submission
            for question in questions:
                selected_choice_id = request.POST.get(f'question_{question.id}')
                if selected_choice_id:
                    try:
                        selected_choice = Choice.objects.get(id=selected_choice_id)
                        submission.choices.add(selected_choice)
                    except Choice.DoesNotExist:
                        pass
            
            # Save the submission
            submission.save()
            
            # Store submission data in session for result page
            request.session['submission_data'] = submission_data
            request.session['total_questions'] = total_questions
            request.session['correct_answers'] = correct_answers
            request.session['score_percentage'] = score_percentage
            request.session['passed'] = passed
            
            # Redirect to result page
            return redirect('onlinecourse_app:show_exam_result', submission_id=submission.id)
            
        except Exception as e:
            # Handle any errors during submission
            messages.error(request, f'Error processing submission: {str(e)}')
            return redirect('onlinecourse_app:course_details', course_id=course_id)
    
    else:
        # If not POST request, redirect to course details
        return redirect('onlinecourse_app:course_details', course_id=course_id)

# TASK 5 REQUIREMENT: show_exam_result function
def show_exam_result(request, submission_id):
    """
    Display exam results
    This function shows the detailed results of an exam submission
    """
    try:
        # Get the submission
        submission = get_object_or_404(Submission, id=submission_id)
        
        # Get data from session or calculate fresh
        submission_data = request.session.get('submission_data', [])
        total_questions = request.session.get('total_questions', 0)
        correct_answers = request.session.get('correct_answers', 0)
        score_percentage = request.session.get('score_percentage', submission.score)
        passed = request.session.get('passed', submission.score >= 70)
        
        # If no session data, calculate from submission
        if not submission_data:
            # Get all choices in this submission
            selected_choices = submission.choices.all()
            
            # Get questions from selected choices
            questions = Question.objects.filter(choice__in=selected_choices).distinct()
            
            # Build submission data
            for question in questions:
                # Get user's selected choice for this question
                user_choice = selected_choices.filter(question=question).first()
                correct_choice = Choice.objects.filter(question=question, is_correct=True).first()
                
                submission_data.append({
                    'question_id': question.id,
                    'question_text': question.question_text[:100] + "..." if len(question.question_text) > 100 else question.question_text,
                    'selected_choice': user_choice.choice_text if user_choice else "No selection",
                    'correct_choice': correct_choice.choice_text if correct_choice else "N/A",
                    'is_correct': user_choice.is_correct if user_choice else False,
                    'status': "Correct" if user_choice and user_choice.is_correct else "Incorrect",
                    'grade': question.grade
                })
            
            total_questions = questions.count()
            correct_answers = len([item for item in submission_data if item['is_correct']])
        
        # Get course information
        course = None
        if submission.lesson:
            course = submission.lesson.course
        
        # Prepare context for template
        context = {
            'submission': submission,
            'course': course,
            'submission_data': submission_data,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score': score_percentage,
            'passed': passed,
            'completion_date': submission.submitted_at.strftime('%B %d, %Y at %I:%M %p'),
            'user': request.user,
        }
        
        # Clear session data
        if 'submission_data' in request.session:
            del request.session['submission_data']
        
        return render(request, 'onlinecourse_app/exam_result.html', context)
        
    except Submission.DoesNotExist:
        messages.error(request, 'Submission not found.')
        return redirect('onlinecourse_app:index')
    except Exception as e:
        messages.error(request, f'Error loading results: {str(e)}')
        return redirect('onlinecourse_app:index')

# Additional helper view for exam page
def take_exam(request, course_id):
    """Display exam questions for a course"""
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course)
    questions = Question.objects.filter(lesson__in=lessons).order_by('id')
    
    # Prepare questions with choices
    exam_questions = []
    for question in questions:
        choices = Choice.objects.filter(question=question).order_by('?')  # Randomize choices
        exam_questions.append({
            'question': question,
            'choices': choices,
        })
    
    context = {
        'course': course,
        'exam_questions': exam_questions,
        'total_questions': questions.count(),
        'user': request.user,
    }
    
    return render(request, 'onlinecourse_app/exam.html', context)

# API view to get submission details (optional)
def get_submission_details(request, submission_id):
    """API endpoint to get submission details in JSON format"""
    if request.method == 'GET':
        try:
            submission = Submission.objects.get(id=submission_id)
            data = {
                'id': submission.id,
                'user': submission.user.username if submission.user else 'Anonymous',
                'score': submission.score,
                'passed': submission.score >= 70,
                'submitted_at': submission.submitted_at.isoformat(),
                'course': submission.lesson.course.name if submission.lesson and submission.lesson.course else 'N/A',
            }
            return JsonResponse(data)
        except Submission.DoesNotExist:
            return JsonResponse({'error': 'Submission not found'}, status=404)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
