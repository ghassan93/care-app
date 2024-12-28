from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from . import decorators

Title = _("كير")


class TemplateDetailView(TemplateView):
    """
    This class used to display detail model from database
    """

    model = None
    lookup_field = ''

    def get_object(self, **kwargs):
        """
        this function is used to return object
        @return:
        """
        filter_kwargs = {self.lookup_field: kwargs.get(self.lookup_field, None)}
        return get_object_or_404(self.model, **filter_kwargs)

    def get_context_data(self, **kwargs):
        """

        @param kwargs:
        @return:
        """
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object(**kwargs)
        return context


class AnonymousTemplateView(TemplateView):
    title = Title

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    @method_decorator(decorators.anonymous_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AnonymousTemplateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class LoginTemplateView(TemplateView):
    title = Title

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginTemplateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class AdminTemplateView(TemplateView):
    title = Title

    @method_decorator(login_required)
    @method_decorator(decorators.admin_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminTemplateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context
