from django import forms
from .models import Wallet


class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ["wallet_type", "address"]
        widgets = {
            "wallet_type": forms.Select(attrs={"class": "f-field"}),
            "address": forms.TextInput(
                attrs={"class": "f-field", "placeholder": "Enter wallet address"}
            ),
        }

    def clean_wallet_type(self):
        wallet_type = self.cleaned_data.get("wallet_type")
        allowed_coins = ["BTC", "ETH", "SOL", "BNB", "LTC"]
        if wallet_type not in allowed_coins:
            raise forms.ValidationError(
                "Only BTC, ETH, SOL, LTC, or BNB wallets are allowed."
            )
        return wallet_type

    def clean_address(self):
        address = self.cleaned_data.get("address")
        return address
