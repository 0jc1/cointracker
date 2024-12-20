from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wallet, Holding, CryptoPrice, Portfolio
from .forms import WalletForm
from decimal import Decimal
from services.crypto_price import get_crypto_price, get_latest_price, get_price_24h_ago
from services.balance import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, F, Max
from datetime import timedelta, date
from .serializers import PortfolioBalanceSerializer


class PortfolioBalanceOverTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=20)

        # Prepare a list of dates
        date_list = [
            start_date + timedelta(days=x)
            for x in range((end_date - start_date).days + 1)
        ]

        # Fetch Portfolio objects for the user within the date range. For each day, get the latest portfolio balance up to that day
        portfolio_qs = Portfolio.objects.filter(
            user=user, timestamp__date__lte=end_date
        ).order_by("timestamp")

        # Annotate each portfolio entry with its date
        portfolio_entries = portfolio_qs.values("balance", "timestamp__date").annotate(
            latest_timestamp=Max("timestamp")
        )

        # Create a mapping from date to the latest balance on or before that date
        balance_over_time = {}
        last_known_balance = Decimal("0.00")

        # Convert queryset to list of dictionaries for easier processing
        portfolio_data = list(portfolio_entries)

        # Sort the portfolio data by date to ensure chronological order
        portfolio_data.sort(key=lambda x: x["timestamp__date"])

        # Create a dictionary to hold the latest balance up to each date
        date_to_balance = {}
        current_index = 0
        total_entries = len(portfolio_data)

        for single_date in date_list:
            # Update the last known balance up to the current date
            while (
                current_index < total_entries
                and portfolio_data[current_index]["timestamp__date"] <= single_date
            ):
                last_known_balance = portfolio_data[current_index]["balance"]
                current_index += 1
            balance_over_time[single_date] = last_known_balance

        # Prepare the response data
        serialized_data = [
            {"date": single_date, "balance": balance_over_time[single_date]}
            for single_date in date_list
        ]

        return Response(
            {
                "labels": [
                    item["date"].strftime("%Y-%m-%d") for item in serialized_data
                ],
                "data": [str(item["balance"]) for item in serialized_data],
            }
        )


def update_wallet_balances(user_wallets):
    for wallet in user_wallets:
        if wallet.wallet_type == "BTC":
            balance = get_address_balance_btc(wallet.address)
        elif wallet.wallet_type == "ETH":
            balance = get_address_balance_eth(wallet.address)
        else:
            balance = Decimal("0.00")  # Unsupported type
        # TODO wallet support

        if balance is not None:
            # wallet.value = balance
            # wallet.save()
            holding, created = Holding.objects.get_or_create(
                wallet=wallet,
                defaults={
                    "currency": wallet.get_wallet_type_display(),
                    "ticker": wallet.wallet_type,
                    "amount": balance,
                },
            )
            if not created:
                holding.amount = balance
                holding.save()


def create_portfolio_object(usr, bal, minutes=5):
    now = timezone.now()
    time_threshold = now - timedelta(minutes=minutes)

    recent_portfolios = Portfolio.objects.filter(
        user=usr, timestamp__gte=time_threshold
    )
    if not recent_portfolios.exists():
        Portfolio.objects.create(user=usr, balance=bal)


@login_required(login_url="/login/")
def portfolio_view(request):
    user = request.user
    user_wallets = Wallet.objects.filter(user=user).prefetch_related("holdings")

    if request.method == "POST":
        form = WalletForm(request.POST)
        if form.is_valid():
            new_wallet = form.save(commit=False)
            new_wallet.user = user
            new_wallet.save()
            return redirect("portfolio")
    else:
        form = WalletForm()

    # Update wallet balances and corresponding holdings
    update_wallet_balances(user_wallets)

    holdings_data = []
    per_wallet_data = []
    total_balance = Decimal("0.00")
    total_change_weighted = Decimal("0.00")
    holdings_aggregate = {}
    wallet_values = {}
    prices_cache = {}  # To store latest_price and price_24h_ago per ticker

    for wallet in user_wallets:
        wallet_value = Decimal("0.00")
        for holding in wallet.holdings.all():
            ticker = holding.ticker.upper()
            amount = holding.amount

            if ticker not in prices_cache:
                latest_price = get_latest_price(ticker)
                price_24h_ago = get_price_24h_ago(ticker)
                prices_cache[ticker] = {
                    "latest_price": latest_price,
                    "price_24h_ago": price_24h_ago,
                }
            else:
                latest_price = prices_cache[ticker]["latest_price"]
                price_24h_ago = prices_cache[ticker]["price_24h_ago"]

            if price_24h_ago and price_24h_ago != Decimal("0.00"):
                change = (
                    (latest_price - price_24h_ago) / price_24h_ago * Decimal("100")
                ).quantize(Decimal("0.01"))
            else:
                change = Decimal("0.00")

            value = (amount * latest_price).quantize(Decimal("0.01"))

            if ticker not in holdings_aggregate:
                holdings_aggregate[ticker] = {
                    "currency": holding.currency,
                    "ticker": ticker,
                    "amount": holding.amount,
                    "latest_price": latest_price,
                    "value": value,
                    "change": change,
                }
            else:
                holdings_aggregate[ticker]["value"] += value
                holdings_aggregate[ticker]["amount"] += holding.amount

            total_balance += value
            total_change_weighted += value * change
            wallet_value += value
            wallet_values[wallet.address] = wallet_value

    for ticker in holdings_aggregate:
        h = holdings_aggregate[ticker]
        holdings_data.append(
            {
                "currency": h["currency"],
                "ticker": h["ticker"],
                "amount": h["amount"],
                "latest_price": h["latest_price"],
                "value": h["value"],
                "change": h["change"],
            }
        )

    for wallet in user_wallets:
        wallet_value = wallet_values[wallet.address]
        # Calculate allocation per wallet
        if total_balance > Decimal("0.00"):
            allocation = (wallet_value / total_balance * Decimal("100")).quantize(
                Decimal("0.01")
            )
        else:
            allocation = Decimal("0.00")

        per_wallet_data.append(
            {
                "wallet": wallet,
                "name": f"{wallet.get_wallet_type_display()} Wallet",
                "address": wallet.address,
                "value": wallet_value,  # Total value across holdings in this wallet
                "allocation": allocation,
            }
        )

    # Calculate overall 24h change
    if total_balance > Decimal("0.00"):
        overall_change = (total_change_weighted / total_balance).quantize(
            Decimal("0.01")
        )
    else:
        overall_change = Decimal("0.00")

    # Sort in descending order
    holdings_data.sort(key=lambda x: x["value"], reverse=True)
    per_wallet_data.sort(key=lambda x: x["value"], reverse=True)

    create_portfolio_object(user, total_balance.quantize(Decimal("0.01")))

    context = {
        "user_wallets": per_wallet_data,
        "form": form,
        "holdings_data": holdings_data,
        "total_balance": total_balance.quantize(Decimal("0.01")),
        "overall_change": overall_change,
    }

    return render(request, "portfolio.html", context)


@login_required
def remove_wallet_view(request, wallet_id):
    wallet = get_object_or_404(Wallet, id=wallet_id, user=request.user)
    wallet.delete()
    return redirect("portfolio")
