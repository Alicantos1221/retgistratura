from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile, Doctor, Patient, Appointment, UserRole, Department
from datetime import datetime, timedelta

class AppointmentTests(TestCase):
    def setUp(self):
        # Создаем тестовое отделение
        self.department = Department.objects.create(
            name='Терапевтическое отделение',
            description='Тестовое отделение',
            floor=1,
            room_number='101'
        )

        # Создаем тестового пользователя-пациента
        self.patient_user = User.objects.create_user(
            username='test_patient',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            last_name='Иванов',
            first_name='Иван',
            middle_name='Иванович',
            birth_date='1990-01-01',
            phone='+79991234567',
            address='ул. Тестовая, 1',
            insurance_number='1234567890123456'
        )

        # Создаем тестового пользователя-врача
        self.doctor_user = User.objects.create_user(
            username='test_doctor',
            password='testpass123'
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            last_name='Петров',
            first_name='Петр',
            middle_name='Петрович',
            specialization='Терапевт',
            department=self.department,
            experience_years=5
        )

    def test_create_appointment(self):
        """Тест создания записи на приём"""
        # Создаем запись на завтрашний день
        tomorrow = datetime.now().date() + timedelta(days=1)
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=tomorrow,
            time='10:00',
            symptoms='Головная боль, температура'
        )

        # Проверяем, что запись создана корректно
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.date, tomorrow)
        self.assertEqual(appointment.time, '10:00')
        self.assertEqual(appointment.symptoms, 'Головная боль, температура')
        self.assertEqual(appointment.status, 'SCHEDULED')

    def test_complete_appointment(self):
        """Тест завершения приёма врачом"""
        # Создаем запись
        tomorrow = datetime.now().date() + timedelta(days=1)
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=tomorrow,
            time='10:00',
            symptoms='Головная боль, температура'
        )

        # Завершаем приём
        appointment.status = 'COMPLETED'
        appointment.diagnosis = 'ОРВИ'
        appointment.prescription = 'Постельный режим, обильное питье'
        appointment.save()

        # Проверяем, что приём завершен корректно
        updated_appointment = Appointment.objects.get(code=appointment.code)
        self.assertEqual(updated_appointment.status, 'COMPLETED')
        self.assertEqual(updated_appointment.diagnosis, 'ОРВИ')
        self.assertEqual(updated_appointment.prescription, 'Постельный режим, обильное питье') 