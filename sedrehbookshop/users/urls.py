from django.urls import path
from .apis import *

urlpatterns = [
    path('register/', RegisterApi.as_view(), name="register"),
    path('stock/', StockAPI.as_view(), name="stock"),
    path('otp/', OtpAPI.as_view(), name="otp"),
    path('charge/', ChargeStockAPI.as_view(), name="charge"),
]
