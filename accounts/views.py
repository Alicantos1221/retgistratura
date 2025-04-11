from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Q, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import (
    UserProfile, UserRole, Doctor, Patient, Department, Appointment, 
    MedicalService, AppointmentService, Payment
)
import random
import json
from datetime import date, datetime, timedelta
from collections import defaultdict
from django.utils import timezone
import csv
from decimal import Decimal
from .forms import PatientPhotoForm, DoctorPhotoForm

def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    departments = Department.objects.all()
    today = date.today()
    return render(request, 'home.html', {
        'departments': departments,
        'today': today
    })

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')
        
        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return redirect('register')
        
        user = User.objects.create_user(username=username, password=password1)
        
        if role == 'PATIENT':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            middle_name = request.POST.get('middle_name')
            birth_date = request.POST.get('birth_date')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            insurance_number = request.POST.get('insurance_number')
            
            patient = Patient.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                birth_date=birth_date,
                phone=phone,
                address=address,
                insurance_number=insurance_number
            )
            
            UserProfile.objects.create(user=user, role=UserRole.PATIENT)
            messages.success(request, 'Регистрация успешна! Теперь вы можете войти в систему.')
            return redirect('login')
            
        elif role == 'DOCTOR':
            first_name = request.POST.get('doctor_first_name')
            last_name = request.POST.get('doctor_last_name')
            middle_name = request.POST.get('doctor_middle_name')
            specialization = request.POST.get('specialization')
            experience_years = request.POST.get('experience_years')
            department_code = request.POST.get('department')
            
            try:
                department = Department.objects.get(code=department_code)
                doctor = Doctor.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    middle_name=middle_name,
                    specialization=specialization,
                    experience_years=experience_years,
                    department=department
                )
                
                UserProfile.objects.create(user=user, role=UserRole.DOCTOR)
                messages.success(request, 'Регистрация успешна! Теперь вы можете войти в систему.')
                return redirect('login')
            except Department.DoesNotExist:
                messages.error(request, 'Выбранное отделение не существует')
                return redirect('register')
    
    departments = Department.objects.all().order_by('name')
    return render(request, 'register.html', {'departments': departments})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('cabinet')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'login.html')

@login_required
def cabinet(request):
    profile = UserProfile.objects.get(user=request.user)
    
    if profile.role == UserRole.PATIENT:
        patient = Patient.objects.get(user=request.user)
        appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-time')
        return render(request, 'cabinet/patient.html', {'patient': patient, 'appointments': appointments})
    
    elif profile.role == UserRole.DOCTOR:
        doctor = Doctor.objects.get(user=request.user)
        appointments = Appointment.objects.filter(doctor=doctor).order_by('-date', '-time')
        return render(request, 'cabinet/doctor.html', {'doctor': doctor, 'appointments': appointments})
    
    elif profile.role == UserRole.ADMIN:
        departments_count = Department.objects.count()
        doctors_count = Doctor.objects.count()
        patients_count = Patient.objects.count()
        appointments_count = Appointment.objects.count()
        services_count = MedicalService.objects.count()
        payments_count = Payment.objects.count()
        
        return render(request, 'cabinet/admin.html', {
            'departments_count': departments_count,
            'doctors_count': doctors_count,
            'patients_count': patients_count,
            'appointments_count': appointments_count,
            'services_count': services_count,
            'payments_count': payments_count
        })
    
    return redirect('home')

@csrf_exempt
def get_departments(request):
    departments = Department.objects.all()
    data = [{'id': dept.id, 'name': dept.name} for dept in departments]
    return JsonResponse(data, safe=False)

@csrf_exempt
def get_doctors(request):
    department_code = request.GET.get('department_id')
    if department_code:
        doctors = Doctor.objects.filter(department__code=department_code)
    else:
        doctors = Doctor.objects.all()
    
    data = [{
        'id': doc.code,
        'name': f"{doc.last_name} {doc.first_name} {doc.middle_name or ''}",
        'specialization': doc.specialization
    } for doc in doctors]
    return JsonResponse({'doctors': data}, safe=False)

@csrf_exempt
def create_appointment(request):
    if request.method == 'POST':
        try:
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'Необходимо войти в систему'})

            data = json.loads(request.body)
            doctor_id = data.get('doctor_id')
            date_str = data.get('date')
            time_str = data.get('time')
            symptoms = data.get('symptoms', '')
            
            try:
                patient = Patient.objects.get(user=request.user)
            except Patient.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Пользователь не является пациентом'})
            
            try:
                doctor = Doctor.objects.get(code=doctor_id)
            except Doctor.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Врач не найден'})
            
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            appointment_time = datetime.strptime(time_str, '%H:%M').time()
            
            # Проверяем, нет ли уже записи на это время
            if Appointment.objects.filter(
                doctor=doctor,
                date=appointment_date,
                time=appointment_time
            ).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'На это время уже есть запись'
                })
            
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=appointment_date,
                time=appointment_time,
                symptoms=symptoms,
                status='SCHEDULED'
            )
            
            return JsonResponse({
                'success': True,
                'appointment_id': appointment.code
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Неверный формат данных'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Метод не поддерживается'
    })

