from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer
from .models import User
from server.utils.response import success_response
from server.utils.error import error_response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                name=serializer.validated_data['name'],
                phone=serializer.validated_data['phone']
            )
            return success_response(
                message="User registered successfully",
                data={
                    "email": user.email,
                    "name": user.name,
                    "phone": user.phone
                },
                status_code=status.HTTP_201_CREATED
            )

        # Use 'errors' instead of 'error' for proper JSON response
        return error_response(
            message="Registration failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return success_response(
                message="Login successful",
                data={
                    "user": {
                        "email": user.email,
                        "name": user.name
                    },
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token)
                    }
                },
                status_code=status.HTTP_200_OK
            )

        return error_response(
            message="Login failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
