from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Settings(models.Model):
    # id = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, null=True, default=None)
    expected_interest = models.DecimalField(max_digits=20, decimal_places=20)
    tax_rate = models.DecimalField(max_digits=20, decimal_places=4)
    inflation = models.DecimalField(max_digits=20, decimal_places=4)