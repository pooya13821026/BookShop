from django.db import transaction
from django.db.models import QuerySet

from sedrehbookshop.book.models import Book, Order


@transaction.atomic
def create_product(*, name_book: str, price: int, category: str, Limitation: bool, book_file) -> QuerySet[Book]:
    return Book.objects.create(
        name_book=name_book, price=price, category=category, Limitation=Limitation, book_file=book_file
    )


def product_list() -> QuerySet[Book]:
    return Book.objects.filter(Limitation=False)