from django.contrib import admin
from .models import PricingConfig, ActionLog

admin.site.register(PricingConfig)
admin.site.register(ActionLog)
