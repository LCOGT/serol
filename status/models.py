from datetime import datetime

from django.db import models

from explorer.models import Challenge, Mission

STATUS_CHOICES = ((0,'Pending'),(1,'Completed'),(2,'Failed'))

class Progress(models.Model):
    user = models.ForeignKey(User)
    challenge = models.ForeignKey(Challenge)
    mission = models.ForeignKey(Mission)
    requestids = models.TextField()
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    last_update = models.DateTimeField(default=datetime.utcnow)
