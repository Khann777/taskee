from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_205_RESET_CONTENT
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, CustomUserSerializer, ProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        """
        Определяет права доступа для различных действий.
        """
        if self.action in ['logout', 'delete', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request, *args, **kwargs):
        """
        Метод для регистрации нового пользователя.
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request, *args, **kwargs):
        """
        Метод для аутентификации пользователя.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'email': user.email,
            'username': user.username,
            'id': user.id
        }, status=HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request, *args, **kwargs):
        """
        Метод для выхода пользователя из системы.
        """
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required for logout.'},
                status=HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logout successful'}, status=HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return CustomUser.objects.filter(user=self.request.user)
        if self.request.user.is_staff:
            return CustomUser.objects.all()
    def get_permissions(self):
        if self.action == 'delete':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
