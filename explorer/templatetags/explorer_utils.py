from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django import template

from explorer.models import Challenge
from status.models import Progress

register = template.Library()

@register.simple_tag
def progress_url(user):
    print(user)
    try:
        latest = Progress.objects.filter(user=user).latest('last_update')
    except ObjectDoesNotExist:
        url = reverse('mission',kwargs={'pk':1})
        return url

    if latest.status in ['Summary','Failed']:
        if not latest.challenge.is_last:
            challenge = Challenge.objects.get(number=latest.challenge.number+1, mission=latest.challenge.mission)
            url = reverse('challenge',kwargs={'pk':challenge.pk})
        else:
            # We have come to the end of the Mission
            url = reverse('missions')
    else:
        # We haven't completed this challenge so just take us to it
        url = reverse('challenge',kwargs={'pk':latest.pk})
    return url
