from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, unique=True)
    # You may add additional fields like a label or nickname for the wallet
    # e.g., nickname = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet - {self.address}"

class Holding(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='holdings')
    currency = models.CharField(max_length=50) 
    ticker = models.CharField(max_length=50)  # e.g., 'BTC', 'ETH'
    amount = models.DecimalField(max_digits=20, decimal_places=8)

    def __str__(self):
        return f"{self.amount} {self.currency} in {self.wallet}"

    # Optional: a method to get the latest value if you have price data
    def get_current_value(self):
        # This would require querying the CryptoPrice model for the latest price
        latest_price = CryptoPrice.objects.filter(currency=self.currency).order_by('-timestamp').first()
        if latest_price:
            return self.amount * latest_price.price
        return None

class CryptoPrice(models.Model):
    ticker = models.CharField(max_length=50) 
    currency = models.CharField(max_length=50) 
    price = models.DecimalField(max_digits=20, decimal_places=2) # price in USD
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.currency} - {self.price} at {self.timestamp}"