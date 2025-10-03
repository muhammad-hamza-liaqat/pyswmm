from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "Password is required"}
    )
    email = serializers.EmailField(
        required=True,
        error_messages={"required": "Email is required"}
    )
    name = serializers.CharField(
        required=True,
        error_messages={"required": "Name is required"}
    )
    phone = serializers.CharField(
        required=True,
        error_messages={"required": "Phone is required"}
    )

    class Meta:
        model = User
        fields = ['email', 'name', 'phone', 'password']

    def validate(self, attrs):
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={"required": "Email is required"}
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "Password is required"}
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError({"error": "Invalid email or password"})

        attrs['user'] = user
        return attrs
