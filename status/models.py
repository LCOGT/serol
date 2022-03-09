from datetime import datetime

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django_fsm import FSMField, transition
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from explorer.models import Challenge, Mission

IMAGE_STATUS_OPTIONS = ((0,'No Image'), (1, 'Quicklook'), (2, 'Final'), (3,'Poor Quality'))
COLOUR_STATE = {'New': '000',
                'Submitted': 'F1C40F',
                'Observed':'5DADE2',
                'Identify':'E67E22',
                'Analyse':'A569BD',
                'Investigate':'aaa',
                'Summary':'2ECC71',
                'Failed':'E74C3C',
                'Redo' : 'F98F00'
                }

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
    default_proposal = models.ForeignKey(Proposal, null=True, blank=True, on_delete=models.CASCADE)
    mission_1 = models.BooleanField(help_text=_('Has user competed Mission 1?'), default=False)
    mission_2 = models.BooleanField(help_text=_('Has user competed Mission 2?'), default=False)
    mission_3 = models.BooleanField(help_text=_('Has user competed Mission 3?'), default=False)

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    requestgroup = models.IntegerField(null=True, blank=True)
    requestid = models.CharField(max_length=100, null=True, blank=True)
    frameids = models.CharField(max_length=20, null=True, blank=True)
    status = FSMField(default='New', choices=settings.PROGRESS_OPTIONS)
    last_update = models.DateTimeField(default=datetime.utcnow)
    target = models.CharField(max_length=100)
    image_file = models.FileField(null=True, blank=True, upload_to='images')
    image_status = models.SmallIntegerField(default=0, choices=IMAGE_STATUS_OPTIONS)

    def has_image(self):
        if self.image_file is not None:
            return True
        else:
            return False
    has_image.boolean = True

    def coloured_state(self):
        return format_html(
            '<span style="color: #{};">{}</span>',
            COLOUR_STATE[self.status],
            self.status,
        )

    def image_tag(self):
        return mark_safe('<img src="{}" width="150" height="150" />'.format(self.image_file.url))
    image_tag.short_description = 'Image'

    @property
    def target_name(self):
        return self.challenge.target

    def __str__(self):
        return "{} is {} in {}".format(self.user.username, self.challenge, self.status)

    class Meta:
        unique_together = (("user","challenge"),)
        verbose_name_plural = 'Challenge Progress'

    @transition(field=status, source=['New'], target='Submitted')
    def submit(self):
        pass

    @transition(field=status, source=['Submitted'], target='Failed')
    def failed(self):
        pass

    @transition(field=status, source=['Analyse','Summary'], target='New')
    def redo(self):
        pass

    @transition(field=status, source=['Failed','Redo'], target='New')
    def retry(self):
        self.requestid = ''
        self.frameids = ''
        self.requestgroup = None
        self.image_file = None
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

class Question(models.Model):
    text = models.TextField()
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'questions'

class Answer(models.Model):
    text = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class UserAnswer(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
