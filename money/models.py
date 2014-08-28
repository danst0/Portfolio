from django.db import models

# Create your models here.

class Money(models.Model):
    date = models.DateField('date of income/total')
    type = models.CharField(max_length=10)
    value = models.DecimalField(max_digits=20, decimal_places=4)

    def __str__(self):
        return self.type, self.date, self.value