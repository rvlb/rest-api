from django.contrib.auth import get_user_model

from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from utils.mixins import MixedPermissionsMixin
from utils.permissions import IsAdminOrSelf

from .serializers import UserSerializer

User = get_user_model()

class UserViewSet(MixedPermissionsMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes_by_action = {
        'list': [IsAdminUser],
        'create': [AllowAny],
        'retrive': [IsAdminOrSelf],
        'update': [IsAdminOrSelf],
        'destroy': [IsAdminOrSelf],
    }