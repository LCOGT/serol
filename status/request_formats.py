import json
import logging
from django.conf import settings
from datetime import datetime, timedelta, timezone
import requests

from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, get_body
from astroplan import Observer
from numpy import float64
from astropy.utils import iers

from explorer.models import Body
from explorer.utils import SerolException

iers.conf.auto_download = False 

EXPOSURE = '0.5'

SITES = {
    'ogg': {'lat': 20.7075, 'lon': -156.256111,'alt':3055},
    'coj': {'lat': -31.273333, 'lon': 149.071111,'alt':1116},
    'lsc': {'lat': -30.1675, 'lon': -70.804722,'alt':2198},
    'elp': {'lat': 30.67, 'lon': -104.02,'alt':2070},
    'cpt': {'lat': -32.38, 'lon': 20.81,'alt':1460},
    'tfn': {'lat': 28.3, 'lon': -16.51,'alt':2330},
}

def request_format_moon(params, proposal, aperture='0m4'):
    '''
    Format a simple request using the schema the Scheduler understands
    '''
    constraints = {
            'max_airmass': 2.0,
            'min_lunar_distance': 0.0
        }
    reqs = []

    for param in params:
        target = {
               'name'              : f"Moon {param['site']}",
               'ra'                : param['ra'], # RA (degrees)
               'dec'               : param['dec'], # Dec (Degrees)
               'epoch'             : 2000,
               'type'              : 'ICRS'
            }

        location = {
            'telescope_class' : aperture,
            'site'            : param['site']
            }

        # f_str = json.loads(obs_filter)
        configurations = [
            {
                'type': 'EXPOSE',
                'instrument_type': settings.DEFAULT_CAMERAS[aperture],
                'target': target,
                'constraints': constraints,
                'acquisition_config': {},
                'guiding_config': {},
                'instrument_configs': [
                    {
                        "mode": "central30x30",
                        'exposure_time': EXPOSURE,
                        'exposure_count': 1,
                        'optical_elements': {
                            'filter': 'up'
                        }
                    }
                ]
            }]

        # Do the observation between these dates
        window = {
            'start' : str(param['start']),
            'end' : str(param['end'])
            }
        request = {
                'configurations': configurations,
                'windows': [window],
                'location': location,
        }
        reqs.append(request)

    request_group = {
        "name": "moon_{}".format(datetime.utcnow().strftime("%m%dt%H%M")),
        "proposal": proposal,
        "ipp_value" : 1.05,
        "operator" : "MANY",
        "observation_type": "NORMAL",
        'requests': reqs
        }

    return request_group

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
            'max_airmass': 2.0,
            'min_lunar_distance': 30.0
        }

    instconfig = []

    for f in obs_filter:
        config = {
                "mode": "central30x30",
                'exposure_time': f['exposure'],
                'exposure_count': 1,
                'optical_elements': {
                    'filter': f['name']
                    }
                }
        instconfig.append(config)

    configurations = {
        'type': 'EXPOSE',
        'instrument_type': default_camera,
        'target': target,
        'constraints': constraints,
        'acquisition_config': {},
        'guiding_config': {},
        'instrument_configs': instconfig
        }

    # Do the observation between these dates
    window = {
        'start' : start, # str(datetime)
        'end' : end, # str(datetime)
        }

    request_group = {
        "operator" : "SINGLE",
        "type" : "compound_request",
        "ipp_value" : 1.0,
        "name": "serol_{}_{}".format(target['name'], datetime.utcnow().strftime("%Y%m%d")),
        "observation_type": "NORMAL",
        "proposal": proposal,
        'requests': [{
                'configurations': [configurations],
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
    elements = fetch_orbital_elements(body.name, body.get_schema_display())
    target = {
        "name": body.name,
        "type": "ORBITAL_ELEMENTS",
        "epochofel": elements['epoch_jd'] - 2400000.5,
        "scheme": body.get_schema_display(),
        "orbinc": elements['inclination'],
        "longascnode": elements['ascending_node'],
        "argofperih": elements['argument_of_perihelion'],
        "eccentricity": elements['eccentricity']
    }
    if body.schema in [0,2]:
        target["meandist"] = elements['semimajor_axis']
        target["meananom"] = elements['mean_anomaly']
        if body.schema == 2:
            target["dailymot"] = elements['mean_daily_motion']
    elif body.schema == 1:
        target["perihdist"] = elements['perihelion_distance']
        target["epochofperih"] = elements['perihelion_date_jd'] - 2400000.5

    # Add filters to inputs
    filters = []
    for f in json.loads(body.filter_list):
        filter_item = {'name' : f, 'exposure' : body.exposuretime}
        filters.append(filter_item)

    return target, filters

def fetch_orbital_elements(name, schema):
    '''
    Fetch orbital elements from Simbad2K small body database
    '''
    url = f"https://simbad2k.lco.global/{name}?target_type=non_sidereal&scheme={schema}"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise SerolException('Could not fetch orbital elements')
    return resp.json()

def moon_coords(time, site):
    loc = EarthLocation(lat=SITES[site]['lat'], lon=SITES[site]['lon'], height=SITES[site]['alt'])
    coords = get_body(time=time,body='moon',location=loc)
    altazframe = AltAz(obstime=time,location=loc)
    earth_coords = coords.transform_to(altazframe)
    return coords, time, earth_coords.alt.value

def best_observing_time(site):
    """
    Calculate moon alt every other day over the next 14 days
    Once we have 4 dates return dates
    """
    loc = EarthLocation(lat=SITES[site]['lat'], lon=SITES[site]['lon'], height=SITES[site]['alt'])
    obs = Observer(location=loc)
    now = datetime.now(timezone.utc)
    day= timedelta(days=1)
    times = [Time(now) + day*i for i in range(1,16,2)]
    best_times = []

    for time in times:
        twilight = obs.twilight_evening_astronomical(time=time, which='nearest')
        dawn = obs.twilight_morning_astronomical(time=time, which='next')
        moonset = obs.moon_set_time(time=twilight, which='next')
        moonrise = obs.moon_rise_time(time=twilight, which='next')
        logging.debug(f"{site} - {twilight.iso} : {moonrise.iso} -> {moonset.iso}")
        if moonset > dawn and moonrise > dawn:
            logging.debug(f'New moon {twilight.iso}')
            continue
        # If the moon never rises at night, check the time isn't a weird masked array
        if type(moonrise.jd) != float64 or moonset < dawn:
            logging.debug(f'Using twilight {twilight.iso}')
            begin = twilight
        else:
            begin = moonrise
            logging.debug('Using moonrise')
        for dt in range(1,10):
            t = timedelta(seconds=1800*dt)
            if begin + t > dawn:
                logging.debug(f'{(begin+t).iso} is day time')
                continue

            alt = obs.moon_altaz(begin +t ).alt.value
            #  logging.debug(f'Alt: {alt} {(begin +t).iso}')
            if alt > 31:
                best_times.append((begin + t, alt, obs.location, site))
            if len(best_times) >= 3:
                return best_times
    return best_times
