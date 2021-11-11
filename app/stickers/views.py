from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.list import ListView
from django.db.models import Count, Q

from stickers.models import PersonSticker, Sticker
from explorer.models import Mission, Challenge
from explorer.utils import completed_missions
from status.models import Progress

class StickerView(LoginRequiredMixin, ListView):

    model = Sticker
    template_name = 'stickers/sticker_list.html'

    def get_context_data(self):
        context = super(StickerView, self).get_context_data()
        context['completed_missions'] = completed_missions(self.request.user)
        return context

    def get_queryset(self):
        challenges = Challenge.objects.filter(active=True).annotate(count=Count("progress", filter=Q(progress__user__username=self.request.user))).order_by('number')
        my_progress = Progress.objects.filter(user=self.request.user)
        missions = []
        for m in Mission.objects.all():
            progress = []
            mission_challenges = challenges.filter(mission=m)
            for c in mission_challenges:
                if c.count == 1:
                    p = {'image': my_progress.filter(challenge=c)[0].image_file, 'complete':True}
                else:
                    p = {'image': None, 'complete':False}
                p['sticker'] = Sticker.objects.get(challenge=c).filename
                p['challenge'] = c
                progress.append(p)
            missions.append({'mission':m, 'challenges':progress})
        return missions

def add_sticker(challenge, user, progress):
    sticker = Sticker.objects.get(challenge=challenge, progress=progress, active=True)
    created, personsticker = PersonSticker.objects.get_or_create(user=user, sticker=sticker)
    return created
