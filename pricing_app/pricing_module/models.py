from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.exceptions import ValidationError

DAY_CHOICES = (
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    )

def validate_tmf_choices(value):
        choices = value.split(',')
        for choice in choices:
            try:
                float_value = float(choice)
                if not float_value.is_integer() and round(float_value, 2) != float_value:
                    raise ValidationError("Time Multiplier Factor must be comma separated integers or decimal values "
                                          "up to two decimal places.")
            except ValueError:
                raise ValidationError("Time Multiplier Factor must be comma separated integers or decimal values up "
                                      "to two decimal places.")


class PricingConfig(models.Model):
    distance_base_price = models.DecimalField(max_digits=8, decimal_places=2)
    base_distance = models.DecimalField(max_digits=8, decimal_places=1)
    day = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    distance_additional_price = models.DecimalField(max_digits=8, decimal_places=2)
    time_multiplier_factor = models.CharField(max_length=200, validators=[validate_tmf_choices])
    waiting_charges = models.DecimalField(max_digits=8, decimal_places=2)
    waiting_time_threshold = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_configs')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_configs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('day', 'is_active')

    def __str__(self):
        return "Pricing Config - {}".format(self.pk)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super(PricingConfig, self).save(*args, **kwargs)


@receiver(pre_save, sender=PricingConfig)
@login_required
def set_updated_by(sender, instance, *args, **kwargs):
    request = kwargs.get('request')
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        instance.updated_by = request.user
