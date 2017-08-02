from django.db import models

class Mission(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    patch = models.ImageField(upload_to='patches')

class Challenge(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    badge = models.ImageField(upload_to='badges')
    mission = models.ForeignKey(Mission)
    description = models.TextField()
    action = models.TextField()
    category = models.TextField(blank=True,null=True)

class Target(models.Model):
    objectid = models.CharField(max_length=50)
