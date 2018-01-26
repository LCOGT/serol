from datetime import datetime

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, Http404
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView
from django.urls import reverse, NoReverseMatch
import logging
import json

from explorer.models import Mission, Challenge, Body
from status.models import Progress, Answer, Question, UserAnswer
from stickers.models import PersonSticker
from stickers.views import add_sticker

logger = logging.getLogger(__name__)

class AnalyseForm(forms.Form):
    answers = forms.CharField(label='Your Answers', max_length=100)

class MissionView(LoginRequiredMixin, DetailView):
    model = Mission
    template_name = "explorer/mission.html"

    def get_context_data(self, **kwargs):
        context = super(MissionView, self).get_context_data(**kwargs)
        mission = self.get_object()
        try:
            latest = Progress.objects.filter(user=self.request.user, challenge__mission=mission).latest('last_update')
            context['current_challenge'] = latest.challenge
        except ObjectDoesNotExist:
            context['current_challenge'] = Challenge.objects.get(mission=mission, number=1)

        return context

class MissionListView(LoginRequiredMixin, ListView):
    model = Mission
    template_name = "explorer/missionlist.html"


class ChallengeView(LoginRequiredMixin, DetailView):
    model = Challenge

    def get(self, request, *args, **kwargs):
        if kwargs.get('mode',None) == 'failed':
            self.template_name = "explorer/challenge-message.html"
        else:
            self.template_name = "explorer/challenge-{}.html".format(kwargs['mode'])
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        mode = kwargs.get('mode',None)
        if mode != 'start':
            obj,created = Progress.objects.get_or_create(challenge=self.get_object(), user=self.request.user)
            if created:
                obj.last_update = datetime.utcnow()
                obj.save()
            context['progress'] = obj
            if mode == 'observe':
                targets = Body.objects.filter(avm_code__startswith=obj.challenge.avm_code, active=True)
                context['targets'] = targets

        return self.render_to_response(context)


class ChallengeSummary(LoginRequiredMixin, DetailView):
    model = Challenge
    template_name = "explorer/challenge-summary.html"

    def get_context_data(self, **kwargs):
        context = super(ChallengeSummary, self).get_context_data(**kwargs)

        challenge = self.get_object()
        progress = Progress.objects.get(challenge=challenge, user=self.request.user)
        stickers = PersonSticker.objects.filter(user=self.request.user, sticker__challenge=challenge)
        answers = UserAnswer.objects.filter(answer__question__challenge=self.get_object(), user=self.request.user)
        # if we are at the end of the mission make sure we mark it on the user profile
        if challenge.is_last:
            missionid = "mission_{}".format(challenge.mission.number)
            self.request.user.__setattr__(missionid, True)
            self.request.user.save()

        context['progress'] = progress
        context['answers'] = answers
        context['stickers'] = stickers


        return context

class AnalyseView(LoginRequiredMixin, DetailView):
    model = Challenge
    template_name = "explorer/challenge-analyser.html"
    form_class = AnalyseForm

    def get_context_data(self, **kwargs):
        frameid = self.request.GET.get('frameid', None)
        context = super(AnalyseView, self).get_context_data(**kwargs)
        try:
            context['questions'] = Question.objects.filter(challenge=self.get_object())
            progress = Progress.objects.get(challenge=self.get_object(), user=self.request.user)
            if frameid and progress.status != 'Analyse':
                progress.analyse()
                progress.frameids = frameid
                progress.save()
            context['progress'] = progress
        except ObjectDoesNotExist:
            raise Http404
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            progress = Progress.objects.get(challenge=self.get_object(), user=self.request.user)
            answers = json.loads(form.cleaned_data['answers'])
            progress.completed()
            progress.save()
            resp = add_answers(answers=answers, user=self.request.user)
            sticker = add_sticker(challenge=self.get_object(), user=self.request.user, progress=progress.status)
            return HttpResponseRedirect(reverse('challenge', args=args, kwargs=kwargs))

        return render(request, self.template_name, {'form': form})


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
                logger.debug("Changed to Analyse")
                progress.analyse()
                progress.save()
            if progress.status == 'New':
                urlpath = 'start'
            else:
                urlpath = progress.status.lower()
        except ObjectDoesNotExist as e:
            urlpath = 'start'
            logger.exception(e)

        try:
            url = reverse(urlpath, args=args, kwargs=kwargs)
            self.url = url
        except NoReverseMatch:
            return None
        return super(ChallengeRedirectView, self).get_redirect_url(*args, **kwargs)

def add_answers(answers, user):
    for answer_id in answers:
        aid = answer_id.replace('answer-', '')
        answer = get_object_or_404(Answer, pk=aid)
        created, ua = UserAnswer.objects.get_or_create(answer=answer, user=user)
    return True
