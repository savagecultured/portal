from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('activate/<uuid:token_id>/', views.activate_token, name='activate_token'),
    path('buy/', views.buy_tokens, name='buy_tokens'),
]

router = DefaultRouter()
router.register(r'api', views.TokenViewSet, basename='token-api')
router.register(r'purchase', views.TokenPurchaseViewSet, basename='token-purchase-api')
urlpatterns += router.urls