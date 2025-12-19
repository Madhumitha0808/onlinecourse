from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('onlinecourse_app.urls')),
]

# This configuration:
# 1. Includes Django admin at /admin/
# 2. Includes all onlinecourse_app URLs at the root level
# 3. Makes submit available at: /course/<id>/submit/
# 4. Makes show_exam_result available at: /result/<id>/
