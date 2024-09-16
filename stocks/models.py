from django.db import models
from django.utils import timezone

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.username

class StockData(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)  # Automatically set the current timestamp

    def __str__(self):
        return self.ticker


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.ForeignKey(StockData, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPE_CHOICES)
    transaction_volume = models.IntegerField()
    transaction_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f"{self.user.username} - {self.ticker.ticker} - {self.transaction_type}"