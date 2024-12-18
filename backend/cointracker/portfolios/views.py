from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wallet
from .forms import WalletForm

def portfolio_view(request):
	if not request.user.is_authenticated:
		return redirect('login')  	

	user = request.user
	# Fetch all wallets associated with the logged-in user
	user_wallets = Wallet.objects.filter(user=user)
	# If you want to handle adding wallets with a POST directly on this page:
	if request.method == 'POST':
		form = WalletForm(request.POST)
		if form.is_valid():
			new_wallet = form.save(commit=False)
			new_wallet.user = user
			new_wallet.save()
			return redirect('portfolio')  # Reload the page to show the new wallet
	else:
		form = WalletForm()

	context = {
		'user_wallets': user_wallets,
		'form': form,
	}
	return render(request, 'portfolio.html', context)

@login_required
def remove_wallet_view(request, wallet_id):
    wallet = get_object_or_404(Wallet, id=wallet_id, user=request.user)
    wallet.delete()
    return redirect('portfolio')
