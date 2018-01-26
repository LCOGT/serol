from datetime import datetime

from django.db import models
from django.conf import settings
from django_fsm import FSMField, transition
from django.utils.translation import ugettext as _
from django.contrib.auth.models import AbstractUser

from explorer.models import Challenge, Mission

class Proposal(models.Model):
    code = models.CharField(max_length=20, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        if self.active:
            state = ""
        else:
            state = "NOT "
        return "{} is {}active".format(self.code, state)


class User(AbstractUser):
    token = models.CharField(help_text=_('Authentication for Valhalla'), max_length=50, blank=True, null=True)
    archive_token = models.CharField(help_text=_('Authentication for LCO archive'), max_length=50, blank=True, null=True)
    default_proposal = models.ForeignKey(Proposal)
    mission_1 = models.BooleanField(help_text=_('Has user competed Mission 1?'), default=False)
    mission_2 = models.BooleanField(help_text=_('Has user competed Mission 2?'), default=False)
    mission_3 = models.BooleanField(help_text=_('Has user competed Mission 3?'), default=False)

class Progress(models.Model):
    user = models.ForeignKey(User)
    challenge = models.ForeignKey(Challenge)
    userrequestid = models.CharField(max_length=20, null=True, blank=True)
    requestids = models.CharField(max_length=20, null=True, blank=True)
    frameids = models.CharField(max_length=20, null=True, blank=True)
    status = FSMField(default='New', choices=settings.PROGRESS_OPTIONS)
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

    @transition(field=status, source=['Analyse','Investigate'], target='Summary')
    def completed(self):
        pass

    class Meta:
        verbose_name_plural = 'Challenge Progress'

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
