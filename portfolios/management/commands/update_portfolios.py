from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from portfolios.models import Wallet, Portfolio
from portfolios.views import update_wallet_balances, create_portfolio_object
from decimal import Decimal
from services.crypto_price import get_latest_price
import time

User = get_user_model()

SLEEP_DELAY = 1800  # 30 minutes in seconds
USER_PROCESS_DELAY = 10


class Command(BaseCommand):
    help = "Updates portfolio objects for all users every 30 minutes"

    def handle(self, *args, **kwargs):
        while True:
            try:
                self.stdout.write("Starting portfolio update cycle...")

                users = User.objects.all()

                for user in users:
                    try:
                        # Get user's wallets
                        user_wallets = Wallet.objects.filter(
                            user=user
                        ).prefetch_related("holdings")

                        # Update wallet balances
                        update_wallet_balances(user_wallets)

                        # Calculate total balance
                        total_balance = Decimal("0.00")
                        prices_cache = {}

                        for wallet in user_wallets:
                            for holding in wallet.holdings.all():
                                ticker = holding.ticker.upper()
                                amount = holding.amount

                                if ticker not in prices_cache:
                                    latest_price = get_latest_price(ticker)
                                    prices_cache[ticker] = latest_price
                                else:
                                    latest_price = prices_cache[ticker]

                                value = (amount * latest_price).quantize(
                                    Decimal("0.01")
                                )
                                total_balance += value

                        # Create portfolio object
                        create_portfolio_object(
                            user, total_balance.quantize(Decimal("0.01")), minutes=30
                        )

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error updating portfolio for user {user.username}: {str(e)}"
                            )
                        )
                        continue
                    time.sleep(USER_PROCESS_DELAY)

                self.stdout.write("Portfolio update cycle completed")

                time.sleep(SLEEP_DELAY)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error in update cycle: {str(e)}"))
                time.sleep(SLEEP_DELAY)
