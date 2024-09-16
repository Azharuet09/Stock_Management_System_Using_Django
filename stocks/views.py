from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import User,StockData,Transaction
from .serializers import StockDataSerializer,TransactionSerializer
from django.utils.dateparse import parse_datetime


class UserView(APIView):
    def post(self, request):
        # Existing code for creating a user
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new user to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, username):
        # Try to retrieve the user data from the Redis cache
        cached_user = cache.get(f'user_{username}')
        
        if cached_user:
            # If user data is cached, return it
            return Response(cached_user, status=status.HTTP_200_OK)
        
        try:
            # If user data is not in the cache, fetch it from the database
            user = User.objects.get(username=username)
            serializer = UserSerializer(user)
            
            # Store the user data in the cache
            cache.set(f'user_{username}', serializer.data, timeout=300)  # Cache for 5 minutes (300 seconds)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
class StockView(APIView):
    def post(self, request):
        # Code for POST /stocks/ (already implemented)
        serializer = StockDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the stock data to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # Check if stock data is in Redis cache
        cached_stocks = cache.get('all_stocks')

        if cached_stocks:
            # If data is cached, return it
            return Response(cached_stocks, status=status.HTTP_200_OK)

        # If cache is empty, fetch data from the database
        stocks = StockData.objects.all()
        serializer = StockDataSerializer(stocks, many=True)

        # Store the serialized data in the cache for 5 minutes
        cache.set('all_stocks', serializer.data, timeout=300)  # Cache for 5 minutes
    
class StockDetailView(APIView):
    def get(self, request, ticker):
        try:
            # Try to get the cached stock data from Redis
            cached_stock = cache.get(f"stock_{ticker}")
        except Exception as e:
            return Response({"error": f"Redis connection error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if cached_stock:
            # If the data is cached, return the cached version (it will be serialized already)
            return Response(cached_stock, status=status.HTTP_200_OK)

        # Fetch the stock data from the database
        stock = StockData.objects.filter(ticker=ticker).first()
        if not stock:
            return Response({"error": "Stock data not found"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the data using DRF serializer
        stock_response = StockDataSerializer(stock).data

        # Cache the serialized data for 60 seconds
        try:
            cache.set(f"stock_{ticker}", stock_response, timeout=60)  # No need to use json.dumps, it's already serialized
        except Exception as e:
            return Response({"error": f"Redis connection error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the serialized stock data
        return Response(stock_response, status=status.HTTP_200_OK)
    
from .tasks import process_transaction  # Import the Celery task 
class TransactionView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        ticker_symbol = request.data.get('ticker')
        transaction_type = request.data.get('transaction_type')
        transaction_volume = request.data.get('transaction_volume')

        # Send transaction task to Celery for processing
        process_transaction.delay(user_id, ticker_symbol, transaction_type, transaction_volume)

        return Response({'status': 'Transaction submitted for processing'}, status=status.HTTP_202_ACCEPTED)
        
class UserTransactionsView(APIView):
    def get(self, request, user_id):
        # Check if the user exists
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve all transactions for the specific user
        transactions = Transaction.objects.filter(user=user)

        # If no transactions are found
        if not transactions:
            return Response({'message': 'No transactions found for this user.'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the transactions
        serializer = TransactionSerializer(transactions, many=True)

        # Return the serialized transaction data
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserTransactionsFromTimestampView(APIView):
    def get(self, request, user_id, start_timestamp, end_timestamp):
        # Check if the user exists
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Parse the start_timestamp to a datetime object
        try:
            start_time = parse_datetime(start_timestamp)
            if start_time is None:
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid start timestamp format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Parse the end_timestamp to a datetime object
        try:
            end_time = parse_datetime(end_timestamp)
            if end_time is None:
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid end timestamp format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the start_time is earlier than end_time
        if start_time >= end_time:
            return Response({'error': 'Start timestamp must be earlier than end timestamp.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Retrieve transactions between the start and end timestamps
        transactions = Transaction.objects.filter(user=user, timestamp__gte=start_time, timestamp__lte=end_time)

        # If no transactions are found
        if not transactions:
            return Response({'message': 'No transactions found for this user between the given timestamps.'},
                            status=status.HTTP_404_NOT_FOUND)

        # Serialize the transactions
        serializer = TransactionSerializer(transactions, many=True)

        # Return the serialized transaction data
        return Response(serializer.data, status=status.HTTP_200_OK)
