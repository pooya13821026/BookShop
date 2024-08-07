from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from django.core.validators import MinLengthValidator
from .validators import number_validator, special_char_validator, letter_validator
from sedrehbookshop.users.models import BaseUser
from sedrehbookshop.users.services import register
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from drf_spectacular.utils import extend_schema

from ..book.models import Book


class RegisterApi(APIView):
    class InputRegisterSerializer(serializers.Serializer):
        email = serializers.EmailField(max_length=255)
        password = serializers.CharField(
            validators=[
                number_validator,
                letter_validator,
                special_char_validator,
                MinLengthValidator(limit_value=10)
            ]
        )
        confirm_password = serializers.CharField(max_length=255)

        def validate_email(self, email):
            if BaseUser.objects.filter(email=email).exists():
                raise serializers.ValidationError("email Already Taken")
            return email

        def validate(self, data):
            if not data.get("password") or not data.get("confirm_password"):
                raise serializers.ValidationError("Please fill password and confirm password")

            if data.get("password") != data.get("confirm_password"):
                raise serializers.ValidationError("confirm password is not equal to password")
            return data

    class OutPutRegisterSerializer(serializers.ModelSerializer):

        token = serializers.SerializerMethodField("get_token")

        class Meta:
            model = BaseUser
            fields = ("email", "token", "created_at", "updated_at")

        def get_token(self, user):
            data = dict()
            token_class = RefreshToken

            refresh = token_class.for_user(user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return data

    @extend_schema(request=InputRegisterSerializer, responses=OutPutRegisterSerializer)
    def post(self, request):
        serializer = self.InputRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = register(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except Exception as ex:
            return Response(
                f"Database Error {ex}",
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(self.OutPutRegisterSerializer(user, context={"request": request}).data)


class StockAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    class OutPutStockSerializer(serializers.ModelSerializer):
        class Meta:
            model = BaseUser
            fields = ['stock']

    @extend_schema(
        responses=OutPutStockSerializer,
    )
    def get(self, request):
        user = BaseUser.objects.filter(id=request.user.id).first()
        return Response(self.OutPutStockSerializer(user, context={"request": request}).data)


class OtpAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    class OutputOTOSerializer(serializers.ModelSerializer):
        class Meta:
            model = BaseUser
            fields = ['otp', ]

    @extend_schema(
        responses=OutputOTOSerializer,
    )
    def get(self, request):
        user = BaseUser.objects.filter(id=request.user.id).first()
        return Response(self.OutputOTOSerializer(user, context={"request": request}).data)


class ChargeStockAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    class InputChargeStockSerializer(serializers.Serializer):
        otp = serializers.IntegerField()
        charge = serializers.IntegerField()

    class OutputChargeStockSerializer(serializers.ModelSerializer):
        class Meta:
            model = BaseUser
            fields = ['stock']

    @extend_schema(
        responses=OutputChargeStockSerializer,
        request=InputChargeStockSerializer,
    )
    def post(self, request):
        serializer = self.InputChargeStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = BaseUser.objects.filter(id=request.user.id).first()
            otpp = serializer.validated_data['otp']
            charge = serializer.validated_data['charge']
            if user.otp == otpp:
                stock = user.stock + charge
                user.stock = stock
                user.save()
        except Exception as ex:
            return Response(
                f"Database Error {ex}",
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(self.OutputChargeStockSerializer(user, context={"request": request}).data)
