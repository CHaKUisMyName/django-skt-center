from django.apps import AppConfig


class AppLevelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_level'
