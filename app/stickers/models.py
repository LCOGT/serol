from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings

from status.models import User
from explorer.models import Challenge

STICKERS = (
    ('stickers/M1C1Planets.png','Planets'),
    ('stickers/M1C2Comet.png','Comet'),
    ('stickers/M1C5Nebulae.png','M1 Nebulae'),
    ('stickers/M2C3SupernovaRemnant.png','M2 Supernova'),
    ('stickers/M2C3SupernovaRemnant2.png','M2 Supernova v2'),
    ('stickers/M3C1Spiral.png', 'M3 Spiral'),
    ('stickers/M3C4Groups.png','M3 Galaxy Group'),
    ('stickers/M1C1Planets.png','Planets v2'),
    ('stickers/M1C3Galaxy.png','M1 Galaxy'),
    ('stickers/M1C3Galaxy2.png','M1 Galaxy v2'),
    ('stickers/M1C4Cluster.png',' Star Cluster'),
    ('stickers/M2C1OpenCluster.png', 'Open Cluster'),
    ('stickers/M2C4PlanetaryNebula.png', 'Planetary Nebula'),
    ('stickers/M3C2Elliptical.png','Elliptical Galaxy'),
    ('stickers/M2C2GlobularCluster.png','Globular Cluster'),
    ('stickers/M2C5StarFormingNebula.png', 'Star forming nebula'),
    ('stickers/M3C3Irregular.png','Irregular Galaxy')
)

class Sticker(models.Model):
    desc = models.CharField(max_length=200)
    filename = models.CharField(max_length=40, choices=STICKERS)
    challenge = models.ForeignKey(Challenge, null=True, blank=True, on_delete=models.CASCADE)
    progress = models.CharField(max_length=20, choices=settings.PROGRESS_OPTIONS)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "{}".format(self.desc)

class PersonSticker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sticker = models.ForeignKey(Sticker, on_delete=models.CASCADE)

    def __str__(self):
        return "{} for {}".format(self.sticker, self.user)
