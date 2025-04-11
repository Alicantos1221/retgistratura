from django.urls import path
from .views import login_view, register, home, logout_view, cabinet, get_departments, get_doctors, create_appointment, cancel_appointment, complete_appointment
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('cabinet/', views.cabinet, name='cabinet'),
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
    
    # Административные маршруты
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/departments/', views.admin_departments, name='admin_departments'),
    path('admin/departments/<int:department_id>/delete/', views.admin_delete_department, name='admin_delete_department'),
    path('admin/departments/<int:department_id>/edit/', views.admin_edit_department, name='admin_edit_department'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)