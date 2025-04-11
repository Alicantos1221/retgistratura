from django.urls import path
from .views import login_view, register, home, logout_view, cabinet, get_departments, get_doctors, create_appointment, cancel_appointment, complete_appointment
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('', home, name='home'),
    path('cabinet/', cabinet, name='cabinet'),
    path('get-departments/', get_departments, name='get_departments'),
    path('get-doctors/', get_doctors, name='get_doctors'),
    path('create-appointment/', create_appointment, name='create_appointment'),
    path('cancel-appointment/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
    path('complete-appointment/<int:appointment_id>/', complete_appointment, name='complete_appointment'),
    path('upload-photo/', views.upload_photo, name='upload_photo'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('get-schedule/', views.get_schedule, name='get_schedule'),
    path('get-doctor-stats/', views.get_doctor_stats, name='get_doctor_stats'),
    path('download-doctor-stats/', views.download_doctor_stats, name='download_doctor_stats'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)