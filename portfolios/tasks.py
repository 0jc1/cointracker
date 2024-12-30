import threading
from django.core.management import call_command


def start_portfolio_updates():
    """Start the portfolio update task in a daemon thread"""
    thread = threading.Thread(
        target=call_command,
        args=("update_portfolios",),
        daemon=True,  # Thread will be terminated when main process exits
    )
    thread.start()
