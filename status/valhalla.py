from datetime import datetime

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
import requests
import logging
import json


logger = logging.getLogger(__name__)

def get_observation_status(requestid, token):
    '''
    Get status of RequestID from the Valhalla API
    '''
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
        logger.debug('Submitted request')
        req = r.json()
        requestid = req['requests'][0]['id']
        return requestid, req['state']
    else:
        logger.error("Could not send request: {}".format(r.content))
        return False, r.content


def process_observation_request(params, token):
    '''
    Send the observation parameters and the authentication cookie to the Scheduler API
    '''
    headers = {'Authorization': 'Token {}'.format(token)}
    url = settings.PORTAL_REQUEST_API
    try:
        r = requests.post(url, json=params, headers=headers, timeout=20.0)
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logger.error(msg)
        params['error_msg'] = msg
        return False, msg

    if r.status_code in [200,201]:
        logger.debug('Submitted request')
        return True, r.json()['id']
    else:
        logger.error("Could not send request: {}".format(r.content))
        return False, r.content

def request_format(target, start,end, obs_filter, proposal, aperture='0m4'):
    '''
    Format a simple request using the schema the Scheduler understands
    '''

    default_camera = settings.DEFAULT_CAMERAS[aperture]

# this selects any telescope on the 1 meter network
    location = {
        'telescope_class' : aperture,
        }
    molecules = []

    # f_str = json.loads(obs_filter)
    for f in obs_filter:
        molecule = {
            # Required fields
            'exposure_time'   : f['exposure'],   # Exposure time, in secs
            'exposure_count'  : 1,     # The number of consecutive exposures
            'filter'          : f['name'],            # The generic filter name
             # Optional fields. Defaults are as below.
            'type'            : 'EXPOSE',  # The type of the molecule
            'instrument_name' : default_camera, # This resolves to the main science camera on the scheduled resource
            'bin_x'           : 2,                 # Your binning choice. Right now these need to be the same.
            'bin_y'           : 2,
            'defocus'       : 0.0             # Mechanism movement of M2, or how much focal plane has moved (mm)
            }
        molecules.append(molecule)

    # Do the observation between these dates
    window = {
        'start' : start, # str(datetime)
        'end' : end, # str(datetime)
        }

    request = {
        "constraints" : {'max_airmass' : 2.0, "min_lunar_distance": 30.0,},
        "location" : location,
        "molecules" : molecules,
        "observation_note" : "Serol Request",
        "target" : target,
        "type" : "request",
        "windows" : [window],
        }

    user_request = {
        "operator" : "SINGLE",
        "requests" : [request],
        "type" : "compound_request",
        "ipp_value" : 1.0,
        "group_id": "serol_{}_{}".format(object_name, datetime.utcnow().strftime("%Y%m%d")),
        "observation_type": "NORMAL",
        "proposal": settings.PROPOSAL_CODE
        }

    return user_request

def format_sidereal_object(object_name, object_ra, object_dec):
    '''
    Format target for non-moving objects
    '''
    target = {
           'name'              : object_name,
           'ra'                : object_ra, # RA (degrees)
           'dec'               : object_dec, # Dec (Degrees)
           'epoch'             : 2000,
           'type'              : 'SIDEREAL'
        }
    return target

def format_moving_object(body_id):
    '''
    Format target for non-sidereal objects
    '''
    body = Body.objects.get(id=body_id)
    target = {
        "name": body.name,
        "type": "NON_SIDEREAL",
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
            target["dailymotion"] = body.dailymotion
    elif body.schema == 1:
        target["perihdist"] = body.perihdist
        target["epochofperih"] = body.epochofperih

    return target
