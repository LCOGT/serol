from django.db import models
from django.utils.translation import ugettext as _

class Mission(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    patch = models.ImageField(upload_to='patches')

    def __str__(self):
        return "{}".format(self.name)

class Challenge(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    badge = models.ImageField(upload_to='badges')
    mission = models.ForeignKey(Mission)
    description = models.TextField(help_text=_("Research page info"))
    action = models.TextField()
    category = models.TextField(help_text=_("Astronomical object type"), blank=True, null=True)
    avm_code = models.CharField(max_length=50, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "Challenge {} from Mission {}".format(self.number, self.mission.number)
