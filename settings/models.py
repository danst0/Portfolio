from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal


# Create your models here.
class Settings(models.Model):
    # id = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, null=True, default=None)
    expected_interest = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('8.8'))
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('26.4'))
    inflation = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('2.5'))
    options = [('instant', 'instant'),
               ('weekly', 'weekly'),
               ('monthly', 'monthly'),
               ('quarterly', 'quarterly')]
    view_update_interval = models.CharField(max_length=10, default='weekly',
                                            choices=options)

    def get_setting(self, user, setting):
        my_settings = Settings.objects.get(user=user)
        selected = getattr(my_settings, setting)
        return selected

    def __str__(self):
        return '; '.join(map(lambda x: str(x), (self.user, self.expected_interest, self.tax_rate, self.inflation, self.view_update_interval)))

    # def set_settings(self, user, dict):
    #     for key in dict.keys():
