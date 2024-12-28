from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _


class ActivateModelMixin:
    """
    Activate a model instance.
    """

    @action(methods=['POST'], detail=True)
    def activate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.activate()
        return Response(_('تم تفعيل الكائن بنجاح'))

    @action(methods=['POST'], detail=True)
    def disabled(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.disabled()
        return Response(_('تم إلغاء تفعيل الكائن بنجاح'))




