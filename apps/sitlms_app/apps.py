from django.apps import AppConfig


class SitlmsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sitlms_app'

    def ready(self):
        import apps.sitlms_app.signals
