import hashlib
import hmac
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Token, TokenPurchase
from apps.analytics.models import Session
from .serializers import TokenSerializer, TokenPurchaseSerializer


@login_required
def activate_token(request, token_id):
    """Activate a token and create an analytics session."""
    token = get_object_or_404(Token, id=token_id, user=request.user, used=False)
    
    # Check for existing active tokens - only one token can be active at a time
    active_token = Token.objects.filter(
        user=request.user,
        used=True,
        expired=False,
        expires_at__gt=timezone.now()
    ).first()
    
    if active_token:
        messages.error(request, f'You already have an active token (expires {active_token.expires_at.strftime("%Y-%m-%d %H:%M")}). Please wait for it to expire before activating another.')
        return redirect('dashboard')
    
    ip = request.META.get('REMOTE_ADDR')
    token.activate(ip)
    # Create analytics session
    Session.objects.create(
        user=request.user,
        device=getattr(request, 'device', None),
        token=token,
        ip_address=ip
    )
    messages.success(request, 'Token activated successfully!')
    return redirect('dashboard')


def create_paynow_payment(user, quantity, amount):
    """Create a Paynow payment and return the redirect URL."""
    if not settings.PAYNOW_MERCHANT_ID or not settings.PAYNOW_INTEGRATION_KEY:
        return None
    
    # Generate unique reference
    reference = f'TOK-{uuid.uuid4().hex[:8].upper()}'
    
    # Prepare payment data
    payment_data = {
        'merchant_id': settings.PAYNOW_MERCHANT_ID,
        'amount': str(amount),
        'reference': reference,
        'narration': f'{quantity} WebMART Tokens for {user.email}',
        'return_url': settings.PAYNOW_URL + '/return/' + reference,
        'result_url': settings.PAYNOW_URL + '/result/' + reference,
    }
    
    # Generate hash (Paynow uses MD5 hash of concatenated fields)
    hash_string = (
        str(payment_data['merchant_id']) +
        str(payment_data['amount']) +
        str(payment_data['reference']) +
        settings.PAYNOW_INTEGRATION_KEY
    )
    payment_data['hash'] = hashlib.md5(hash_string.encode()).hexdigest()
    
    # Build redirect URL
    import urllib.parse
    query = urllib.parse.urlencode(payment_data)
    redirect_url = f'{settings.PAYNOW_URL}/checkout?{query}'
    
    return redirect_url, reference


@login_required
def buy_tokens(request):
    """Token purchase view with Paynow integration."""
    from django.conf import settings
    
    quantity = int(request.POST.get('quantity', 1))
    amount = quantity * settings.TOKEN_PRICE
    
    if request.method == 'POST':
        # Check if Paynow is configured
        if settings.PAYNOW_MERCHANT_ID and settings.PAYNOW_INTEGRATION_KEY:
            # Create Paynow payment
            result = create_paynow_payment(request.user, quantity, amount)
            if result:
                redirect_url, reference = result
                # Create pending purchase
                TokenPurchase.objects.create(
                    user=request.user,
                    quantity=quantity,
                    amount=amount,
                    status='pending',
                    reference=reference
                )
                return redirect(redirect_url)
        
        # No payment gateway - fulfil immediately (for testing)
        purchase = TokenPurchase.objects.create(
            user=request.user,
            quantity=quantity,
            amount=amount,
            status='completed'  # Auto-complete if no payment gateway
        )
        purchase.fulfil()
        messages.success(request, f'{quantity} tokens purchased successfully!')
        return redirect('dashboard')
    
    return render(request, 'tokens/buy.html', {
        'token_price': settings.TOKEN_PRICE
    })


@login_required
def payment_result(request, reference):
    """Handle Paynow payment result."""
    try:
        purchase = TokenPurchase.objects.get(reference=reference)
        
        # Check payment status from Paynow result
        payment_status = request.GET.get('payment_status', '')
        
        if payment_status == 'Successful':
            purchase.status = 'completed'
            purchase.fulfil()
            messages.success(request, 'Payment successful! Tokens added.')
        else:
            purchase.status = 'failed'
            messages.error(request, 'Payment failed. Please try again.')
        
        purchase.save()
    except TokenPurchase.DoesNotExist:
        messages.error(request, 'Invalid payment reference.')
    
    return redirect('dashboard')


class TokenViewSet(viewsets.ModelViewSet):
    """API viewset for token management."""
    serializer_class = TokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Token.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a token via API."""
        token = self.get_object()
        if token.used:
            return Response(
                {'error': 'Token already used'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for existing active tokens - only one token can be active at a time
        active_token = Token.objects.filter(
            user=request.user,
            used=True,
            expired=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if active_token:
            return Response(
                {'error': f'User already has an active token (expires {active_token.expires_at.strftime("%Y-%m-%d %H:%M")})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ip = request.META.get('REMOTE_ADDR')
        token.activate(ip)
        # Create analytics session
        Session.objects.create(
            user=request.user,
            token=token,
            ip_address=ip
        )
        return Response(TokenSerializer(token).data)


class TokenPurchaseViewSet(viewsets.ModelViewSet):
    """API viewset for token purchases."""
    serializer_class = TokenPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TokenPurchase.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)