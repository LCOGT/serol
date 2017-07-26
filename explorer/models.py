from django.db import models

class Mission(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    patch = models.ImageField(uploads='patches')

class Challenge(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    badge = models.ImageField(uploads='badges')
    mission = models.ForeignKey(Mission)
    description = models.TextField()

class Target(models.Model):
    objectid = models.CharField(max_length=50)
    
