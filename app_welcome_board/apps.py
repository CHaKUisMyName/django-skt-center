from django.apps import AppConfig


class AppWelcomeBoardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_welcome_board'

    def ready(self):
        from scheduler import start
        start()
