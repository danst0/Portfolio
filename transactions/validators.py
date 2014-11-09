from django.core.exceptions import ValidationError

def validate_total(value):
    if value % 2 != 0:
        raise ValidationError('%s is not an even number' % value)