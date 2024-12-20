from django.shortcuts import render, redirect
from services.crypto_price import get_cached_or_refresh_prices

def my404_view(request, exception):
    # exception contains information about what caused the 404
    return render(request, '404.html', {}, status=404)

def index_view(request):
    prices = get_cached_or_refresh_prices()

    coins = []
    for symbol, price in prices.items():
        if symbol.lower() == 'btc':
            coins.append({  
                'ticker': symbol.lower(),
                'price': price
            })

    return render(request, 'index.html', {'coins': coins})

def donate_view(request):
    return render(request, 'donate.html')

def about_view(request):
    return render(request, 'about.html')

def login_view(request):
    return render(request, 'login.html')

def settings_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  
    return render(request, 'settings.html')

def signup_view(request):
    return render(request, 'sign-up.html')

def ranking_view(request):
    prices = get_cached_or_refresh_prices()

    coins = []
    for symbol, price in prices.items():
        coins.append({
            'ticker': symbol.lower(),
            'price': price
        })
    
    return render(request, 'ranking.html', {'coins': coins})

def transactions_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  
    return render(request, 'transactions.html')