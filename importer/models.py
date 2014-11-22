from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_delete
from django.dispatch import receiver


class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    user = models.ForeignKey(User, null=True, default=None)
    imported = models.BooleanField(default=False)

    def __str__(self):
        return str(self.docfile.name)

@receiver(post_delete, sender=Document)
def Document_post_delete_handler(sender, **kwargs):
    file_instance = kwargs['instance']
    storage, path = file_instance.docfile.storage, file_instance.docfile.path
    storage.delete(path)