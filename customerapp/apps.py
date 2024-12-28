from django.apps import AppConfig


class CustomerappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customerapp'

    def ready(self):
        import customerapp.signals
