from django.contrib import admin
from .models import Course, Lesson, Question, Choice, Submission, Instructor, Learner

# Register your models here.

# ChoiceInline class - TASK 2 REQUIREMENT
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 3  # Show 3 empty choice fields by default
    max_num = 5  # Maximum 5 choices per question
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset

# QuestionInline class - TASK 2 REQUIREMENT
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1  # Show 1 empty question field by default
    show_change_link = True  # Allow editing questions directly
    fields = ['question_text', 'grade']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('lesson')

# QuestionAdmin class - TASK 2 REQUIREMENT
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'lesson', 'grade', 'get_course_name']
    list_filter = ['lesson', 'grade']
    search_fields = ['question_text', 'lesson__title']
    inlines = [ChoiceInline]  # Include ChoiceInline
    
    # Custom method to get course name
    def get_course_name(self, obj):
        return obj.lesson.course.name
    get_course_name.short_description = 'Course'
    get_course_name.admin_order_field = 'lesson__course__name'
    
    # Customize the form
    fieldsets = [
        (None, {'fields': ['lesson', 'question_text']}),
        ('Grading', {'fields': ['grade'], 'classes': ['collapse']}),
    ]
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('lesson__course')

# LessonAdmin class - TASK 2 REQUIREMENT
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'get_question_count']
    list_filter = ['course']
    search_fields = ['title', 'content', 'course__name']
    inlines = [QuestionInline]  # Include QuestionInline
    
    # Custom method to count questions
    def get_question_count(self, obj):
        return obj.question_set.count()
    get_question_count.short_description = 'Questions'
    
    # Customize the form
    fieldsets = [
        (None, {'fields': ['course', 'title']}),
        ('Content', {'fields': ['content'], 'classes': ['wide']}),
    ]
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('course')

# CourseAdmin class (not required but helpful)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'description_short']
    search_fields = ['name', 'description']
    
    def description_short(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_short.short_description = 'Description'

# SubmissionAdmin class (not required but helpful)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'score', 'submitted_at']
    list_filter = ['lesson', 'submitted_at', 'score']
    search_fields = ['user__username', 'lesson__title']
    readonly_fields = ['submitted_at']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'lesson__course')

# Register all models with admin site
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission, SubmissionAdmin)

# Note: Instructor and Learner models are imported but not registered
# as they might be custom user models. If you need to register them:
# admin.site.register(Instructor)
# admin.site.register(Learner)