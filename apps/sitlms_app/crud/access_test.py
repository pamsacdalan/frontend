from apps.sitlms_app.models import Admin
from django.core.exceptions import PermissionDenied

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