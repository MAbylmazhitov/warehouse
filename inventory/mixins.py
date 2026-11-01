# Миксины разграничения прав доступа для Class-Based Views (CBV) системы WMS Control.
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


class StorekeeperRequiredMixin(AccessMixin):
    """
    Миксин ограничивает доступ к представлению, разрешая его только
    кладовщикам (storekeeper), менеджерам (manager) и администраторам (admin/superuser).
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
        if user_role in ['storekeeper', 'manager', 'admin']:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied


class ManagerRequiredMixin(AccessMixin):
    """
    Миксин ограничивает доступ к управлению, разрешая его только
    менеджерам склада (manager) и администраторам системы (admin/superuser).
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
        if user_role in ['manager', 'admin']:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied