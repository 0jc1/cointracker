"""
URL configuration for cointracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404

from accounts.views import signup_view, login_view, logout_view
from portfolios.views import portfolio_view, remove_wallet_view, PortfolioBalanceOverTimeView
from .views import (
    donate_view, index_view,
    settings_view, transactions_view, about_view, my404_view
)

handler404 = my404_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='index'),
    path('home/', index_view, name='index'),
    path('donate/', donate_view, name='donate'),
    path('about/', about_view, name='about'),
    path('login/', login_view, name='login'),
    path('portfolio/', portfolio_view, name='portfolio'),
    path('settings/', settings_view, name='settings'),
    path('sign-up/', signup_view, name='sign-up'),
    path('transactions/', transactions_view, name='transactions'),
    path('logout/', logout_view, name="logout"),
    path('remove-wallet/<int:wallet_id>/', remove_wallet_view, name='remove_wallet'),
    path('api-auth/', include('rest_framework.urls')),  # For browsable API login
    path('api/portfolio/balance/', PortfolioBalanceOverTimeView.as_view(), name='portfolio-balance-over-time'),

]
