from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.dispatch import receiver
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models.signals import post_save, post_delete
from .models import Admin, Students_Auth, Instructor_Auth
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

@receiver(post_delete, sender=Admin)
def auto_delete_user_with_admin(sender, instance, **kwargs):
    # This behavior is not final. However, the Django recommendation is not to delete User models, which may create errors in the application if done.
    # instance.user.is_active = False
    # instance.user.save()
    instance.user.delete()

@receiver(post_delete, sender=Students_Auth)
def auto_delete_user_with_student(sender, instance, **kwargs):
    # This behavior is not final. However, the Django recommendation is not to delete User models, which may create errors in the application if done.
    # instance.user.is_active = False
    # instance.user.save()
    instance.user.delete()

@receiver(post_delete, sender=Instructor_Auth)
def auto_delete_user_with_instructor(sender, instance, **kwargs):
    # This behavior is not final. However, the Django recommendation is not to delete User models, which may create errors in the application if done.
    # instance.user.is_active = False
    # instance.user.save()
    instance.user.delete()
