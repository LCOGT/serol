import json
from django.conf import settings
from datetime import datetime, timedelta
from astropy.time import Time
from astropy.coordinates import EarthLocation, get_moon, AltAz, get_sun
from astroplan import Observer

from explorer.models import Body


EXPOSURE = '2.0'
DEFAULT_CAMERAS = { '1m0' : '1M0-SCICAM-SBIG',
                    '2m0' : '2M0-SCICAM-SPECTRAL',
                    '0m4' : '0M4-SCICAM-SBIG'
                    }
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
                'instrument_type': DEFAULT_CAMERAS[aperture],
                'target': target,
                'constraints': constraints,
                'acquisition_config': {},
                'guiding_config': {},
                'instrument_configs': [
                    {
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
            'max_airmass': 1.6,
            'min_lunar_distance': 30.0
        }

    instconfig = []

    for f in obs_filter:
        config = {
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

def moon_coords(time, site):
    loc = EarthLocation(lat=SITES[site]['lat'], lon=SITES[site]['lon'], height=SITES[site]['alt'])
    coords = get_moon(time,loc)
    altazframe = AltAz(obstime=time,location=loc)
    earth_coords = coords.transform_to(altazframe)
    return coords, time, earth_coords.alt.value

def best_observing_time(site):
    """
    Calculate moon alt every other day over the next 7 days
    Once we have 4 dates return dates
    """
    loc = EarthLocation(lat=SITES[site]['lat'], lon=SITES[site]['lon'], height=SITES[site]['alt'])
    obs = Observer(location=loc)
    now = datetime.utcnow()
    day= timedelta(days=1)
    times = [Time(now) + day*i for i in range(0,7,2)]
    best_times = []

    for time in times:
        twilight = obs.twilight_evening_astronomical(time=time, which='next')
        moonset = obs.moon_set_time(time=time, which='next')
        for dt in range(1,10):
            t = timedelta(seconds=3600*dt)
            if twilight +t > moonset:
                continue
            alt = obs.moon_altaz(twilight +t ).alt.value
            if alt > 31:
                best_times.append((twilight + t, alt, obs.location, site))
            if len(best_times) >= 4:
                break
    return best_times
