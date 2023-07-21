from rest_framework.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint, Q
from django.utils import timezone

DAY_CHOICES = (
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
)


def validate_tmf_choices(value):
    choices = value.replace(' ', '').split(',')
    validation_msg = "Time Multiplier Factor must be comma separated integers or decimal values up to two decimal " \
                     "places. "
    for choice in choices:
        try:
            float_value = float(choice)
            if not float_value.is_integer() and round(float_value, 2) != float_value:
                raise ValidationError(validation_msg)
        except ValueError:
            raise ValidationError(validation_msg)


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
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='updated_configs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['day'],
                condition=Q(is_active=True),
                name='unique_day_for_active_true'
            )
        ]

    def __str__(self):
        return "Pricing Config - {}".format(self.pk)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super(PricingConfig, self).save(*args, **kwargs)

    def clean(self):
        if PricingConfig.objects.filter(day=self.day, is_active=self.is_active).exists():
            if self.is_active:
                raise ValidationError(
                    {'is_active': f'There is already an active=True instance with day={self.get_day_display()}.'}
                )

