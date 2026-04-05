from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from apps.tokens.models import Token
from apps.analytics.models import Session


@login_required
def dashboard(request):
    """User dashboard showing tokens and recent sessions."""
    tokens = Token.objects.filter(user=request.user).order_by('-created_at')
    sessions = Session.objects.filter(user=request.user).order_by('-start_time')[:20]
    return render(request, 'portal/dashboard.html', {
        'tokens': tokens,
        'sessions': sessions,
        'available': tokens.filter(used=False, expired=False).count()
    })


@login_required
def activate_token(request, token_id):
    """Activate a token and create an analytics session."""
    token = get_object_or_404(Token, id=token_id, user=request.user, used=False)
    ip = request.META.get('REMOTE_ADDR')
    token.activate(ip)
    # Create analytics session
    Session.objects.create(
        user=request.user,
        device=getattr(request, 'device', None),
        token=token,
        ip_address=ip
    )
    return redirect('dashboard')