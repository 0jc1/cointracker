# portfolios/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Wallet, Holding

@receiver(post_save, sender=Wallet)
def create_holding_for_wallet(sender, instance, created, **kwargs):
    if created:
        # Assuming that the wallet's value represents the initial amount
        # You might need to adjust this based on your business logic
        initial_amount = instance.value

        # Create a Holding object
        Holding.objects.create(
            wallet=instance,
            currency=instance.get_wallet_type_display(),
            ticker=instance.wallet_type,
            amount=initial_amount
        )