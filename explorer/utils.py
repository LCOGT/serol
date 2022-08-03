from astropy.coordinates import SkyCoord
from django.shortcuts import get_object_or_404

from status.models import UserAnswer, Answer


def add_answers(answers, user):
    for answer_id in answers:
        aid = answer_id.replace('answer-', '')
        answer = get_object_or_404(Answer, pk=aid)
        created, ua = UserAnswer.objects.get_or_create(answer=answer, user=user)
    return True

def completed_missions(user):
    completed_missions = []
    for mid in range(1,4):
        if getattr(user, 'mission_'+str(mid)):
            completed_missions.append(mid)
    return completed_missions

def deg_to_hms_plain(ra,dec):
    try:
        coords = SkyCoord(ra, dec, unit='deg')
        ra = coords.ra.hms
        dec = coords.dec.dms
        ra_txt = f'{ra[0]:.0f} : {ra[1]:.0f} : {ra[2]:.0f}'
        dec_txt = f'{dec[0]:.0f} : {dec[1]:.0f} : {dec[2]:.0f}'
        return ra_txt, dec_txt
    except ValueError:
        return "0", "0"

def deg_to_hms(ra,dec):
    try:
        coords = SkyCoord(ra, dec, unit='deg')
        ra = coords.ra.hms
        dec = coords.dec.dms
        ra_html = f'<abbr title="{ra[0]:.0f} hours {ra[1]:.0f} minutes {ra[2]:.0f} seconds">{ra[0]:.0f} : {ra[1]:.0f} : {ra[2]:.0f}</abbr>'
        dec_html = f'<abbr title="{dec[0]:.0f} degrees {dec[1]:.0f} minutes {dec[2]:.0f} seconds">{dec[0]:.0f} : {dec[1]:.0f} : {dec[2]:.0f}</abbr>'
        return mark_safe(ra_html), mark_safe(dec_html)
    except ValueError:
        return "0", "0"

class SerolException(Exception):
    def __init__(self, msg='Something went wrong', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
