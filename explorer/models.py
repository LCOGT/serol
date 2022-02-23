from django.db import models
from django.utils.translation import ugettext as _
from django.templatetags.static import static

from datetime import datetime

BODY_TYPES = ((0,'MPC_MINOR_PLANET'), (1,'MPC_COMET'), (2, 'JPL_MAJOR_PLANET'))
ICONS = (
        ('1.1.1-mars.png','Mars'),
        ('1.1.2-jupiter.png','Jupiter'),
        ('1.1.2-neptune.png','Neptune'),
        ('1.1.2-saturn.png','Saturn'),
        ('1.1.2-uranus.png','Uranus'),
        ('2.2-comet-icon.png','Comet'),
        ('2.3-asteroids-icon.png','Asteroid')
)

CHALLENGE_ICONS = (
        ('M1C2-comet-icon.png','Comet'),
        ('M1C1-planet-icon1.png','Planet'),
        ('M1-moon-icon.png','Moon'),
        ('M1C3Galaxy-icon-01.png',' Galaxy M1'),
        ('M1C4-cluster-icon.png','Cluster M1'),
        ('M1C5-nebulae-icon.png','Nebula M1'),
        ('M1C7-asteroid-icon.png','Asteroid'),
        ('M2C1-OpenCluster-icon.png','Open Cluster'),
        ('M2C2-GlobularCluster-icon.png','Globular Cluster'),
        ('M2C3-SupernovaRemnant-icon.png','Supernova'),
        ('M2C4-PlanetaryNebula-icon.png','Planetary Nebula'),
        ('M2C5-StarFormingNebula-icon1.png','Nebula'),
        ('M3C1Spiral-icon.png','Spiral Galaxy'),
        ('M3C2-Elliptical-icon.png','Elliptical Galaxy'),
        ('M3C3-Irregular-icon.png','Irregular Galaxy'),
        ('M3C4-Groups-icon1.png','Galaxy Group'),
)

FACT_CATEGORIES = (
                ('En','Engineering'),
                ('HU','Humour'),
                ('AS','Astronomy'),
                ('OP','Operations')
)


PATCHES = (
    ('patches/GetToKnowTheNightSky_patch.png', 'Mission 1'),
    ('patches/LifeAndDeathOfStars_patch.png', 'Mission 2'),
    ('patches/universeatlarge_patch.png', 'Mission 3')
)

SEASON_FILES = (
    ('halloween.json', 'halloween'),
    ('asteroid-day.json', 'asteroid day'),
    ('equinox2020.json', 'equinox'),
    ('new-year.json', 'new year'),
    ('earth-day.json', 'earth day'),
    ('perseids.json', 'perseids'),
    ('christmas.json', 'christmas'),
)

class Mission(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    patch = models.CharField(max_length=40, choices=PATCHES)
    sticker_total = models.IntegerField(default=0)

    def __str__(self):
        return "{}".format(self.name)

class Challenge(models.Model):
    number = models.IntegerField(help_text=_("Which number in the mission is this challenge?"))
    name = models.CharField(max_length=200)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    description = models.TextField(help_text=_("Start page info"))
    action = models.CharField(max_length=200, help_text=_("What the user should do on Observe page"))
    category = models.CharField(max_length=30, help_text=_("What type of object is this?"), blank=True, null=True)
    avm_code = models.CharField(max_length=10, blank=True, null=True)
    active = models.BooleanField(default=True)
    sticker_total = models.IntegerField(default=1, blank=True, null=True)
    is_last = models.BooleanField(default=False)
    icon = models.CharField(max_length=40, choices=CHALLENGE_ICONS, blank=True, null=True)

    def __str__(self):
        return "Challenge {} from Mission {}".format(self.number, self.mission.number)

    @property
    def icon_url(self):
        return static(f'explorer/images/{self.icon}')

    class Meta:
        unique_together = ['number','mission','active']
        ordering = ['mission','number']

class Body(models.Model):
    name = models.CharField(max_length=20)
    schema = models.IntegerField(choices=BODY_TYPES)
    epochofel = models.FloatField(help_text='MJD')
    orbinc = models.FloatField(help_text='IN')
    longascnode = models.FloatField(help_text='OM')
    argofperih = models.FloatField(help_text='W')
    eccentricity = models.FloatField(help_text='EC')
    dailymotion = models.FloatField(help_text='n', blank=True, null=True)
    meananom = models.FloatField(help_text='MA', blank=True, null=True)
    meandist = models.FloatField(help_text='A',blank=True, null=True)
    perihdist = models.FloatField(help_text='Used for comets',blank=True, null=True)
    epochofperih = models.FloatField(help_text='Used for comets',blank=True, null=True)
    filter_list = models.CharField(max_length=20, help_text=_('JSON blob of filters'))
    exposuretime = models.FloatField()
    avm_code = models.CharField(max_length=10)
    description = models.TextField()
    icon = models.CharField(max_length=25, choices=ICONS)
    active = models.BooleanField(default=True)
    last_update = models.DateTimeField(default=datetime.utcnow)

    class Meta:
        verbose_name_plural = 'bodies'

    def __str__(self):
        return "{}".format(self.name)

class Fact(models.Model):
    tagline = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=200, blank=True, null=True)
    img = models.CharField(max_length=100, blank=True, null=True)
    site = models.CharField(max_length=3, blank=True, null=True)
    published = models.BooleanField(default=True)
    category = models.CharField(max_length=2, choices=FACT_CATEGORIES, default='AS')

    def __str__(self):
        return "{}".format(self.tagline)

class Season(models.Model):
    name = models.CharField(max_length=100)
    start = models.DateTimeField()
    end = models.DateTimeField()
    active = models.BooleanField(default=True)
    jsfile = models.CharField(max_length=20, choices=SEASON_FILES)
    message = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Activity(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    desc = models.TextField()
    active = models.BooleanField()

    class Meta:
        verbose_name_plural = 'activities'

    def __str__(self):
        return self.name
