from django.db import models
from django.utils.translation import ugettext as _

from datetime import datetime

BODY_TYPES = ((0,'MPC_MINOR_PLANET'), (1,'MPC_COMET'), (2, 'JPL_MAJOR_PLANET'))
ICONS = (
        ('1.1.1-mars.png','Mars'),
        ('1.1.2-jupiter.png','Jupiter'),
        ('1.1.2-neptune.png','Neptune'),
        ('1.1.2-saturn.png','Saturn'),
        ('1.1.2-uranus.png','Uranus'),
        ('2.2-comet.png','Comet'),
        ('2.3-asteroid.png','Asteroid')
)

class Mission(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    patch = models.ImageField(upload_to='patches')
    sticker_total = models.IntegerField(default=0)

    def __str__(self):
        return "{}".format(self.name)

class Challenge(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    mission = models.ForeignKey(Mission)
    description = models.TextField(help_text=_("Research page info"))
    action = models.TextField(help_text=_("What the user should look for on investigate?"))
    category = models.TextField(help_text=_("What type of object is this?"), blank=True, null=True)
    avm_code = models.CharField(max_length=10, blank=True, null=True)
    active = models.BooleanField(default=True)
    sticker_total = models.IntegerField(default=0)
    is_last = models.BooleanField(default=False)

    def __str__(self):
        return "Challenge {} from Mission {}".format(self.number, self.mission.number)

class Body(models.Model):
    name = models.CharField(max_length=20)
    schema = models.IntegerField(choices=BODY_TYPES)
    epochofel = models.FloatField(help_text='MJD')
    orbinc = models.FloatField(help_text='IN')
    longascnode = models.FloatField(help_text='OM')
    argofperih = models.FloatField(help_text='Tp')
    eccentricity = models.FloatField(help_text='EC')
    dailymotion = models.FloatField(help_text='n', blank=True, null=True)
    meananom = models.FloatField(help_text='MA', blank=True, null=True)
    meandist = models.FloatField(help_text='A',blank=True, null=True)
    perihdist = models.FloatField(help_text='Used for comets',blank=True, null=True)
    epochofperih = models.FloatField(help_text='Used for comets',blank=True, null=True)
    filter_list = models.CharField(max_length=20, help_text=_('JSON blob of filters'))
    exposuretime = models.FloatField()
    avm_code = models.CharField(max_length=10)
    icon = models.CharField(max_length=20, choices=ICONS)
    active = models.BooleanField(default=True)
    last_update = models.DateTimeField(default=datetime.utcnow)

    def __str__(self):
        return "{}".format(self.name)
