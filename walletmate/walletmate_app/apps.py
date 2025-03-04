from django.apps import AppConfig


class WalletmateAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'walletmate_app'
    
    def ready(self):
        import walletmate_app.signals
