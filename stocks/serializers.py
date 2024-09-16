from rest_framework import serializers
from .models import User
from .models import StockData
from .models import Transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'balance']


class StockDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = ['id', 'ticker', 'open_price', 'close_price', 'high', 'low', 'volume', 'timestamp']  # Include 'id' and 'timestamp'
        read_only_fields = ['id', 'timestamp']  # Make 'id' and 'timestamp' read-only


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user', 'ticker', 'transaction_type', 'transaction_volume', 'transaction_price', 'timestamp']
        read_only_fields = ['transaction_price', 'timestamp']