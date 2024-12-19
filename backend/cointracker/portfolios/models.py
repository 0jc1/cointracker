from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Wallet(models.Model):
    COIN_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('SOL', 'Solana'),
        ('BNB', 'Binance Coin'),
        ('LTC', 'Litecoin'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, unique=True)
    wallet_type = models.CharField(max_length=10, choices=COIN_CHOICES)
    value = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.get_wallet_type_display()} Wallet for {self.user.username}"

class Holding(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='holdings')
    currency = models.CharField(max_length=50) 
    ticker = models.CharField(max_length=50)  # e.g., 'BTC', 'ETH'
    amount = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        unique_together = ('wallet', 'ticker')  # Ensures one holding per ticker per wallet

    def __str__(self):
        return f"{self.amount} {self.currency} in {self.wallet}"
    
    def get_current_value(self):
        # This would require querying the CryptoPrice model for the latest price
        latest_price = CryptoPrice.objects.filter(ticker=self.ticker).order_by('-timestamp').first()
        if latest_price:
            return self.amount * latest_price.price
        return Decimal('0.00')

class CryptoPrice(models.Model):
    ticker = models.CharField(max_length=50) 
    currency = models.CharField(max_length=50) 
    price = models.DecimalField(max_digits=20, decimal_places=2) # price in USD
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.currency} - {self.price} at {self.timestamp}"