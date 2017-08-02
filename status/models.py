from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from explorer.models import Challenge, Mission

STATUS_CHOICES = ((0,'Pending'),(1,'Completed'),(2,'Failed'),(3,'Retry'),(4,'Finished'))


class Progress(models.Model):
    user = models.ForeignKey(User)
    challenge = models.ForeignKey(Challenge)
    requestids = models.TextField()
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    last_update = models.DateTimeField(default=datetime.utcnow)
