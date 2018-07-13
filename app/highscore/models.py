from django.db import models

from status.models import User

class Score(models.Model):
    score = models.FloatField(default=0.0)
    username = models.CharField(max_length=10)

    def __str__(self):
        return "{} scored {}".format(self.username, self.score)

class LevelScore(models.Model):
    user = models.ForeignKey(User)
    level = models.IntegerField(default=1)
    score = models.FloatField(default=0.0)
    username = models.CharField(max_length=10)

    def __str__(self):
        return "{} scored {} on level {}".format(self.user, self.score, self.level)

    class Meta:
        unique_together = (("user","level"),)
