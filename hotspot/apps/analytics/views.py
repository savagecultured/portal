from rest_framework import viewsets, permissions
from .models import Session
from .serializers import SessionSerializer


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for session analytics."""
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Session.objects.all()

    def get_queryset(self):
        return Session.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        # Admin can see all sessions
        if self.request.user.is_staff:
            return SessionSerializer
        return SessionSerializer