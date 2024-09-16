# Stock Management System
This is a simple Stock Management System built with Django, Django REST Framework, Redis, and Celery. The system allows users to manage stock data, execute buy/sell transactions, and store user details. It uses Redis for caching and Celery for processing tasks asynchronously.


### Clone the repository:
``` python 
git clone <repository-url>
```
``` python 
cd stock_management
```
Create a virtual environment and activate it:

### Install the required packages:

``` python 
pip install -r requirements.txt
```

### Set up Redis:

Make sure Redis is installed and running using below command:

``` python 
redis-server
``` 

### Run migrations:

Apply migrations to set up the database tables:
``` python 
python manage.py makemigrations
python manage.py migrate
```
### Start the Django development server:

``` python 
python manage.py runserver
```

### Start the Celery worker:

In a separate terminal, run:

```python 
celery -A stock_management worker --loglevel=info
```

### Endpoints
Install Postman, create a POST request, and use the following details:
``` python 
http://127.0.0.1:8000/stocks/users/

```

POST /users/: Register a new user with a username and initial balance.

Example request:

``` python 
{
  "username": "test",
  "balance": 100.00
}
```
GET /users/{username}/: Retrieve user data (cached in Redis).

create a GET request, and use the following details:
```python
http://127.0.0.1:8000/stocks/users/test/
```

POST /stocks/: Ingest new stock data.
```python
http://127.0.0.1:8000/stocks/stocks/
```
Example request:

```python
{
  "ticker": "test",
  "open_price": 150.00,
  "close_price": 155.00,
  "high": 160.00,
  "low": 148.00,
  "volume": 2000000
}
```
GET /stocks/: Retrieve all stock data (cached in Redis).

```python
http://127.0.0.1:8000/stocks/stocks/
```

GET /stocks/{ticker}/: Retrieve specific stock data by ticker (cached in Redis).

```python
http://127.0.0.1:8000/stocks/stocks/test/
```

POST /transactions/: Post a new transaction.

```python
http://127.0.0.1:8000/stocks/transactions/
```
Example request:
```python
{
  "user_id": 1,
  "ticker": "AAPL",
  "transaction_type": "buy",
  "transaction_volume": 10
}
```
This will calculate the transaction price based on the stock price and update the user’s balance.

GET /transactions/{user_id}/: Retrieve all transactions of a specific user.
```python
http://127.0.0.1:8000/stocks/transactions/{user_id}
```
GET /transactions/{user_id}/{start_timestamp}/{end_timestamp}/: 
Retrieve transactions of a specific user starting from a given timestamp.

```python
http://127.0.0.1:8000/stocks/transactions/{user_id}/{start_timestamp}/{end_timestamp}/
```
## Swagger Documentation
You can access the Swagger API documentation at:

```python
http://127.0.0.1:8000/swagger/
```
### Celery Task
When a new transaction is posted, a task is sent to Celery via Redis for processing. The task checks if the user has sufficient balance for the transaction and updates the User and Transaction tables accordingly.

To monitor tasks, you can run the Celery worker and flower with:

```python
celery -A stock_management worker --loglevel=info
```

```python
celery -A stock_management flower --loglevel=info
```

when you execute the flower command then hit the below url on browser:

```python
http://0.0.0.0:5555
```