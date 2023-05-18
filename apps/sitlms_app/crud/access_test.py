from apps.sitlms_app.models import Admin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

pw_reset_email_template = 'registration/password_reset_email.html'

# Custom test function that checks if the user is an admin
def is_admin(user):
    try:
        access_type = Admin.objects.values_list('access_type', flat=True).get(user=user.id)
        if access_type == 1:
            return True
        return False
    except Exception as e:
        raise PermissionDenied
        # return False

def send_initial_password_resest(request, user):
    # Get the current site
    current_site = get_current_site(request)
    # Determine the protocol (http or https)
    protocol = 'https' if request.is_secure() else 'http'
    # Determine the domain
    domain = current_site.domain
    site_name = domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_password_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    # DI AKO SURE SAAN GALING DAPAT ANG PROTOCOL AND DOMAIN
    html_message = render_to_string(pw_reset_email_template, {'site_name':site_name, 'protocol':protocol, 'domain':domain, 'uid': uid, 'token': token, 'email':user.email })
    plain_message = strip_tags(html_message)
    # email_body = f"Hello {instance.first_name} {instance.last_name}, \n\nPlease use this link to reset your password: \n http://127.0.0.1:8000{reset_password_url} \n\nThank you!"
    send_mail(
        'Password reset request',
        plain_message,
        'noreply@yourdomain.com',
        [user.email],
        fail_silently=False, 
        html_message=html_message,
    )

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data['email']
        form_user = User.objects.filter(email=email).first()
        # Generate the password reset email content
        context = {
            'email': email,
            'domain': self.request.META['HTTP_HOST'],
            'site_name': self.request.META['HTTP_HOST'],
            'uid': urlsafe_base64_encode(force_bytes(form_user.pk)),
            'user': form_user,
            'token': default_token_generator.make_token(form_user),
            'protocol': 'https' if self.request.is_secure() else 'http',
        }
        # Render both the HTML and plain text versions of the email
        html_message = render_to_string(pw_reset_email_template, context)
        plain_message = strip_tags(html_message)
        # Send the email with both versions
        send_mail(
            subject='Password reset request',
            message=plain_message,
            from_email='noreply@yourdomain.com',
            recipient_list=[email],
            fail_silently=False, 
            html_message=html_message,
        )
        print('email sent')
        # return super().form_valid(form)
        return HttpResponseRedirect('/accounts/password_reset/done/')