from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wallet, Holding, CryptoPrice
from .forms import WalletForm
from decimal import Decimal
from services.crypto_price import get_crypto_price, get_latest_price, get_price_24h_ago
from services.balance import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, F
from datetime import timedelta, date
from .serializers import PortfolioBalanceSerializer

class PortfolioBalanceOverTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        wallets = Wallet.objects.filter(user=user)
        holdings = Holding.objects.filter(wallet__in=wallets)

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=20)

        # Prepare a list of dates
        date_list = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

        # Initialize a dictionary to hold the balance per day
        balance_over_time = {single_date: Decimal('0.00') for single_date in date_list}

        for holding in holdings:
            ticker = holding.ticker
            amount = holding.amount

            # Get all relevant CryptoPrice entries for the holding's ticker between start_date and end_date
            prices = CryptoPrice.objects.filter(
                ticker=ticker,
                timestamp__date__gte=start_date,
                timestamp__date__lte=end_date
            ).order_by('timestamp')

            # Create a date-wise price mapping (use the latest price up to that date)
            price_mapping = {}
            last_price = Decimal('0.00')
            for single_date in date_list:
                # Get the latest price up to and including this date
                latest_price = prices.filter(timestamp__date__lte=single_date).order_by('-timestamp').first()
                if latest_price:
                    last_price = latest_price.price
                price_mapping[single_date] = last_price

            # Calculate the balance for each day and add to the total
            for single_date in date_list:
                daily_balance = amount * price_mapping[single_date]
                balance_over_time[single_date] += daily_balance

        # Prepare the response data
        serialized_data = [
            {
                'date': single_date,
                'balance': balance_over_time[single_date]
            }
            for single_date in date_list
        ]

        # Serialize the data
        serializer = PortfolioBalanceSerializer(serialized_data, many=True)

        return Response({
            'labels': [item['date'].strftime('%Y-%m-%d') for item in serialized_data],
            'data': [str(item['balance']) for item in serialized_data]
        })

def update_wallet_balances(user_wallets):
    for wallet in user_wallets:
        if wallet.wallet_type == 'BTC':
            balance = get_address_balance_btc(wallet.address)
        elif wallet.wallet_type == 'ETH':
            balance = get_address_balance_eth(wallet.address)
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
