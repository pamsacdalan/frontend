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

'''
UserModel = get_user_model()

@receiver(post_save, sender=UserModel)
def send_password_reset(sender, instance, created, **kwargs):
    # WILL REMOVE THIS SIGNAL AND CREATE NON-SIGNAL VERION IN ADMIN CRUD
    if created:
        # Get the current site
        # current_site = Site.objects.get_current()
        # Determine the protocol
        # protocol = 'https' if current_site.domain.startswith('https://') else 'http'
        # Determine the domain
        # domain = current_site.domain
        site_name = '127.0.0.1:8000'
        protocol = 'http'
        domain = '127.0.0.1:8000'
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        token = default_token_generator.make_token(instance)
        reset_password_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        # DI AKO SURE SAAN GALING DAPAT ANG PROTOCOL AND DOMAIN
        html_message = render_to_string('registration/password_reset_email.html', {'site_name':site_name, 'protocol':protocol, 'domain':domain, 'uid': uid, 'token': token, })
        plain_message = strip_tags(html_message)
        # email_body = f"Hello {instance.first_name} {instance.last_name}, \n\nPlease use this link to reset your password: \n http://127.0.0.1:8000{reset_password_url} \n\nThank you!"
        send_mail(
            'Password reset request',
            plain_message,
            'noreply@yourdomain.com',
            [instance.email],
            fail_silently=False, 
            html_message=html_message
        )
'''

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
