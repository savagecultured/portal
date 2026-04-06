from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Token, TokenPurchase

User = get_user_model()


class TokenPurchaseTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_token_purchase_creates_tokens(self):
        initial_count = Token.objects.filter(user=self.user).count()
        purchase = TokenPurchase.objects.create(
            user=self.user,
            quantity=3,
            amount=1.50
        )
        purchase.fulfil()
        self.assertEqual(
            Token.objects.filter(user=self.user).count(),
            initial_count + 3
        )
        self.assertEqual(purchase.status, 'completed')