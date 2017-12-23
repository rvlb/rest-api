from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

class User(AbstractUser):
    def set_auth_token(self):
        return {'token': Token.objects.create(user=self).key}

'''
Generates a token whenever an superuser is created through createsuperuser
'''
@receiver(post_save, sender=User)
def set_auth_token(sender, instance=None, created=False, **kwargs):
    if created and instance.is_staff:
        instance.set_auth_token()