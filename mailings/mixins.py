from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class OwnerOrManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Менеджеры могут только смотреть (GET), владельцы — полностью управлять"""
    def test_func(self):
        user = self.request.user
        if getattr(user, 'is_blocked', False):
            return False
        if getattr(user, 'is_manager', False):
            return self.request.method in ['GET', 'HEAD', 'OPTIONS']
        obj = self.get_object()
        return obj.owner == user
