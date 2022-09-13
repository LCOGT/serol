from astropy.coordinates import SkyCoord
from django.shortcuts import get_object_or_404
from django.utils.html import mark_safe
from django.templatetags.static import static

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

def target_icon(avmcode):
    avm_files = {
        '5.5' : 'explorer/images/5.5-groupofgalaxies.png' ,
        '5.1.1' : 'explorer/images/5.1.1-spiral_galaxy.png' ,
        '5.1.4' : 'explorer/images/5.1.4-elliptical_galaxy.png' ,
        '5.1.6' : 'explorer/images/5.1.6-interacting_galaxy.png' ,
        '5' : 'explorer/images/5-galaxy-icon.png' ,
        '4.1.4' : 'explorer/images/4.1.4-supernova_remnant.png' ,
        '4.1.3' : 'explorer/images/4.1.3-planetary_nebula.png' ,
        '4.1.2' : 'explorer/images/4-nebulae-icon.png' ,
        '4' : 'explorer/images/4-nebulae-icon.png' ,
        '3.6.4' : 'explorer/images/3.6.4.1-cluster-icon.png' ,
        '3.6.4.1' : 'explorer/images/3.6.4.1-cluster-icon.png' ,
        '3.6.4.2' : 'explorer/images/3.6.4.2-globular_cluster.png' ,
        '2.3' : 'explorer/images/2.3-asteroids-icon.png' ,
        '2.2' : 'explorer/images/M1C2-comet-icon.png' ,
        '1.4' : "explorer/images/1.1.1-mercury.png",
        '1.1' : 'explorer/images/M1C1-planet-icon1.png'
    }
    avm_file = avm_files.get(avmcode,'')
    if avm_file:
        return static(avm_file)
    else:
        return static('explorer/images/serol_logo_sm.png')


class SerolException(Exception):
    def __init__(self, msg='Something went wrong', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
