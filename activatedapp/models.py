from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class ActivatedQuerySet(QuerySet):
    """
    This class is used to filter the data returned by the database based on a set of variables
    that are defined in this class
    """

    def activated(self):
        return self.update(is_active=True, activated_at=timezone.now(), disabled_at=None)

    def disabled(self):
        return self.update(is_active=False, disabled_at=timezone.now(), activated_at=None)


class ActivatedManager(models.Manager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    use_in_migrations = True

    def get_queryset(self):
        return ActivatedQuerySet(self.model, using=self._db).filter(is_active=True)


class ArchivedManager(models.Manager):
    """
    This class is used in the model by assigning it to the data member to 'object'
    where it works to add all the methods defined here to every object cloned from that model
    """

    use_in_migrations = True

    def get_queryset(self):
        return ActivatedQuerySet(self.model, using=self._db).filter(is_active=False)


class ActivatedModel(models.Model):
    """
    This class is used to activate objects through additional fields such as activation
    """

    is_active = models.BooleanField(
        _('متاح'),
        default=True
    )

    activated_at = models.DateTimeField(
        _('تاريخ التفعيل'),
        null=True
    )

    disabled_at = models.DateTimeField(
        _('تاريخ إلغاء التفعيل'),
        null=True
    )

    objects = models.Manager()

    activated = ActivatedManager()

    archived = ArchivedManager()

    class Meta:
        abstract = True

    def activate(self):
        """
        this function is used to activate instance
        """
        self.is_active = True
        self.activated_at = timezone.now()
        self.disabled_at = None
        self.save()

    def disabled(self):
        """
        this function is used to disabled instance
        """
        self.is_active = False
        self.disabled_at = timezone.now()
        self.activated_at = None
        self.save()
