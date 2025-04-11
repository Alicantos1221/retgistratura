from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class UserRole(models.TextChoices):
    PATIENT = 'PATIENT', 'Пациент'
    DOCTOR = 'DOCTOR', 'Врач'
    ADMIN = 'ADMIN', 'Администратор'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PATIENT,
        verbose_name='Роль пользователя'
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Department(models.Model):
    code = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Название отделения')
    description = models.TextField(verbose_name='Описание отделения', blank=True)
    floor = models.IntegerField(verbose_name='Этаж')
    room_number = models.CharField(max_length=10, verbose_name='Номер кабинета')

    class Meta:
        verbose_name = 'Отделение'
        verbose_name_plural = 'Отделения'

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor', null=True)
    code = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=100, verbose_name='Отчество', blank=True)
    specialization = models.CharField(max_length=100, verbose_name='Специализация')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Отделение')
    experience_years = models.IntegerField(verbose_name='Опыт работы (лет)')
    photo = models.ImageField(upload_to='doctors_photos/', null=True, blank=True, verbose_name='Фото')
    schedule = models.JSONField(verbose_name='Расписание приёмов', default=dict)

    class Meta:
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'

    def __str__(self):
        return f"Др. {self.last_name} {self.first_name}"

class Patient(models.Model):
    code = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=100, verbose_name='Отчество', blank=True)
    birth_date = models.DateField(verbose_name='Дата рождения')
    phone = models.CharField(max_length=15, verbose_name='Номер телефона')
    address = models.TextField(verbose_name='Адрес')
    medical_history = models.TextField(verbose_name='История болезни', blank=True)
    insurance_number = models.CharField(max_length=20, verbose_name='Номер страхового полиса')
    photo = models.ImageField(upload_to='patients_photos/', null=True, blank=True, verbose_name='Фото')

    class Meta:
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Запланирован'),
        ('COMPLETED', 'Завершён'),
        ('CANCELLED', 'Отменён'),
    ]

    code = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name='Пациент')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='Врач')
    date = models.DateField(verbose_name='Дата приёма')
    time = models.TimeField(verbose_name='Время приёма')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED', verbose_name='Статус')
    symptoms = models.TextField(verbose_name='Симптомы', blank=True)
    diagnosis = models.TextField(verbose_name='Диагноз', blank=True)
    prescription = models.TextField(verbose_name='Назначения', blank=True)
    notes = models.TextField(verbose_name='Заметки', blank=True)

    class Meta:
        verbose_name = 'Приём'
        verbose_name_plural = 'Приёмы'

    def __str__(self):
        return f"Приём {self.patient} у {self.doctor} {self.date}"

class MedicalService(models.Model):
    code = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Название услуги')
    description = models.TextField(verbose_name='Описание услуги')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Отделение')

    class Meta:
        verbose_name = 'Медицинская услуга'
        verbose_name_plural = 'Медицинские услуги'

    def __str__(self):
        return self.name

class AppointmentService(models.Model):
    code = models.AutoField(primary_key=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, verbose_name='Приём')
    service = models.ForeignKey(MedicalService, on_delete=models.CASCADE, verbose_name='Услуга')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')

    class Meta:
        verbose_name = 'Услуга приёма'
        verbose_name_plural = 'Услуги приёма'

    def __str__(self):
        return f"Услуга {self.service} для приёма {self.appointment.code}"

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('PENDING', 'Ожидает оплаты'),
        ('COMPLETED', 'Оплачено'),
        ('CANCELLED', 'Отменено'),
    ]

    code = models.AutoField(primary_key=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, verbose_name='Приём')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    date = models.DateField(verbose_name='Дата платежа')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING', verbose_name='Статус')
    payment_method = models.CharField(max_length=50, verbose_name='Способ оплаты')

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f"Платёж {self.amount} за приём {self.appointment.code}"