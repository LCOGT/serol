from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.list import ListView


from stickers.models import PersonSticker, Sticker

class StickerView(LoginRequiredMixin, ListView):

    model = Sticker

    def get_context_data(self):
        context = super(StickerView, self).get_context_data()
        context['stickers'] = Sticker.objects.filter(active=True).order_by('challenge__mission','challenge__number')
        return context

    def get_queryset(self):
        queryset = super(StickerView, self).get_queryset()
        queryset = queryset.filter(personsticker__user__username=self.request.user)
        return queryset
