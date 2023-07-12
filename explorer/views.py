from datetime import datetime

from django import forms
from django.conf.urls.static import static
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, Http404
from django.templatetags.static import static
from django.urls import reverse, NoReverseMatch
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView
from django.contrib import messages

import logging
import json

from explorer.models import Mission, Challenge, Body, Season, Activity
from status.models import Progress, Answer, Question, UserAnswer
from stickers.models import PersonSticker
from status.views import check_token
from stickers.views import add_sticker
from explorer.utils import add_answers, completed_missions, deg_to_hms, target_icon
from status.models import User

logger = logging.getLogger(__name__)

def home(request):
    now = datetime.now()
    season = Season.objects.filter(start__lte=now, end__gte=now, active=True)
    if season:
        seasonfile = static('explorer/js/{}'.format(season[0].jsfile))
        msg = season[0].message
    else:
        seasonfile = None
        msg = None
    return render(request, 'explorer/home.html', {'seasonfile':seasonfile,'seasonal_msg':msg})

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

        active_missions = set(Progress.objects.filter(user=self.request.user).values_list('challenge__mission', flat=True))
        context['active_missions'] = active_missions
        context['completed_missions'] = completed_missions(self.request.user)

        return context


class MissionComplete(LoginRequiredMixin, DetailView):
    model = Mission
    template_name = "explorer/mission_complete.html"

class MissionListView(LoginRequiredMixin, ListView):
    model = Mission
    template_name = "explorer/missionlist.html"

    def get_context_data(self, **kwargs):
        context = super(MissionListView, self).get_context_data(**kwargs)
        active_missions = set(Progress.objects.filter(user=self.request.user).values_list('challenge__mission', flat=True))
        context['active_missions'] = active_missions

        return context

    def get(self, request):
        if request.user.mission_1 and request.user.mission_2 and request.user.mission_3:
            url = reverse('project-complete')
            return HttpResponseRedirect(url)
        else:
            return super(MissionListView, self).get(request)

class ChallengeBaseView(DetailView):
    model = Challenge

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if context.get('nouser', False):
            return HttpResponseRedirect(reverse('auth_login'))
        return self.render_to_response(context)

class ChallengeView(LoginRequiredMixin, DetailView):
    model = Challenge

    def get(self, request, *args, **kwargs):
        self.template_name = "explorer/challenge-{}.html".format(kwargs['mode'])
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['icon'] = target_icon(self.object.avm_code)
        mode = kwargs.get('mode',None)
        if mode != 'start':
            obj,created = Progress.objects.get_or_create(challenge=self.object, user=self.request.user)
            if created:
                obj.last_update = datetime.utcnow()
                obj.save()
            context['progress'] = obj
            if mode == 'observe':
                if self.object.action == 'moon':
                    context['moon'] = True
                targets = Body.objects.filter(avm_code=self.object.avm_code, active=True)
                context['targets'] = targets
            if mode == 'submitted':
                token = check_token(request.user)
                context['activities'] = Activity.objects.filter(active=True).order_by('?')[0:2]
                context['requestids'] = json.loads(obj.requestid)
                request.session['token'] = token
        return self.render_to_response(context)


class NextChallengeView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        try:
            latest = Progress.objects.filter(user=self.request.user,
                                            status='Summary',
                                            challenge__mission__number=kwargs['mission_num']
                                            ).latest('last_update')

            chal_id = check_missing_challenge(user=self.request.user, mission=kwargs['mission_num'])
            if chal_id:
                return HttpResponseRedirect(reverse('challenge', kwargs={'pk':chal_id}))
            else:
                logger.error("Next challenge returned no challenges")
        except ObjectDoesNotExist as e:
            if str(kwargs['mission_num']) in ['1', '2', '3']:
                logger.debug('User accessing Mission {} for 1st time'.format(kwargs['mission_num']))
                chal = Challenge.objects.get(number=1,mission__id=kwargs['mission_num'])
                return HttpResponseRedirect(reverse('challenge', kwargs={'pk':chal.id}))
            else:
                logger.error("User tried to access mission {} which doesn't exist".format(kwargs['mission_num']))
        return HttpResponseRedirect(reverse('missions'))

class NextMissionChallengeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            latest = Progress.objects.filter(user=self.request.user,
                                            status='Summary',
                                            challenge__mission__number=kwargs['mission_num']
                                            ).latest('last_update')
            if not latest.challenge.is_last:
                chal_id = Challenge.objects.get(number=latest.challenge.number + 1, mission=kwargs['mission_num']).id
            else:
                chal_id = check_missing_challenge(user=self.request.user, mission=kwargs['mission_num'])
            if chal_id:
                return HttpResponseRedirect(reverse('challenge', kwargs={'pk':chal_id}))
            else:
                logger.error("Next challenge returned no challenges")
        except ObjectDoesNotExist as e:
            if str(kwargs['mission_num']) in ['1', '2', '3']:
                logger.debug('User accessing Mission {} for 1st time'.format(kwargs['mission_num']))
                chal = Challenge.objects.get(number=1,mission__id=kwargs['mission_num'])
                return HttpResponseRedirect(reverse('challenge', kwargs={'pk':chal.id}))
            else:
                logger.error("User tried to access mission {} which doesn't exist".format(kwargs['mission_num']))
        return HttpResponseRedirect(reverse('missions'))

