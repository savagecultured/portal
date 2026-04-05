import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from apps.tokens.models import Token
from apps.analytics.models import Session


def get_media_services():
    """Build media services context from settings."""
    services = []
    
    if settings.JELLYFIN_URL:
        services.append({
            'name': settings.JELLYFIN_LABEL,
            'url': settings.JELLYFIN_URL,
            'icon': '🎬',
            'description': 'Movies & TV Shows'
        })
    
    if settings.NAVIDROME_URL:
        services.append({
            'name': settings.NAVIDROME_LABEL,
            'url': settings.NAVIDROME_URL,
            'icon': '🎵',
            'description': 'Music Streaming'
        })
    
    if settings.IMMICH_URL:
        services.append({
            'name': settings.IMMICH_LABEL,
            'url': settings.IMMICH_URL,
            'icon': '📸',
            'description': 'Photo Library'
        })
    
    # Parse additional services from JSON
    if settings.ADDITIONAL_SERVICES:
        try:
            additional = json.loads(settings.ADDITIONAL_SERVICES)
            services.extend(additional)
        except json.JSONDecodeError:
            pass
    
    return services


def welcome(request):
    """Welcome/splash page for guest WiFi users."""
    services = get_media_services()
    
    # Build context for template
    context = {}
    for svc in services:
        if svc['name'] == settings.JELLYFIN_LABEL:
            context['jellyfin_url'] = svc['url']
            context['jellyfin_label'] = svc['name']
        elif svc['name'] == settings.NAVIDROME_LABEL:
            context['navidrome_url'] = svc['url']
            context['navidrome_label'] = svc['name']
        elif svc['name'] == settings.IMMICH_LABEL:
            context['immich_url'] = svc['url']
            context['immich_label'] = svc['name']
    
    context['additional_services'] = [s for s in services if s['name'] not in [
        settings.JELLYFIN_LABEL, settings.NAVIDROME_LABEL, settings.IMMICH_LABEL
    ]]
    
    return render(request, 'portal/welcome.html', context)


@login_required
def dashboard(request):
    """User dashboard showing tokens and recent sessions."""
    tokens = Token.objects.filter(user=request.user).order_by('-created_at')
    sessions = Session.objects.filter(user=request.user).order_by('-start_time')[:20]
    available = tokens.filter(used=False, expired=False).count()
    
    # Find active token
    active_token = None
    active_count = 0
    for token in tokens:
        if token.is_active:
            active_count += 1
            if active_token is None:
                active_token = token
    
    # Build media services context
    services = get_media_services()
    media_context = {}
    for svc in services:
        if svc['name'] == settings.JELLYFIN_LABEL:
            media_context['jellyfin_url'] = svc['url']
            media_context['jellyfin_label'] = svc['name']
        elif svc['name'] == settings.NAVIDROME_LABEL:
            media_context['navidrome_url'] = svc['url']
            media_context['navidrome_label'] = svc['name']
        elif svc['name'] == settings.IMMICH_LABEL:
            media_context['immich_url'] = svc['url']
            media_context['immich_label'] = svc['name']
    
    media_context['additional_services'] = [s for s in services if s['name'] not in [
        settings.JELLYFIN_LABEL, settings.NAVIDROME_LABEL, settings.IMMICH_LABEL
    ]]
    
    return render(request, 'portal/dashboard.html', {
        'tokens': tokens,
        'sessions': sessions,
        'available': available,
        'active_count': active_count,
        'active_token': active_token,
        'active_token_expires': active_token.expires_at if active_token else None,
        **media_context
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