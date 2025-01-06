from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework import serializers

from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email')
        exclude = ('password',)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    password_confirm = serializers.CharField(min_length=8, write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)

        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match')
        validate_password(password)

        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists'})

        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, min_length=8, required=True)

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError({
                    "error": "Invalid credentials",
                    "detail": "Email or password is incorrect."
                })
            if not user.is_active:
                raise serializers.ValidationError({"detail": "This account is inactive."})
        else:
            raise serializers.ValidationError({"detail": "Both email and password are required."})

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, min_length=8, required=True)
    new_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, min_length=8, required=True)
    new_password_confirm = serializers.CharField(style={'input_type': 'password'}, write_only=True, min_length=8, required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')


        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})

        if new_password != new_password_confirm:
            raise serializers.ValidationError({"new_password_confirm": "New passwords do not match."})

        validate_password(new_password, user)

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']

        user.set_password(new_password)
        user.save()
        return user


class ChangeEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_email = serializers.EmailField(required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        email = attrs['email']
        new_email = attrs['new_email']

        if user.email != email:
            raise serializers.ValidationError({"email": "The provided email does not match your current email."})
        if CustomUser.objects.filter(email=new_email).exists():
            raise serializers.ValidationError({"new_email": "A user with this email already exists."})

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.email = self.validated_data['new_email']
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'bio', 'date_joined', )
        read_only_fields = ('id', 'date_joined')

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.bio = validated_data.get('bio', instance.bio)
