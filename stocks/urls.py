from django.urls import path
from .views import UserView,StockView,StockDetailView,TransactionView,UserTransactionsView,UserTransactionsFromTimestampView

urlpatterns = [
    path('users/', UserView.as_view(), name='register_user'),  # POST endpoint
    path('users/<str:username>/', UserView.as_view(), name='get_user'),  # GET endpoint for retrieving user data
    path('stocks/', StockView.as_view(), name='add_stock'),  # POST endpoint to ingest stock data
    path('stocks/<str:ticker>/', StockDetailView.as_view(), name='get_stock'),  # GET for specific stock data by ticker
    path('transactions/', TransactionView.as_view(), name='post_transaction'),  # POST endpoint for transactions
    path('transactions/<int:user_id>/', UserTransactionsView.as_view(), name='get_user_transactions'),  # GET for user transactions
    path('transactions/<int:user_id>/<str:start_timestamp>/<str:end_timestamp>/', UserTransactionsFromTimestampView.as_view(), name='get_user_transactions_from_timestamp'),  # GET for transactions from a specific timestamp
    
]
