from django.utils.timezone import now
from django.db import models


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

    def save(self, *args, **kwargs):
        self.changed = now()
        super(FeatureFlag, self).save(*args, **kwargs)
