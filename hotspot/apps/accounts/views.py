from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .forms import RegistrationForm
from .models import WebmartUser
from .serializers import RegisterSerializer, WebmartUserSerializer
from apps.tokens.models import Token


def register(request):
    """User registration view with automatic token grant."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Grant registration tokens
            for _ in range(settings.REGISTRATION_TOKEN_GRANT):
                Token.objects.create(user=user, source='registration')
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


class UserViewSet(viewsets.ModelViewSet):
    """API viewset for user registration and profile."""
    queryset = WebmartUser.objects.all()
    serializer_class = WebmartUserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """Register a new user via API."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Grant registration tokens
        for _ in range(settings.REGISTRATION_TOKEN_GRANT):
            Token.objects.create(user=user, source='registration')
        return Response(
            WebmartUserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user profile."""
        serializer = WebmartUserSerializer(request.user)
        return Response(serializer.data)