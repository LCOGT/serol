from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django import template

from explorer.models import Challenge
from status.models import Progress

register = template.Library()

@register.simple_tag
def progress_url(user):
    '''
     Returns latest challenge
    '''
    try:
        latest = Progress.objects.filter(user=user).latest('last_update')
    except ObjectDoesNotExist:
        url = reverse('mission',kwargs={'pk':1})
        return url

    if latest.status in ['Summary','Failed']:
        if not latest.challenge.is_last:
            challenges = Challenge.objects.filter(number__gt=latest.challenge.number,
                                                mission=latest.challenge.mission,
                                                active=True).order_by('number')
            url = reverse('challenge',kwargs={'pk':challenges[0].pk})
        else:
            # We have come to the end of the Mission
            url = reverse('missions')
    else:
        # We haven't completed this challenge so just take us to it
        url = reverse('challenge',kwargs={'pk':latest.challenge.pk})
    return url

@register.simple_tag
def mission_progress_url(user, mission_id):
    '''
    Returns latest challenge URL within a mission
    '''
    try:
        latest = Progress.objects.filter(user=user, challenge__mission=mission_id).latest('last_update')
    except ObjectDoesNotExist:
        url = reverse('mission',kwargs={'pk':1})
        return url

    if latest.status in ['Summary','Failed']:
        if not latest.challenge.is_last:
            challenges = Challenge.objects.filter(number__gt=latest.challenge.number,
                                                mission=mission_id,
                                                active=True).order_by('number')
            url = reverse('challenge',kwargs={'pk':challenges[0].pk})
        else:
            # We have come to the end of the Mission
            url = reverse('missions')
    else:
        # We haven't completed this challenge so just take us to it
        url = reverse('challenge',kwargs={'pk':latest.challenge.pk})
    return url

@register.filter(name='user_mission_state')
def user_mission_state(user, missionid):
    mission_var = "mission_{}".format(missionid)
    if user._meta.get_field(mission_var) and user.mission_1:
        return True
    elif missionid == 1:
        return True
    else:
        return False
