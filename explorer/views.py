from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, Http404
from django.views.generic import DetailView
from django.views.generic.base import RedirectView
from django.urls import reverse, NoReverseMatch
import logging

from explorer.models import Mission, Challenge
from status.models import Progress

logger = logging.getLogger(__name__)

class MissionView(DetailView):
    model = Mission
    template_name = "explorer/mission.html"

class ChallengeView(LoginRequiredMixin, DetailView):
    model = Challenge

    def get(self, request, *args, **kwargs):
        if kwargs.get('mode',None) in ['observe','analyse','identify','investigate']:
            self.template_name = "explorer/challenge-{}.html".format(kwargs['mode'])
        elif kwargs.get('mode',None) in ['failed', 'submitted', 'completed', 'start']:
            self.template_name = "explorer/challenge-message.html"
        return super(ChallengeView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ChallengeView, self).get_context_data(**kwargs)
        if kwargs.get('mode',None) != 'start':
            obj,created = Progress.objects.get_or_create(challenge=self.get_object(), user=self.request.user)
            context['progress'] = obj
        return context


class ChallengeRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        logger.debug("Challenge  {}".format(kwargs['pk']))
        challenge = get_object_or_404(Challenge, pk=kwargs['pk'])
        logger.debug('In RedirectView')
        try:
            progress = Progress.objects.get(challenge=challenge, user=self.request.user)
            if progress.status == 'Observed':
                # Skip from observed to identify. This is manual in case user is resting on Submitted page
                progress.identify()
                progress.save()
            elif progress.status == 'Identify' and self.request.META.get('QUERY_STRING', '') == 'next':
                print("Changed to Analyse")
                progress.analyse()
                progress.save()
            if progress.status == 'New':
                urlpath = 'start'
            else:
                urlpath = progress.status.lower()
        except Exception as e:
            urlpath = 'start'
            logger.exception(e)

        try:
            url = reverse(urlpath, args=args, kwargs=kwargs)
            self.url = url
        except NoReverseMatch:
            return None
        return super(ChallengeRedirectView, self).get_redirect_url(*args, **kwargs)
