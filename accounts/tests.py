from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import Driver, Trip, Profit
from django.contrib.auth.models import User
from datetime import date

# Create your tests here.

class ExportTripsTests(TestCase):

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Создаем тестового водителя 
        self.driver = Driver.objects.create(
            user=self.user,
            name='Test Driver',
            license_issue_date=date.today()  
        )

        # Создаем тестовые поездки 
        self.trip = MagicMock()  # Используем MagicMock для имитации объекта Trip
        self.trip.start_date = '2025-01-01'
        self.trip.route = MagicMock()  # Создаем mock для route
        self.trip.route.departure_city = 'Москва'
        self.trip.route.arrival_city = 'Санкт-Петербург'
        self.trip.client = MagicMock()  # Создаем mock для client
        self.trip.client.first_name = 'Иван'
        self.trip.client.last_name = 'Иванов'
        self.trip.cargo_weight = 100.0
        self.trip.rating = 5
        self.trip.feedback = 'Отличная поездка!'



    @patch('accounts.views.TripDriver.objects.filter')
    def test_export_trips_mock(self, mock_filter):
        # Настраиваем mock для возвращения тестовых данных
        mock_filter.return_value = [self.trip]

        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('export_trips')) #получаем ответ на запрос для экспорта 

        # Проверяем, что ответ имеет статус 200
        self.assertEqual(response.status_code, 200)
        # Проверяем, что ответ имеет правильный тип контента
        self.assertEqual(response['Content-Type'], 'text/csv')
        # Проверяем, что в ответе есть данные
        self.assertIn('Дата'.encode('utf-8'), response.content)  # Проверяем, что заголовок "Дата" присутствует

        # Убедитесь, что mock был вызван
        mock_filter.assert_called_once_with(driver=self.driver)

class CabinetViewTests(TestCase):

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Создаем тестового водителя с обязательным полем license_issue_date
        self.driver = Driver.objects.create(
            user=self.user,
            name='Test Driver',
            license_issue_date=date.today()  # Указываем дату выдачи прав
        )

    def test_cabinet_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('cabinet'))

        # Проверяем, что ответ имеет статус 200
        self.assertEqual(response.status_code, 200)

        # Проверяем, что на странице присутствует имя пользователя
        self.assertContains(response, 'testuser')

