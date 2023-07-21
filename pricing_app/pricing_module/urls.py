from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = 'pricing_module'

urlpatterns = [
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('pricing_config', views.PricingConfigListCreateView.as_view(), name='price_config_list_create'),
    path('pricing_config/<int:pk>', views.PricingConfigRetrieveUpdateDeleteView.as_view(), name='price_config_retrieve_update_delete'),
    path('calculate_price', views.CalculatePricingView.as_view(), name='calculate_price'),
    path('action_logs', views.ActionLogListView.as_view(), name='action_logs')
]
