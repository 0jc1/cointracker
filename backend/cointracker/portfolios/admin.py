from django.contrib import admin
from .models import Wallet, Holding, Portfolio, CryptoPrice
from decimal import Decimal

class HoldingInline(admin.TabularInline):
    model = Holding
    extra = 1
    fields = ('currency', 'ticker', 'amount')
    readonly_fields = ('__str__',)
    show_change_link = True

class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallet_type', 'address', 'value')
    search_fields = ('user__username', 'wallet_type', 'address')
    list_filter = ('wallet_type',)
    inlines = [HoldingInline]

class HoldingAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'currency', 'ticker', 'amount', 'current_value')
    search_fields = ('wallet__user__username', 'ticker')
    list_filter = ('ticker',)
    readonly_fields = ('current_value',)

    def current_value(self, obj):
        return obj.get_current_value()
    current_value.short_description = 'Current Value (USD)'
    current_value.admin_order_field = 'price'  # Ensure 'price' is annotated if needed

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Update the Wallet's total value
        wallet = obj.wallet
        total_value = Decimal('0.00')
        for holding in wallet.holdings.all():
            total_value += holding.get_current_value()
        wallet.value = total_value
        wallet.save()

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance', 'timestamp')
    search_fields = ('user__username',)
    list_filter = ('timestamp',)
    readonly_fields = ('balance', 'timestamp')

class CryptoPriceAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'currency', 'price', 'timestamp')
    search_fields = ('ticker', 'currency')
    list_filter = ('ticker', 'currency', 'timestamp')
    ordering = ('-timestamp',)
    readonly_fields = ('ticker', 'currency', 'price', 'timestamp')
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        meta = self.model._meta
        field_names = ['ticker', 'currency', 'price', 'timestamp']
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response

    export_as_csv.short_description = "Export Selected as CSV"

admin.site.register(Wallet, WalletAdmin)
admin.site.register(Holding, HoldingAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(CryptoPrice, CryptoPriceAdmin)