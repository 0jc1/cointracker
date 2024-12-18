from django import forms
from .models import Wallet

class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['address']
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Enter wallet address'})
        }