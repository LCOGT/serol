from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django_fsm import FSMField, transition

from explorer.models import Challenge, Mission

STATUS = (
('New','New'),('Submitted', 'Submitted'),('Observed','Observed'),('Failed','Failed'),('Retry','Retry'),('Completed','Completed'),
('Identify','Identify'), ('Analyse','Analyse'), ('Identify','Identify'), ('Investigate','Investigate')
)


class Progress(models.Model):
    user = models.ForeignKey(User)
    challenge = models.ForeignKey(Challenge)
    requestids = models.TextField()
    status = FSMField(default='New', choices=STATUS)
    last_update = models.DateTimeField(default=datetime.utcnow)

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
    def indentify(self):
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
