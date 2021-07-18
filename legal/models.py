from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Policy(models.Model):
    eula = models.TextField()
    privacy_policy = models.TextField()
    created = models.DateTimeField(default=now, null=True, editable=False)
    version = models.AutoField(primary_key=True)
    current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.current:
            Policy.objects.filter(current=True).exclude(version=self.version).update(current=False)
        super(Policy, self).save(*args, **kwargs)

    @classmethod
    def get_current(cls):
        return cls.objects.get(current=True)


class PolicyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(default=now, null=True, editable=False)

    @classmethod
    def fetch(cls, user):
        instance = cls.objects.filter(user=user)
        if instance.exists():
            instance = instance.first()
        else:
            instance = cls(user=user)
            instance.save()
        return instance
