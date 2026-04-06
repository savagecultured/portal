from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationTest(TestCase):
    def test_registration_form_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_registration_creates_user(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone': '+263771234567',
            'date_of_birth': '1990-01-01',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, 'test@example.com')
