from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
import requests
import logging
import json

from explorer.models import Body


logger = logging.getLogger(__name__)

def get_observation_status(requestid, token):
    '''
    Get status of Requestgroup from the Observing Portal API
    Pass sub-request ID back and replace this on the model if COMPLETED
    '''
    if not requestid:
        return False, "No request ID provided"

    headers = {'Authorization': 'Token {}'.format(token)}
    url = settings.PORTAL_REQUEST_API + requestid
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
        return req['requests'][0]['id'], req['requests'][0]['state']
    else:
        logger.error("Could not send request: {}".format(r.content))
        return False, r.content

def get_observation_frameid(requestid, token):
    '''
    Get status of RequestID from the Valhalla API
    '''
    if not requestid:
        return False, "No request ID provided"

    headers = {'Authorization': 'Token {}'.format(token)}
    url = "{}?limit=1&offset=0&ordering=-id&REQNUM={}".format(settings.ARCHIVE_FRAMES_URL, requestid)
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
    url = settings.PORTAL_REQUEST_API
    logging.debug('Submitting request')
    try:
        r = requests.post(url, json=params, headers=headers, timeout=20.0)
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logging.error(msg)
        params['error_msg'] = msg
        return False, msg

    if r.status_code in [200,201]:
        logging.debug('Submitted request')
        return True, r.json()['id']
    else:
        logging.error("Could not send request: {}".format(r.content))
        return False, r.content

def process_observation_request(params):
    if params['target_type'] == 'moving':
        target, filters = format_moving_object(params['object_name'])
        params['filters'] = filters
    else:
        target = format_sidereal_object(params['object_name'], params['object_ra'], params['object_dec'])
    obs_params = request_format(target, params['start'], params['end'], params['filters'], params['proposal'], params['aperture'])
    resp_status, resp_msg = submit_observation_request(params=obs_params, token=params['token'])
    return resp_status, resp_msg, target['name']

def request_format(target, start, end, obs_filter, proposal, aperture='0m4'):
    '''
    Format a simple request using the schema the Scheduler understands
    '''

    default_camera = settings.DEFAULT_CAMERAS[aperture]

# this selects any telescope on the 1 meter network
    location = {
        'telescope_class' : aperture,
        }

    constraints = {
            'max_airmass': 1.6,
            'min_lunar_distance': 30.0
        }

    configurations = []

    for f in obs_filter:
        config = {
            'type': 'EXPOSE',
            'instrument_type': default_camera,
            'target': target,
            'constraints': constraints,
            'acquisition_config': {},
            'guiding_config': {},
            'instrument_configs': [{
                'exposure_time': f['exposure'],
                'exposure_count': 1,
                'optical_elements': {
                    'filter': f['name']
                    }
                }]
            }
        configurations.append(config)

    # Do the observation between these dates
    window = {
        'start' : start, # str(datetime)
        'end' : end, # str(datetime)
        }

    request_group = {
        "operator" : "SINGLE",
        "type" : "compound_request",
        "ipp_value" : 1.05,
        "name": "serol_{}_{}".format(target['name'], datetime.utcnow().strftime("%Y%m%d")),
        "observation_type": "NORMAL",
        "proposal": proposal,
        'requests': [{
                'configurations': configurations,
                'windows': [window],
                'location': location,
            }]
        }

    return request_group

def format_sidereal_object(object_name, object_ra, object_dec):
    '''
    Format target for non-moving objects
    '''
    target = {
           'name'              : object_name,
           'ra'                : object_ra, # RA (degrees)
           'dec'               : object_dec, # Dec (Degrees)
           'epoch'             : 2000,
           'type'              : 'ICRS'
        }
    return target

def format_moving_object(tid):
    '''
    Format target for non-sidereal objects
    '''
    body = Body.objects.get(id=tid)
    target = {
        "name": body.name,
        "type": "ORBITAL_ELEMENTS",
        "epochofel": body.epochofel,
        "scheme": body.get_schema_display(),
        "orbinc": body.orbinc,
        "longascnode": body.longascnode,
        "argofperih": body.argofperih,
        "eccentricity": body.eccentricity
    }
    if body.schema in [0,2]:
        target["meandist"] = body.meandist
        target["meananom"] = body.meananom
        if body.schema == 2:
            target["dailymot"] = body.dailymotion
    elif body.schema == 1:
        target["perihdist"] = body.perihdist
        target["epochofperih"] = body.epochofperih

    # Add filters to inputs
    filters = []
    for f in json.loads(body.filter_list):
        filter_item = {'name' : f, 'exposure' : body.exposuretime}
        filters.append(filter_item)

    return target, filters
