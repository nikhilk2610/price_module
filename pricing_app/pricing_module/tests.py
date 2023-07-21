from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import PricingConfig


class PricingConfigAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_create_pricing_config(self):
        url = reverse('pricing_module:price_config_list_create')
        data = {
            'distance_base_price': 10.00,
            'base_distance': 5.0,
            'day': 1,
            'distance_additional_price': 32.50,
            'time_multiplier_factor': '1.25,1.5,2.0',
            'waiting_charges': 4.0,
            'waiting_time_threshold': 5,
            'is_active': True,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PricingConfig.objects.get().day, 1)
        self.assertEqual(PricingConfig.objects.get().distance_base_price, 10.00)

    def test_get_pricing_config_list(self):
        url = reverse('pricing_module:price_config_list_create')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), PricingConfig.objects.count())


class CalculatePricingAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.active_config = PricingConfig.objects.create(
            distance_base_price=80.00,
            base_distance=3.0,
            day=1,
            distance_additional_price=30.00,
            time_multiplier_factor='1.0,1.5',
            waiting_charges=5.0,
            waiting_time_threshold=3,
            is_active=True,
        )

    def test_calculate_pricing(self):
        url = reverse('pricing_module:calculate_price')
        data = {
            'distance_traveled': 20,
            "distance_traveled_each_hour": "10,10",
            'time_duration': 10,
            'date': '',
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid request. Date is required.')

