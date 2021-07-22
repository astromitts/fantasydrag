from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class ContactMessage(models.Model):
    from_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    message_type = models.CharField(
        max_length=100,
        choices=(
            ('support', 'Support'),
            ('dispute', 'Dispute a score'),
            ('general', 'General')
        )
    )
    dispute_type = models.CharField(
        max_length=100,
        choices=(
            ('wrong', 'A score is wrong'),
            ('missing', 'A score is missing')
        ),
        blank=True,
        null=True
    )
    content = models.TextField()
    time_sent = models.DateTimeField(default=now, editable=False)
    status = models.CharField(
        max_length=100,
        choices=(
            ('new', 'new'),
            ('action', 'action needed'),
            ('resolved', 'resolved')
        ),
        default='new'
    )
