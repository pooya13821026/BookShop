from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.views import APIView

from sedrehbookshop.api.pagination import get_paginated_response_context, LimitOffsetPagination
from sedrehbookshop.book.models import Book, Order
from sedrehbookshop.book.services import create_product, product_list
from sedrehbookshop.users.models import BaseUser


class BookAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class InputSerializer(serializers.Serializer):
        name_book = serializers.CharField(max_length=50)
        category = serializers.CharField(max_length=50)
        price = serializers.IntegerField()
        Limitation = serializers.BooleanField(default=True)
        book_file = serializers.FileField()

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Book
            fields = '__all__'

    @extend_schema(
        responses=OutputSerializer,
        request=InputSerializer,
    )
    def get(self, request):
        query = product_list()
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=query,
            request=request,
            view=self,
        )

    @extend_schema(
        responses=OutputSerializer,
        request=InputSerializer,
    )
    def post(self, request):
        serializer = self.InputSerializer(data=request.data, files=request.FILES)
        serializer.is_valid(raise_exception=True)
        try:
            query = create_product(
                name_book=serializer.validated_data['name_book'],
                category=serializer.validated_data['category'],
                price=serializer.validated_data["price"],
                Limitation=serializer.validated_data["Limitation"],
                book_file=serializer.validated_data["book_file"],
            )
        except Exception as ex:
            return Response(
                {"detail": "Database Error - " + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(self.OutputSerializer(query, context={"request": request}).data)


class BuyBookAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    class InputBuyBookSerializer(serializers.Serializer):
        id = serializers.IntegerField()

    class OutputBuyBookSerializer(serializers.ModelSerializer):
        class Meta:
            model = BaseUser
            fields = ['stock']

    @extend_schema(
        request=InputBuyBookSerializer,
        responses=OutputBuyBookSerializer,
    )
    def post(self, request):
        serializer = self.InputBuyBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            book = Book.objects.get(id=serializer.validated_data['id'])
            user = BaseUser.objects.filter(id=request.user.id).first()
            if book.price <= user.stock:
                stack = user.stock - book.price
                user.stock = stack
                user.save()
                Order.objects.create(book=book, user=user)
        except Exception as ex:
            return Response(
                f"Database Error {ex}",
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(self.OutputBuyBookSerializer(user, context={"request": request}).data)


class OrderAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class OutputOrderSerializer(serializers.ModelSerializer):
        class Meta:
            model = Order
            fields = ['book']

    @extend_schema(
        responses=OutputOrderSerializer,
    )
    def get(self, request):
        user = BaseUser.objects.filter(id=request.user.id).first()
        query = Order.objects.all()
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=self.OutputOrderSerializer,
            queryset=query,
            request=request,
            view=self,
        )
