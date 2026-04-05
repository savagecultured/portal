import re
import subprocess
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import Device


def get_mac_from_arp(ip):
    """Look up MAC address from the kernel ARP table for the given IP."""
    try:
        result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
        match = re.search(r'([0-9a-fA-F:]{17})', result.stdout)
        return match.group(1).lower() if match else None
    except Exception:
        return None


def detect_device_type(user_agent):
    ua = user_agent.lower()
    if 'android' in ua:
        return 'Android Phone/Tablet'
    if 'iphone' in ua:
        return 'iPhone'
    if 'ipad' in ua:
        return 'iPad'
    if 'windows' in ua:
        return 'Windows PC'
    if 'macintosh' in ua or 'mac os x' in ua:
        return 'Mac'
    if 'linux' in ua:
        return 'Linux Device'
    return 'Unknown'


class DeviceFingerprintMiddleware(MiddlewareMixin):
    """Capture device fingerprint and attach a Device instance to the request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT', '')

        mac = get_mac_from_arp(ip) if ip else None

        if mac:
            device, _ = Device.objects.update_or_create(
                mac_address=mac,
                defaults={
                    'ip_address': ip,
                    'user_agent': ua,
                    'device_type': detect_device_type(ua),
                    'os_hint': '',  # Could be extended with OS detection
                    'user': request.user if request.user.is_authenticated else None,
                }
            )
            request.device = device
        else:
            request.device = None

        response = self.get_response(request)
        return response