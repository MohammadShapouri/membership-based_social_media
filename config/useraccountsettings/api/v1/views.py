from useraccountsettings.models import UserAccountSettings
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from .permissions import CanAccessSettings
from .exceptions import DeleteNotAllowed, PostNotAllowed
from useraccountsettings.api.v1.serializers.generalserializer.serializers import UserAccountSettingsSerializer



class SettingsViewSet(ModelViewSet):
    queryset = UserAccountSettings.objects.all()
    serializer_class = UserAccountSettingsSerializer
    lookup_url_kwarg = 'pk'
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'user_account',
        'user_account__username',
    ]

    def get_queryset(self):
        user = self.request.user

        # Base queryset
        if user.is_superuser:
            qs = UserAccountSettings.objects.all()
        else:
            qs = UserAccountSettings.objects.filter(user_account=user.pk)
        return qs

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, CanAccessSettings]
        elif self.request.method == 'DELETE':
            raise DeleteNotAllowed
        elif self.request.method == 'POST':
            raise PostNotAllowed
        else:
            self.permission_classes = [IsAuthenticated, CanAccessSettings]
        return super().get_permissions()
