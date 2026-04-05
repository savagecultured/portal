# Webmart Implementation - Step-by-Step Action Plan

This document outlines the remaining steps required to complete the Webmart WiFi Captive Portal implementation based on the [Webmart Implementation Guide](../Webmart_Implementation_Guide.docx).

---

## Table of Contents

1. [Database Migrations](#1-database-migrations)
2. [Token Model Migration](#2-token-model-migration)
3. [URL Configuration](#3-url-configuration)
4. [Templates](#4-templates)
5. [Token Activation Logic](#5-token-activation-logic)
6. [Tests](#6-tests)
7. [Static Files](#7-static-files)
8. [Production Deployment](#8-production-deployment)

---

## 1. Database Migrations

### 1.1 Generate Migrations

Run the following command to generate migrations for all new models:

```bash
python manage.py makemigrations accounts devices tokens analytics portal
```

### 1.2 Apply Migrations

```bash
python manage.py migrate
```

### 1.3 Verify Migration Output

Check that the following tables are created:

- `accounts_webmartuser`
- `devices_device`
- `tokens_tokenpurchase`
- `analytics_session`

---

## 2. Token Model Migration

The existing `Token` model in `apps/accounts/models.py` needs to be migrated to `apps/tokens/models.py` with the full schema from the guide.

### 2.1 Update `apps/tokens/models.py`

Add the complete `Token` model with all required fields:

```python
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Token(models.Model):
    """A single access token granting TOKEN_DURATION_HOURS of portal access."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    used = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)
    source = models.CharField(max_length=30, choices=[
        ('registration', 'Registration Gift'),
        ('purchase', 'Purchase'),
    ], default='registration')

    def activate(self, ip_address):
        """Mark token active, set expiry, whitelist IP in nftables."""
        self.used = True
        self.activated_at = timezone.now()
        self.expires_at = timezone.now() + timedelta(hours=settings.TOKEN_DURATION_HOURS)
        self.save()
        # Open firewall for this IP
        import subprocess
        seconds = settings.TOKEN_DURATION_HOURS * 3600
        subprocess.run([
            'nft', 'add', 'element', 'ip', 'nat', 'allowed_ips',
            f'{{ {ip_address} timeout {seconds}s }}'
        ], check=False)
        subprocess.run([
            'nft', 'add', 'element', 'ip', 'filter', 'allowed_ips',
            f'{{ {ip_address} timeout {seconds}s }}'
        ], check=False)

    @property
    def is_active(self):
        if not self.used or self.expired:
            return False
        return timezone.now() < self.expires_at

    def __str__(self):
        return f'Token {str(self.id)[:8]} — {self.user.email}'
```

### 2.2 Remove Old Token Model from `apps/accounts/models.py`

Remove the `Token` model from `apps/accounts/models.py` since it now lives in `apps/tokens/models.py`.

### 2.3 Update Imports

Update all files that import `Token` from `accounts` to import from `tokens` instead:

- `apps/accounts/views.py`
- `apps/accounts/signals.py`
- `apps/accounts/admin.py`

### 2.4 Generate and Apply Migration

```bash
python manage.py makemigrations tokens
python manage.py migrate
```

---

## 3. URL Configuration

### 3.1 Create `apps/portal/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('activate/<uuid:token_id>/', views.activate_token, name='activate_token'),
]
```

### 3.2 Update `config/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('tokens/', include('apps.tokens.urls')),
    path('dashboard/', include('apps.portal.urls')),
    path('', include('apps.portal.urls')),
]
```

### 3.3 Create `apps/devices/urls.py` (Optional)

If device management views are needed, create URL routes for them.

---

## 4. Templates

Create the following template files:

### 4.1 Base Template

**File:** `templates/base.html`

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}Webmart{% endblock %}</title>
    {% load static %}
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="{% static 'css/style.css' %}" />
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <a class="navbar-brand" href="{% url 'dashboard' %}">Webmart</a>
        {% if user.is_authenticated %}
        <div class="navbar-nav ms-auto">
          <span class="nav-item nav-text">Welcome, {{ user.email }}</span>
          <form method="post" action="{% url 'logout' %}" class="d-inline">
            {% csrf_token %}
            <button type="submit" class="btn btn-link nav-link">Logout</button>
          </form>
        </div>
        {% endif %}
      </div>
    </nav>
    <main class="container mt-4">
      {% if messages %} {% for message in messages %}
      <div
        class="alert alert-{{ message.tags }} alert-dismissible fade show"
        role="alert"
      >
        {{ message }}
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="alert"
        ></button>
      </div>
      {% endfor %} {% endif %} {% block content %}{% endblock %}
    </main>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
```

### 4.2 Registration Template

**File:** `templates/accounts/register.html`

```html
{% extends "base.html" %} {% load crispy_forms_tags %} {% block title %}Register
- Webmart{% endblock %} {% block content %}
<div class="row justify-content-center">
  <div class="col-md-6">
    <div class="card">
      <div class="card-header">
        <h4 class="mb-0">Create Account</h4>
      </div>
      <div class="card-body">
        <form method="post">
          {% csrf_token %} {{ form|crispy }}
          <button type="submit" class="btn btn-primary w-100">Register</button>
        </form>
        <p class="mt-3 text-center">
          Already have an account? <a href="{% url 'login' %}">Login here</a>
        </p>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

### 4.3 Login Template

**File:** `templates/accounts/login.html`

```html
{% extends "base.html" %} {% load crispy_forms_tags %} {% block title %}Login -
Webmart{% endblock %} {% block content %}
<div class="row justify-content-center">
  <div class="col-md-6">
    <div class="card">
      <div class="card-header">
        <h4 class="mb-0">Login</h4>
      </div>
      <div class="card-body">
        <form method="post">
          {% csrf_token %} {{ form|crispy }}
          <button type="submit" class="btn btn-primary w-100">Login</button>
        </form>
        <p class="mt-3 text-center">
          Don't have an account?
          <a href="{% url 'register' %}">Register here</a>
        </p>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

### 4.4 Dashboard Template

**File:** `templates/portal/dashboard.html`

```html
{% extends "base.html" %} {% block title %}Dashboard - Webmart{% endblock %} {%
block content %}
<h2>Welcome, {{ user.email }}</h2>

<!-- Available Tokens -->
<div class="card mb-4">
  <div class="card-header">
    <h5 class="mb-0">Available Tokens: {{ available }}</h5>
  </div>
  <div class="card-body">
    <a href="{% url 'buy_tokens' %}" class="btn btn-success">Buy More Tokens</a>
  </div>
</div>

<!-- Token List -->
<div class="card mb-4">
  <div class="card-header">
    <h5 class="mb-0">Your Tokens</h5>
  </div>
  <div class="card-body">
    <table class="table">
      <thead>
        <tr>
          <th>Token ID</th>
          <th>Source</th>
          <th>Status</th>
          <th>Created</th>
          <th>Expires</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {% for token in tokens %}
        <tr>
          <td>{{ token.id|truncatechars:8 }}</td>
          <td>{{ token.get_source_display }}</td>
          <td>
            {% if token.is_active %}
            <span class="badge bg-success">Active</span>
            {% elif token.used %}
            <span class="badge bg-warning">Used</span>
            {% else %}
            <span class="badge bg-primary">Available</span>
            {% endif %}
          </td>
          <td>{{ token.created_at|date:"Y-m-d H:i" }}</td>
          <td>{{ token.expires_at|date:"Y-m-d H:i"|default:"—" }}</td>
          <td>
            {% if not token.used %}
            <a
              href="{% url 'activate_token' token.id %}"
              class="btn btn-sm btn-primary"
              >Activate</a
            >
            {% endif %}
          </td>
        </tr>
        {% empty %}
        <tr>
          <td colspan="6" class="text-center">
            No tokens yet. Register to receive 5 free tokens!
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>

<!-- Recent Sessions -->
<div class="card">
  <div class="card-header">
    <h5 class="mb-0">Recent Sessions</h5>
  </div>
  <div class="card-body">
    <table class="table">
      <thead>
        <tr>
          <th>Start Time</th>
          <th>End Time</th>
          <th>Duration</th>
          <th>Bandwidth</th>
        </tr>
      </thead>
      <tbody>
        {% for session in sessions %}
        <tr>
          <td>{{ session.start_time|date:"Y-m-d H:i" }}</td>
          <td>{{ session.end_time|date:"Y-m-d H:i"|default:"Active" }}</td>
          <td>{{ session.duration_seconds|default:0 }}s</td>
          <td>{{ session.total_bytes|default:0 }} bytes</td>
        </tr>
        {% empty %}
        <tr>
          <td colspan="4" class="text-center">No sessions yet.</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
```

### 4.5 Buy Tokens Template

**File:** `templates/tokens/buy.html`

```html
{% extends "base.html" %} {% block title %}Buy Tokens - Webmart{% endblock %} {%
block content %}
<div class="row justify-content-center">
  <div class="col-md-6">
    <div class="card">
      <div class="card-header">
        <h4 class="mb-0">Buy Tokens</h4>
      </div>
      <div class="card-body">
        <form method="post">
          {% csrf_token %}
          <div class="mb-3">
            <label for="quantity" class="form-label">Quantity</label>
            <input
              type="number"
              class="form-control"
              id="quantity"
              name="quantity"
              min="1"
              value="1"
            />
          </div>
          <p class="text-muted">Price: $0.50 per token</p>
          <button type="submit" class="btn btn-success w-100">Purchase</button>
        </form>
        <a href="{% url 'dashboard' %}" class="btn btn-secondary w-100 mt-2"
          >Back to Dashboard</a
        >
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

### 4.6 Update Settings for Templates

Add template directories to `config/settings.py`:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Add this line
        'APP_DIRS': True,
        # ... rest of config
    },
]
```

---

## 5. Token Activation Logic

### 5.1 Implement `Token.activate()` Method

Ensure the `Token` model in `apps/tokens/models.py` has the `activate()` method as shown in Section 2.1.

### 5.2 Test Token Activation

1. Create a test user
2. Create a test token for the user
3. Call the activate endpoint with a test IP
4. Verify nftables rules are updated:
   ```bash
   nft list set ip nat allowed_ips
   nft list set ip filter allowed_ips
   ```

---

## 6. Tests

### 6.1 Create Test Files

Create test files for each app:

**`apps/accounts/tests.py`:**

```python
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
            'email': 'test@example.com',
            'phone': '1234567890',
            'date_of_birth': '1990-01-01',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, 'test@example.com')
```

**`apps/tokens/tests.py`:**

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Token, TokenPurchase

User = get_user_model()


class TokenPurchaseTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
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
```

### 6.2 Run Tests

```bash
python manage.py test accounts tokens devices analytics portal
```

---

## 7. Static Files

### 7.1 Create Static Directory Structure

```
static/
├── css/
│   └── style.css
├── js/
│   └── main.js
└── images/
    └── logo.png
```

### 7.2 Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## 8. Production Deployment

### 8.1 Install Production Dependencies

```bash
pip install gunicorn psycopg2-binary whitenoise django-ratelimit celery redis
```

### 8.2 Configure PostgreSQL

Update `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'webmart_db'),
        'USER': os.getenv('DB_USER', 'webmart_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

### 8.3 Configure Gunicorn

Create `gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 3
timeout = 120
accesslog = "/var/log/webmart/gunicorn_access.log"
errorlog = "/var/log/webmart/gunicorn_error.log"
```

### 8.4 Configure Nginx

Follow the guide's Nginx configuration in Section 14.

### 8.5 Configure Supervisor

Follow the guide's Supervisor configuration in Section 15.

### 8.6 Set Up Cron Jobs

```bash
crontab -e
```

Add:

```
*/5 * * * * /opt/webmart/venv/bin/python /opt/webmart/manage.py poll_bandwidth
* * * * * /opt/webmart/venv/bin/python /opt/webmart/manage.py expire_tokens
0 3 * * * /opt/webmart/venv/bin/python /opt/webmart/manage.py cleanup_sessions
```

---

## Quick Reference Commands

| Action                 | Command                                    |
| ---------------------- | ------------------------------------------ |
| Generate migrations    | `python manage.py makemigrations`          |
| Apply migrations       | `python manage.py migrate`                 |
| Run tests              | `python manage.py test`                    |
| Collect static files   | `python manage.py collectstatic --noinput` |
| Create superuser       | `python manage.py createsuperuser`         |
| Run development server | `python manage.py runserver`               |
| Check nftables rules   | `nft list ruleset`                         |
| View DHCP leases       | `cat /var/lib/misc/dnsmasq.leases`         |
| Check AP clients       | `iw dev wlan0 station dump`                |

---

## Checklist

- [ ] Generate and apply database migrations
- [ ] Migrate Token model to tokens app
- [ ] Update all Token imports
- [ ] Create URL configurations
- [ ] Create all HTML templates
- [ ] Implement Token.activate() method
- [ ] Write and run tests
- [ ] Configure static files
- [ ] Set up PostgreSQL
- [ ] Configure Gunicorn
- [ ] Configure Nginx
- [ ] Configure Supervisor
- [ ] Set up cron jobs
- [ ] Deploy to production
