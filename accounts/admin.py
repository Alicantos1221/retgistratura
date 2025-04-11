from django.contrib import admin
from .models import (
    Department, Doctor, Patient, Appointment, 
    MedicalService, AppointmentService, Payment, UserProfile
)
from django.utils.html import format_html

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'floor', 'room_number')
    search_fields = ('name',)
    list_filter = ('floor',)
    ordering = ('name',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'specialization', 'department', 'experience_years')
    list_filter = ('department', 'specialization')
    search_fields = ('last_name', 'first_name', 'specialization')
    ordering = ('last_name', 'first_name')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'birth_date', 'phone', 'insurance_number')
    search_fields = ('last_name', 'first_name', 'insurance_number', 'phone')
    list_filter = ('birth_date',)
    ordering = ('last_name', 'first_name')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'patient', 'doctor', 'date', 'time', 'status')
    list_filter = ('status', 'date', 'doctor__department')
    search_fields = ('patient__last_name', 'patient__first_name', 'doctor__last_name')
    ordering = ('-date', '-time')

@admin.register(MedicalService)
class MedicalServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'price')
    list_filter = ('department',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(AppointmentService)
class AppointmentServiceAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'service', 'price')
    list_filter = ('service__department',)
    search_fields = ('appointment__patient__last_name', 'service__name')
    ordering = ('-appointment__date',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('code', 'appointment', 'amount', 'date', 'status', 'payment_method')
    list_filter = ('status', 'date', 'payment_method')
    search_fields = ('appointment__patient__last_name', 'appointment__doctor__last_name')
    ordering = ('-date',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']
