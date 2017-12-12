from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.list import ListView


from stickers.models import PersonSticker, Sticker
from explorer.models import Mission

class StickerView(LoginRequiredMixin, ListView):

    model = Sticker

    def get_context_data(self):
        context = super(StickerView, self).get_context_data()
        context['missions'] = Mission.objects.all()#.order_by('challenge__mission','challenge__number')
        return context

    def get_queryset(self):
        queryset = super(StickerView, self).get_queryset()
        queryset = queryset.filter(personsticker__user__username=self.request.user).order_by('sticker.challenge')
        return queryset

def add_sticker(challenge, user, progress):
    sticker = Sticker.objects.get(challenge=challenge, progress=progress, active=True)
    created, personsticker = PersonSticker.objects.get_or_create(user=user, sticker=sticker)
    return created
