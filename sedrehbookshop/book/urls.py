from django.urls import path
from sedrehbookshop.book.apis.book import *

urlpatterns = [
    path('product/', BookAPI.as_view(), name='product'),
    path('buy/', BuyBookAPI.as_view(), name='buy'),
    path('order/', OrderAPI.as_view(), name='order'),
]
