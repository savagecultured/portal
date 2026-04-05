from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
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


@login_required
def buy_tokens(request):
    """Token purchase view."""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        amount = quantity * 0.50  # $0.50 per token
        purchase = TokenPurchase.objects.create(
            user=request.user,
            quantity=quantity,
            amount=amount
        )
        # Fulfil immediately (placeholder for payment gateway integration)
        purchase.fulfil()
        messages.success(request, f'{quantity} tokens purchased successfully!')
        return redirect('dashboard')
    return render(request, 'tokens/buy.html')


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