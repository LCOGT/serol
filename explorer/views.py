from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from django.views.generic.base import RedirectView
from django.urls import reverse, NoReverseMatch

from explorer.models import Mission, Challenge
from status.models import Progress

class MissionView(DetailView):
    model = Mission
    template_name = "explorer/mission.html"

class ChallengeView(DetailView):
    model = Challenge

    def get(self, request, *args, **kwargs):
        self.template_name = "explorer/challenge-{}.html".format(kwargs['mode'])
        if kwargs.get('mode',None) in ['observe','analyse','identify','investigate','status']:
            obj,created = Progress.objects.get_or_create(challenge=self.get_object(), user=self.request.user)
        return super(ChallengeView, self).get(request, *args, **kwargs)


class ChallengeRedirectView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        challenge = get_object_or_404(Challenge, pk=kwargs['pk'])
        try:
            progress = Progress.objects.get(challenge=challenge, user=self.request.user)
            state = progress.state
            urlpath = urlpaths[state]
        except:
            urlpath = 'challenge-start'
        try:
            url = reverse(urlpath, args=args, kwargs=kwargs)
            self.url = url
        except NoReverseMatch:
            return None
        return super(ChallengeRedirectView, self).get_redirect_url(*args, **kwargs)
