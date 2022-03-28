from datetime import datetime, timedelta
import logging
import json
from urllib.parse import urljoin

import requests
from astropy.time import Time
from astropy.coordinates import get_moon, AltAz, get_sun
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore

from explorer.models import Body
from .request_formats import request_format, request_format_moon, format_moving_object, \
    best_observing_time, moon_coords, format_sidereal_object

logger = logging.getLogger(__name__)


def convert_requestid(requestid, token):
    '''
    Get status of Requestgroup from the Observing Portal API
    Pass sub-request ID back and replace this on the model if COMPLETED
    '''
    if '[' in requestid:
        return False, "Already ported"
    if not requestid:
        return False, "No request ID provided"

    headers = {'Authorization': 'Token {}'.format(token)}
    url = urljoin(settings.PORTAL_REQUESTGROUP_API, str(requestid))

    try:
        r = requests.get(url, headers=headers, timeout=20.0)
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logger.error(msg)
        params['error_msg'] = msg
        return False, msg

    if r.status_code in [200,201]:
        req = r.json()
        logger.debug('Request {} is {}'.format(req['id'], req['requests'][0]['state']))
        return [j['id'] for j in req['requests']], "Success"
    else:
        logger.error("Could not send request: {}".format(r.content))
        return False, "Could not send request"

def get_observation_status(requestid, token):
    '''
    Get status of Requestgroup from the Observing Portal API
    Pass sub-request ID back and replace this on the model if COMPLETED
    '''
    if not requestid:
        return False, "No request ID provided"

    headers = {'Authorization': 'Token {}'.format(token)}
    url = urljoin(settings.PORTAL_REQUEST_API, str(requestid))
    try:
        r = requests.get(url, headers=headers, timeout=20.0)
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logger.error(msg)
        params['error_msg'] = msg
        return False, msg

    if r.status_code in [200,201]:
        req = r.json()
        logger.debug('Request {} is {}'.format(req['id'], req['state']))
        return req['id'], req['state']
    else:
        logger.error("Could not send request: {}".format(r.content))
        return False, r.content

def get_observation_frameid(requestid, token):
    '''
    Get status of RequestID from the Portal API
    '''
    if not requestid:
        return False, "No request ID provided"

    headers = {'Authorization': 'Token {}'.format(token)}
    url = f"{settings.ARCHIVE_FRAMES_URL}?limit=1&offset=0&ordering=-id&REQNUM={requestid}"
    try:
        r = requests.get(url, headers=headers, timeout=20.0)
    except requests.exceptions.Timeout:
        msg = "Archive API timed out"
        logger.error(msg)
        return False

    if r.status_code in [200,201]:
        resp = r.json()
        if len(resp['results']) > 0:
            frameid = resp['results'][0]['id'];
            return frameid
        else:
            logger.error("No frames found for {}".format(requestid))
            return False
    else:
        logger.error("Could not send request: {}".format(r.content))
        return False

def submit_observation_request(params, token):
    '''
    Send the observation parameters and the authentication cookie to the Scheduler API
    '''
    headers = {'Authorization': 'Token {}'.format(token)}
    if settings.SCHEDULE_DEBUG:
        url = settings.PORTAL_VALIDATE_API
        logging.debug('Using Validate API')
    else:
        url = settings.PORTAL_REQUESTGROUP_API
    logging.debug('Submitting request')
    try:
        r = requests.post(url, json=params, headers=headers, timeout=20.0)
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logging.error(msg)
        params['error_msg'] = msg
        return False, msg, False

    if r.status_code in [200,201] and not settings.SCHEDULE_DEBUG:
        logging.debug('Submitted request')
        return True, [req['id'] for req in r.json()['requests']], r.json()['id']
    else:
        logging.error("Could not send request: {}".format(r.content))
        return False, r.json()['requests'], False

def process_observation_request(params):
    if params['target_type'] == 'moon':
        obs_params = auto_schedule(proposal=params['proposal'])
        target_name = 'Moon'
    else:
        if params['target_type'] == 'moving':
            target, filters = format_moving_object(params['object_name'])
            params['filters'] = filters
        else:
            target = format_sidereal_object(params['object_name'], params['object_ra'], params['object_dec'])
        target_name = target['name']
        obs_params = request_format(target, params['start'], params['end'], params['filters'], params['proposal'], params['aperture'])

    resp_status, resp_msg, resp_group = submit_observation_request(params=obs_params, token=params['token'])
    return resp_status, resp_msg, target_name, resp_group

def auto_schedule(proposal):
    siteset = ['ogg','coj','lsc','tfn']
    now = datetime.utcnow()
    params_list = []
    dates = []
    for site in siteset:
        dates.extend(best_observing_time(site))
    dates = sorted(dates, key=lambda element: (element[0], -element[1]))

    # Choose top 4
    for date in dates[0:4]:
        time, alt, loc, site = date
        coords = get_moon(time, loc)
        start = time.datetime - timedelta(seconds=60)
        end = time.datetime + timedelta(seconds=180)
        req_params = {'start':start,'end':end,'ra':coords.ra.value, 'dec':coords.dec.value, 'site':site}
        params_list.append(req_params)
    params = request_format_moon(params_list, proposal)
    return params
