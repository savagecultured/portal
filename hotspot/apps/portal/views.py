import json
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Sum
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


def format_bytes(bytes_val):
    """Format bytes into human readable string."""
    if bytes_val >= 1024**3:
        return f'{bytes_val / (1024**3):.1f} GB'
    elif bytes_val >= 1024**2:
        return f'{bytes_val / (1024**2):.1f} MB'
    elif bytes_val >= 1024:
        return f'{bytes_val / 1024:.1f} KB'
    return f'{bytes_val} B'


def get_usage_chart_data(user, days=7):
    """Get usage data for chart (last N days)."""
    labels = []
    data = []
    
    for i in range(days - 1, -1, -1):
        day = timezone.now().date() - timedelta(days=i)
        labels.append(day.strftime('%b %d'))
        
        # Get bandwidth for this day
        bandwidth = Session.objects.filter(
            user=user,
            start_time__date=day
        ).aggregate(total=Sum('bytes_rx') + Sum('bytes_tx'))['total'] or 0
        
        data.append(round(bandwidth / (1024 * 1024), 2))  # MB
    
    return labels, data


@login_required
def dashboard(request):
    """User dashboard showing tokens, sessions, and usage stats."""
    user = request.user
    tokens = Token.objects.filter(user=user).order_by('-created_at')
    sessions = Session.objects.filter(user=user).order_by('-start_time')[:20]
    available = tokens.filter(used=False, expired=False).count()
    total_tokens = tokens.count()
    
    # Active token
    active_token = None
    active_count = 0
    for token in tokens:
        if token.is_active:
            active_count += 1
            if active_token is None:
                active_token = token
    
    # Usage stats
    total_sessions = sessions.count()
    total_seconds = sum(s.duration_seconds for s in sessions)
    total_hours = total_seconds // 3600
    total_minutes = (total_seconds % 3600) // 60
    total_time_display = f'{total_hours}h {total_minutes}m'
    
    total_bandwidth = sum(s.total_bytes for s in sessions)
    total_bandwidth_display = format_bytes(total_bandwidth)
    
    # Chart data
    chart_labels, chart_data = get_usage_chart_data(user)
    
    # Media services context
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
        'total_tokens': total_tokens,
        'active_count': active_count,
        'active_token': active_token,
        'active_token_expires': active_token.expires_at if active_token else None,
        'total_sessions': total_sessions,
        'total_time_display': total_time_display,
        'total_bandwidth_display': total_bandwidth_display,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        **media_context
    })


@login_required
def activate_token(request, token_id):
    """Activate a token and create an analytics session."""
    token = get_object_or_404(Token, id=token_id, user=request.user, used=False)
    ip = request.META.get('REMOTE_ADDR')
    token.activate(ip)
    Session.objects.create(
        user=request.user,
        device=getattr(request, 'device', None),
        token=token,
        ip_address=ip
    )
    return redirect('dashboard')


# Admin stats view
@login_required
def admin_stats(request):
    """Admin overview of all users, tokens, and sessions."""
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Admin only")
    
    from apps.accounts.models import WebmartUser
    
    # User stats
    total_users = WebmartUser.objects.count()
    active_users = WebmartUser.objects.filter(is_active=True).count()
    new_users_today = WebmartUser.objects.filter(date_joined__date=timezone.now().date()).count()
    
    # Token stats
    total_tokens = Token.objects.count()
    available_tokens = Token.objects.filter(used=False, expired=False).count()
    active_tokens = Token.objects.filter(used=True, expired=False, expires_at__gt=timezone.now()).count()
    purchased_tokens = Token.objects.filter(source='purchase').count()
    
    # Session stats
    total_sessions = Session.objects.count()
    active_sessions = Session.objects.filter(end_time__isnull=True).count()
    total_bandwidth = Session.objects.aggregate(
        total=Sum('bytes_rx') + Sum('bytes_tx')
    )['total'] or 0
    
    # Recent activity
    recent_sessions = Session.objects.order_by('-start_time')[:10]
    recent_users = WebmartUser.objects.order_by('-date_joined')[:10]
    
    # Revenue (from purchases)
    from apps.tokens.models import TokenPurchase
    revenue = TokenPurchase.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    return render(request, 'portal/admin_stats.html', {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'total_tokens': total_tokens,
        'available_tokens': available_tokens,
        'active_tokens': active_tokens,
        'purchased_tokens': purchased_tokens,
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
        'total_bandwidth': format_bytes(total_bandwidth),
        'revenue': revenue,
        'recent_sessions': recent_sessions,
        'recent_users': recent_users,
    })