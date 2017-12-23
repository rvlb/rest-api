from django.contrib.auth import get_user_model

from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from utils.mixins import MixedPermissionsMixin

from .serializers import UserSerializer, PasswordSerializer
from .permissions import IsSelf, IsAdminOrSelf

User = get_user_model()

class UserViewSet(MixedPermissionsMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes_by_action = {
        'list': [IsAdminUser],
        'retrieve': [IsAdminOrSelf],
        'update': [IsAdminOrSelf],
        'destroy': [IsAdminOrSelf],
        'change_password': [IsSelf],
    }

    def create(self, request):
        response = super(UserViewSet, self).create(request)
        # Add new user's token to the response
        instance = User.objects.get(pk=response.data.get('id'))
        response.data.update(instance.set_auth_token())
        return response

    @detail_route(methods=['post'])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['password'])
            user.save()
            # Delete the existing token
            Token.objects.get(user=user).delete()
            # Returns a newly created token within the response
            return Response(user.set_auth_token(), status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
