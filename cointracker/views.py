from django.shortcuts import render, redirect
from decimal import Decimal
from services.crypto_price import get_cached_or_refresh_prices, get_price_24h_ago


def my404_view(request, exception):
    # exception contains information about what caused the 404
    return render(request, "404.html", {}, status=404)


def index_view(request):
    prices = get_cached_or_refresh_prices()

    coins = []
    for symbol, price in prices.items():
        if symbol.lower() == "btc":
            coins.append({"ticker": symbol.lower(), "price": price})

    return render(request, "index.html", {"coins": coins})


def donate_view(request):
    return render(request, "donate.html")


def about_view(request):
    return render(request, "about.html")


def login_view(request):
    return render(request, "login.html")


def settings_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "settings.html")


def ranking_view(request):
    prices = get_cached_or_refresh_prices()
    coins = []
    for symbol, price in prices.items():
        if price is not None: 
            current_price = Decimal(str(price))
            price_24h = get_price_24h_ago(symbol)
            
            # Calculate 24h change percentage
            if price_24h and price_24h != 0:
                change_24h = ((current_price - price_24h) / price_24h) * 100
            else:
                change_24h = Decimal('0.00')
            
            coins.append({
                "ticker": symbol.lower(),
                "price": current_price,
                "change_24h": change_24h
            })
    
    # Sort coins by price in descending order
    coins.sort(key=lambda x: x['price'], reverse=True)
    
    return render(request, "ranking.html", {"coins": coins})


def transactions_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "transactions.html")
