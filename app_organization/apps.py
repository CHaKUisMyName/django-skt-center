from django.apps import AppConfig


class AppOrganizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_organization'

    def ready(self):
        import app_organization.models
        # return super().ready()
