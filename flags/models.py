from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class FeatureFlag(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    value = models.IntegerField(
        choices=(
            (0, 'Off'),
            (1, 'On')
        ),
        default=0
    )
    created = models.DateTimeField(default=now, editable=False)
    changed = models.DateTimeField(default=now, editable=False)
    users = models.ManyToManyField(User, blank=True)

    def save(self, *args, **kwargs):
        self.changed = now()
        super(FeatureFlag, self).save(*args, **kwargs)

    @property
    def has_users(self):
        return self.users.count() > 0

    @classmethod
    def flag_is_true(cls, flag, user):
        flag = cls.objects.get(title=flag)
        if flag.has_users and user in flag.users.all():
            return flag.value == 1
        else:
            return flag.value == 1
