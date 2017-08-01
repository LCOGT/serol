from django.shortcuts import render
from django.views.generic import DetailView

from explorer.models import Mission, Challenge

class MissionView(DetailView):
    model = Mission
    template_name = "explorer/mission.html"

class ChallengeView(DetailView):
    model = Challenge
    template_name = "explorer/challenge-observe.html"
