from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings

from status.models import User
from explorer.models import Challenge

class Sticker(models.Model):
    desc = models.CharField(max_length=200)
    filename = models.ImageField(upload_to='stickers/')
    challenge = models.ForeignKey(Challenge, null=True, blank=True)
    progress = models.CharField(max_length=20, choices=settings.PROGRESS_OPTIONS)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "{}".format(self.desc)

class PersonSticker(models.Model):
    user = models.ForeignKey(User)
    sticker = models.ForeignKey(Sticker)

    def __str__(self):
        return "{} for {}".format(self.sticker, self.user)