class ChallengeRetry(LoginRequiredMixin, DetailView):
    model = Challenge

    def get(self, request, *args, **kwargs):
        # this can only happen if the request has failed or has been explicitly "redone"
        try:
            obj = Progress.objects.get(challenge=self.get_object(), user=self.request.user)
            obj.retry()
            obj.save()
        except:
            logger.info("Challenge {} for {} has not failed".format(self.get_object(), self.request.user))
        return HttpResponseRedirect(reverse('challenge', args=args, kwargs=kwargs))

class ChallengeRedo(LoginRequiredMixin, DetailView):
    model = Challenge

    def get(self, request, *args, **kwargs):
        # this can only happen if the request has failed or has been explicitly "redone"
        try:
            obj = Progress.objects.get(challenge=self.get_object(), user=self.request.user)
            obj.redo()
            obj.save()
            answers = UserAnswer.objects.filter(user=self.request.user, answer__question__challenge=self.get_object())
            answers.delete()
            return HttpResponseRedirect(reverse('retry', args=args, kwargs=kwargs))
        except:
            logger.error("Challenge {} for {} is not in the correct state".format(self.get_object(), self.request.user))
            return HttpResponseRedirect(reverse('challenge', args=args, kwargs=kwargs))

class ChallengeSummary(ChallengeBaseView):
    template_name = "explorer/challenge-summary.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ChallengeSummary, self).get_context_data(**kwargs)
        user, readonly = get_current_user(self.request)
        print(user, readonly)
        if not user:
            context['nouser'] = True
            return context

        challenge = self.get_object()
        progress = Progress.objects.get(challenge=challenge, user=user)

        stickers = PersonSticker.objects.filter(user=user, sticker__challenge=challenge)
        answers = UserAnswer.objects.filter(answer__question__challenge=self.get_object(), user=user)
        # if we are at the end of the mission make sure we mark it on the user profile
        if challenge.is_last and not readonly:
            missionid = "mission_{}".format(challenge.mission.number)
            self.request.user.__setattr__(missionid, True)
            self.request.user.save()

        context['progress'] = progress
        context['answers'] = answers
        context['stickers'] = stickers
        context['completed_missions'] = completed_missions(user)
        context['icon'] = target_icon(challenge.avm_code)
        context['animation'] = static(f"explorer/js/stickerreveal-{challenge.mission.number}.json")
        context['coords'] = deg_to_hms(progress.ra, progress.dec)
        context['readonly'] = readonly
        context['user'] = user

        return context
    

class AnalyseView(ChallengeBaseView):
    template_name = "explorer/challenge-analyser.html"
    form_class = AnalyseForm

    def get_context_data(self, **kwargs):
        frameid = self.request.GET.get('frameid', None)
        context = super(AnalyseView, self).get_context_data(**kwargs)
        user, readonly = get_current_user(self.request)
        context['user'] = user
        context['readonly'] = readonly
        if not user:
            context['nouser'] = True
            return context
        try:
            context['questions'] = Question.objects.filter(challenge=self.get_object())
            progress = Progress.objects.get(challenge=self.get_object(), user=user)
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
        except Progress.DoesNotExist:
            urlpath = 'start'

        try:
            url = reverse(urlpath, args=args, kwargs=kwargs)
            self.url = url
        except NoReverseMatch:
            return None
        return super(ChallengeRedirectView, self).get_redirect_url(*args, **kwargs)

def check_missing_challenge(user, mission):
    chals = Challenge.objects.filter(mission__number=mission, active=True).order_by('number').values_list('number', flat=True)
    pgs = Progress.objects.filter(user=user, challenge__mission__number=mission, challenge__active=True, status="Summary").values_list('challenge__number',flat=True).order_by('challenge__number')
    missing = list(set(chals).difference(set(pgs)))
    if missing:
        return Challenge.objects.get(number=missing[0], mission__number=mission).id
    else:
        return 0
    
def get_current_user(request):
    readonly = False
    uid = request.GET.get('uid','')
    print(uid)
    user = None
    if uid:
        try:
            user = User.objects.get(uuid=uid)
            readonly = True
        except:
            pass
    if request.user.is_authenticated and not user:
        user = request.user
    return user, readonly