@login_required
def cancel_appointment(request, appointment_id):
    try:
        appointment = Appointment.objects.get(code=appointment_id)
        profile = UserProfile.objects.get(user=request.user)
        
        # Проверяем, имеет ли пользователь право отменять эту запись
        if profile.role == UserRole.PATIENT and appointment.patient.user != request.user:
            raise PermissionDenied
        elif profile.role == UserRole.DOCTOR and appointment.doctor.user != request.user:
            raise PermissionDenied
        
        appointment.status = 'CANCELLED'
        appointment.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def complete_appointment(request, appointment_id):
    try:
        appointment = Appointment.objects.get(code=appointment_id)
        profile = UserProfile.objects.get(user=request.user)
        
        # Проверяем, имеет ли пользователь право завершать эту запись
        if profile.role != UserRole.DOCTOR or appointment.doctor.user != request.user:
            raise PermissionDenied
        
        data = json.loads(request.body)
        diagnosis = data.get('diagnosis')
        prescription = data.get('prescription')
        notes = data.get('notes')
        
        appointment.diagnosis = diagnosis
        appointment.prescription = prescription
        appointment.notes = notes
        appointment.status = 'COMPLETED'
        appointment.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def schedule_view(request):
    departments = Department.objects.all().order_by('name')
    doctors = Doctor.objects.all().order_by('user__last_name')
    return render(request, 'schedule.html', {
        'departments': departments,
        'doctors': doctors,
    })

@login_required
def get_schedule(request):
    department_id = request.GET.get('department')
    doctor_id = request.GET.get('doctor')
    date = request.GET.get('date')
    
    appointments = Appointment.objects.all()
    
    if department_id:
        appointments = appointments.filter(doctor__department_id=department_id)
    if doctor_id:
        appointments = appointments.filter(doctor_id=doctor_id)
    if date:
        appointments = appointments.filter(date=date)
        
    appointments = appointments.select_related('doctor', 'doctor__department', 'patient').order_by('date', 'time')
    
    schedule_data = []
    for appointment in appointments:
        schedule_data.append({
            'id': appointment.id,
            'time': appointment.time.strftime('%H:%M'),
            'doctor': f"{appointment.doctor.user.last_name} {appointment.doctor.user.first_name}",
            'department': appointment.doctor.department.name,
            'room': appointment.doctor.room_number,
            'patient': f"{appointment.patient.user.last_name} {appointment.patient.user.first_name}" if appointment.patient else "Свободно",
            'status': appointment.status,
            'can_cancel': appointment.status == 'SCHEDULED' and (
                request.user == appointment.patient.user or 
                request.user == appointment.doctor.user or 
                request.user.is_staff
            )
        })
    
    return JsonResponse({'schedule': schedule_data})

@login_required
def upload_photo(request):
    if request.method == 'POST':
        try:
            if hasattr(request.user, 'patient'):
                form = PatientPhotoForm(request.POST, request.FILES, instance=request.user.patient)
            elif hasattr(request.user, 'doctor'):
                form = DoctorPhotoForm(request.POST, request.FILES, instance=request.user.doctor)
            else:
                return JsonResponse({'success': False, 'error': 'Пользователь не найден'})

            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Ошибка при загрузке фото'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})

@login_required
def get_doctor_stats(request):
    if not hasattr(request.user, 'doctor'):
        return JsonResponse({'error': 'Пользователь не является врачом'}, status=403)
    
    doctor = request.user.doctor
    stats = Appointment.objects.filter(doctor=doctor).values('status').annotate(count=Count('status'))
    
    result = {
        'completed_count': 0,
        'cancelled_count': 0,
        'scheduled_count': 0
    }
    
    for stat in stats:
        if stat['status'] == 'COMPLETED':
            result['completed_count'] = stat['count']
        elif stat['status'] == 'CANCELLED':
            result['cancelled_count'] = stat['count']
        elif stat['status'] == 'SCHEDULED':
            result['scheduled_count'] = stat['count']
    
    return JsonResponse(result)

@login_required
def download_doctor_stats(request):
    if not hasattr(request.user, 'doctor'):
        return JsonResponse({'error': 'Пользователь не является врачом'}, status=403)
    
    doctor = request.user.doctor
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-date', '-time')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="appointments_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Дата', 'Время', 'Пациент', 'Статус', 'Диагноз', 'Назначения'])
    
    for appointment in appointments:
        writer.writerow([
            appointment.date.strftime('%d.%m.%Y'),
            appointment.time.strftime('%H:%M'),
            f"{appointment.patient.last_name} {appointment.patient.first_name}",
            appointment.get_status_display(),
            appointment.diagnosis or '',
            appointment.prescription or ''
        ])
    
    return response
