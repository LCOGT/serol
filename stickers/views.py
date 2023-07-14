import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models import Count, Q
from django_weasyprint import WeasyTemplateResponseMixin

from stickers.models import PersonSticker, Sticker
from explorer.models import Mission, Challenge
from explorer.utils import completed_missions
from status.models import Progress
from explorer.utils import deg_to_hms_plain
from explorer.utils import get_current_user

class StickerView(ListView):

    model = Sticker
    template_name = 'stickers/sticker_list.html'

    # def get(self, request, *args, **kwargs):
    #     context = self.get_context_data()
    #     if context.get('nouser', False):
    #         return HttpResponseRedirect(reverse('auth_login'))
    #     return self.render_to_response(context)

    def get_context_data(self):
        context = super(StickerView, self).get_context_data()
        user, readonly = get_current_user(self.request)
        context['user'] = user
        context['readonly'] = readonly
        context['completed_missions'] = completed_missions(user)
        if context.get('nouser', False):
            return HttpResponseRedirect(reverse('auth_login'))
        return context

    def get_queryset(self):
        user, readonly = get_current_user(self.request)
        challenges = Challenge.objects.filter(active=True).annotate(count=Count("progress", filter=Q(progress__user__username=user))).order_by('number')
        my_progress = Progress.objects.filter(user=user)
        missions = []
        for m in Mission.objects.all():
            progress = []
            mission_challenges = challenges.filter(mission=m)
            for c in mission_challenges:
                if c.count == 1:
                    myp = my_progress.filter(challenge=c)[0]
                    p = {'image': myp.image_file}
                    if myp.status == 'Summary':
                        p['complete'] = True
                    else:
                        p['complete'] = False
                else:
                    p = {'image': None, 'complete':False}
                p['sticker'] = Sticker.objects.get(challenge=c).notext
                p['challenge'] = c
                progress.append(p)
            missions.append({'mission':m, 'challenges':progress})
        return missions

class MissionPrintView(LoginRequiredMixin, DetailView):

    model = Mission
    template_name = 'stickers/print.html'

    def get_context_data(self, **kwargs):
        context = super(MissionPrintView, self).get_context_data(**kwargs)
        my_progress = Progress.objects.filter(user=self.request.user, challenge__mission=self.get_object())
        progress = []
        mission_challenges = Challenge.objects.filter(active=True, mission=self.get_object()).annotate(count=Count("progress", filter=Q(progress__user__username=self.request.user))).order_by('number')
        for c in mission_challenges:
            if c.count == 1:
                p = {}
                myp = my_progress.filter(challenge=c)[0]
                p['progress'] = myp
                if myp.status == 'Summary':
                    p['coords'] = deg_to_hms_plain(myp.ra, myp.dec)
                    p['complete'] = True
                else:
                    p['complete'] = False
            else:
                p = {'image': None, 'complete':False}
            p['sticker'] = Sticker.objects.get(challenge=c).notext
            progress.append(p)
        context['challenges'] = progress
        return context

class DownloadStickersView(WeasyTemplateResponseMixin, MissionPrintView):
    def get_pdf_filename(self):
        return f'serol-mission-{self.get_object().number}.pdf'


def add_sticker(challenge, user, progress):
    sticker = Sticker.objects.get(challenge=challenge, progress=progress, active=True)
    created, personsticker = PersonSticker.objects.get_or_create(user=user, sticker=sticker)
    return created
