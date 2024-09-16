# stock_management/stocks/tasks.py
from celery import shared_task
from .models import User, StockData, Transaction

@shared_task
def process_transaction(user_id, ticker_symbol, transaction_type, transaction_volume):
    try:
        user = User.objects.get(user_id=user_id)
        stock = StockData.objects.get(ticker=ticker_symbol)
        transaction_price = stock.close_price * int(transaction_volume)

        if transaction_type == 'buy':
            if user.balance < transaction_price:
                return {'error': 'Insufficient balance'}
            user.balance -= transaction_price
        elif transaction_type == 'sell':
            user.balance += transaction_price
        else:
            return {'error': 'Invalid transaction type'}

        user.save()

        transaction = Transaction(
            user=user,
            ticker=stock,
            transaction_type=transaction_type,
            transaction_volume=transaction_volume,
            transaction_price=transaction_price
        )
        transaction.save()

        return {'status': 'Transaction processed successfully'}
    except User.DoesNotExist:
        return {'error': 'User not found'}
    except StockData.DoesNotExist:
        return {'error': 'Stock not found'}
