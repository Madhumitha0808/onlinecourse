from django.shortcuts import render, redirect
from .models import Course, Lesson, Question, Choice, Submission
from django.contrib.auth.decorators import login_required

def submit(request, lesson_id):
    if request.method == 'POST':
        lesson = Lesson.objects.get(id=lesson_id)
        selected_choices = request.POST.getlist('choice')
        
        # Calculate score
        questions = Question.objects.filter(lesson=lesson)
        total = len(questions)
        correct = 0
        
        for question in questions:
            correct_choices = Choice.objects.filter(question=question, is_correct=True)
            correct_choice_ids = [str(c.id) for c in correct_choices]
            selected_for_q = [c for c in selected_choices if c in correct_choice_ids]
            
            if len(selected_for_q) == len(correct_choices):
                correct += 1
        
        score = (correct / total) * 100 if total > 0 else 0
        
        # Save submission
        submission = Submission.objects.create(
            user=request.user,
            lesson=lesson,
            score=score
        )
        
        return render(request, 'onlinecourse_app/result.html', {
            'score': score,
            'correct': correct,
            'total': total,
            'lesson': lesson
        })
    
    return redirect('/')

def show_exam_result(request, submission_id):
    submission = Submission.objects.get(id=submission_id)
    return render(request, 'onlinecourse_app/result.html', {
        'submission': submission,
        'score': submission.score
    })

# Create your views here.
