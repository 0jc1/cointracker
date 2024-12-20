from rest_framework import serializers


class PortfolioBalanceSerializer(serializers.Serializer):
    date = serializers.DateField()
    balance = serializers.DecimalField(max_digits=20, decimal_places=2)
