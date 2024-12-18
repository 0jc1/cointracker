from django.shortcuts import render, redirect

def my404_view(request, exception):
    # exception contains information about what caused the 404
    return render(request, '404.html', {}, status=404)

def index_view(request):
    coins = [
        {'ticker': 'btc', 'price': 100000},
        {'ticker': 'eth', 'price': 5000},
        {'ticker': 'ltc', 'price': 300},
    ]
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

def transactions_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  
    return render(request, 'transactions.html')