from django.apps import AppConfig
import os


class PortfoliosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portfolios"

    def ready(self):
        import portfolios.signals  # noqa
        
        # Only start the background task in the main process
        if os.environ.get('RUN_MAIN', None) != 'true':
            from portfolios.tasks import start_portfolio_updates
            start_portfolio_updates()
