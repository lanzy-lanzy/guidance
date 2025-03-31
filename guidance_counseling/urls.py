"""guidance_counseling URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import counselor_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('counselor/student/<int:student_id>/print/', counselor_views.print_student_info, name='print_student_info'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
