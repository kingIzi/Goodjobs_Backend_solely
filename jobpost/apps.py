from django.apps import AppConfig


class JobpostConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobpost'

    def ready(self):
        import jobpost.signals
        # notify_users_on_new_job = jobpost.signals.notify_users_on_new_job
        pass
