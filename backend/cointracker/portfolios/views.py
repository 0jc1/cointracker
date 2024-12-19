from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wallet, Holding
from .forms import WalletForm
from decimal import Decimal
from services.crypto_price import get_crypto_price, get_latest_price, get_price_24h_ago
from services.btc import get_address_balance

def update_wallet_balances(user_wallets):
    for wallet in user_wallets:
        if wallet.wallet_type == 'BTC':
            balance = get_address_balance(wallet.address)
        # Handle other wallet types as needed
        else:
            balance = Decimal('0.00')  # Unsupported type

        if balance is not None:
            #wallet.value = balance
            #wallet.save()

            # Update or create the corresponding Holding
            holding, created = Holding.objects.get_or_create(
                wallet=wallet,
                defaults={
                    'currency': wallet.get_wallet_type_display(),
                    'ticker': wallet.wallet_type,
                    'amount': balance
                }
            )
            if not created:
                holding.amount = balance
                holding.save()

def portfolio_view(request):
    user = request.user
    user_wallets = Wallet.objects.filter(user=user)

    if request.method == 'POST':
        form = WalletForm(request.POST)
        if form.is_valid():
            new_wallet = form.save(commit=False)
            new_wallet.user = user
            new_wallet.save()
            return redirect('portfolio')
    else:
        form = WalletForm()

    # Update wallet balances and corresponding holdings
    update_wallet_balances(user_wallets)

    holdings_data = []
    per_wallet_data = []
    total_balance = Decimal('0.00')
    total_change_weighted = Decimal('0.00')

    # Aggregate holdings by ticker
    holdings_aggregate = {}
    for wallet in user_wallets:
        for holding in wallet.holdings.all():
            ticker = holding.ticker.upper()
            if ticker not in holdings_aggregate:
                holdings_aggregate[ticker] = {
                    'currency': holding.currency,
                    'ticker': ticker,
                    'amount': holding.amount,
                }
            else:
                holdings_aggregate[ticker]['amount'] += holding.amount

    # Gather aggregated holdings data
    for ticker, data in holdings_aggregate.items():
        amount = data['amount']

        # Fetch the latest price from CryptoPrice model
        latest_price = get_latest_price(ticker)
        price_24h_ago = get_price_24h_ago(ticker)

        if price_24h_ago and price_24h_ago != Decimal('0.00'):
            change = ((latest_price - price_24h_ago) / price_24h_ago * Decimal('100')).quantize(Decimal('0.01'))
        else:
            change = Decimal('0.00')

        value = (amount * latest_price).quantize(Decimal('0.01'))

        holdings_data.append({
            'currency': data['currency'],
            'ticker': ticker,
            'amount': amount,
            'latest_price': latest_price.quantize(Decimal('0.01')),
            'value': value,
            'change': change,
        })

        total_balance += value
        total_change_weighted += value * change

    # If you still need per_wallet_data (optional)
    for wallet in user_wallets:
        wallet_value = Decimal('0.00')
        for holding in wallet.holdings.all():
            ticker = holding.ticker.upper()
            amount = holding.amount

            # Fetch the latest price from CryptoPrice model
            latest_price = get_latest_price(ticker)
            price_24h_ago = get_price_24h_ago(ticker)

            if price_24h_ago and price_24h_ago != Decimal('0.00'):
                change = ((latest_price - price_24h_ago) / price_24h_ago * Decimal('100')).quantize(Decimal('0.01'))
            else:
                change = Decimal('0.00')

            value = (amount * latest_price).quantize(Decimal('0.01'))
            wallet_value += value

        # Calculate allocation per wallet
        if total_balance > Decimal('0.00'):
            allocation = (wallet_value / total_balance * Decimal('100')).quantize(Decimal('0.01'))
        else:
            allocation = Decimal('0.00')

        per_wallet_data.append({
            'wallet': wallet,
            'name': f"{wallet.get_wallet_type_display()} Wallet",
            'address': wallet.address,
            'value': wallet_value,  # Total value across holdings in this wallet
            'allocation': allocation,
        })

    # Calculate overall 24h change
    if total_balance > Decimal('0.00'):
        overall_change = (total_change_weighted / total_balance).quantize(Decimal('0.01'))
    else:
        overall_change = Decimal('0.00')
        
    holdings_data.sort(key=lambda x: x['value'], reverse=True)
    per_wallet_data.sort(key=lambda x: x['value'], reverse=True)

    context = {
        'user_wallets': per_wallet_data,
        'form': form,
        'holdings_data': holdings_data,
        'total_balance': total_balance.quantize(Decimal('0.01')),
        'overall_change': overall_change,
    }

    return render(request, 'portfolio.html', context)

@login_required
def remove_wallet_view(request, wallet_id):
    wallet = get_object_or_404(Wallet, id=wallet_id, user=request.user)
    wallet.delete()
    return redirect('portfolio')
