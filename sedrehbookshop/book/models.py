from django.db import models
import random
from sedrehbookshop.common.models import BaseModel
from sedrehbookshop.users.models import BaseUser


class Book(BaseModel):
    name_book = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=30, default='action')
    price = models.PositiveIntegerField()
    Limitation = models.BooleanField(default=True)
    book_file = models.FileField(upload_to='books/', null=True, blank=True)

    def __str__(self):
        return self.name_book


class Order(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE,null=True, blank=True)
    user = models.ForeignKey(BaseUser, on_delete=models.CASCADE,null=True, blank=True)
