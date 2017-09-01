from datetime import datetime

from django.db import models
from django_fsm import FSMField, transition
from django.utils.translation import ugettext as _
from django.contrib.auth.models import AbstractUser

from explorer.models import Challenge, Mission

STATUS = (
('New','New'),('Submitted', 'Submitted'),('Observed','Observed'),('Failed','Failed'),('Retry','Retry'),('Completed','Completed'),
('Identify','Identify'), ('Analyse','Analyse'), ('Identify','Identify'), ('Investigate','Investigate')
)

class User(AbstractUser):
    token = models.CharField(help_text=_('Authentication for Valhalla'), max_length=50, blank=True, null=True)
    archive_token = models.CharField(help_text=_('Authentication for LCO archive'), max_length=50, blank=True, null=True)

class Progress(models.Model):
    user = models.ForeignKey(User)
    challenge = models.ForeignKey(Challenge)
    userrequestid = models.CharField(max_length=20)
    requestids = models.CharField(max_length=20)
    status = FSMField(default='New', choices=STATUS)
    last_update = models.DateTimeField(default=datetime.utcnow)
    target = models.CharField(max_length=100)

    def __str__(self):
        return "{} is {} in {}".format(self.user.username, self.challenge, self.status)

    class Meta:
        unique_together = (("user","challenge"),)

    @transition(field=status, source=['New', 'Retry'], target='Submitted')
    def submit(self):
        pass

    @transition(field=status, source=['Submitted'], target='Failed')
    def fail(self):
        pass

    @transition(field=status, source=['Submitted'], target='Observed')
    def observed(self):
        pass

    @transition(field=status, source=['Observed'], target='Identify')
    def identify(self):
        pass

    @transition(field=status, source=['Identify'], target='Analyse')
    def analyse(self):
        pass

    @transition(field=status, source=['Analyse'], target='Investigate')
    def investigate(self):
        pass

    @transition(field=status, source=['Investigate'], target='Completed')
    def completed(self):
        pass

    class Meta:
        verbose_name_plural = 'User Progress'

class Question(models.Model):
    text = models.TextField()
    challenge = models.ForeignKey(Challenge)

    class Meta:
        verbose_name_plural = 'questions'

class Answer(models.Model):
    text = models.TextField()
    question = models.ForeignKey(Question)

class UserAnswer(models.Model):
    answer = models.ForeignKey(Answer)
    user = models.ForeignKey(User)
