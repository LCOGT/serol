from datetime import datetime, timedelta
from django.conf import settings
from hashlib import md5
import glob
import logging
import os, sys
import requests

logger = logging.getLogger(__name__)

ssl_verify = True

def lco_api_call(url, headers):
    try:
        resp = requests.get(url, headers=headers, timeout=20, verify=ssl_verify)
        data = resp.json()
    except requests.exceptions.InvalidSchema as err:
        data = None
        logger.error("Request call to %s failed with: %s" % (url, err))
    except ValueError as err:
        logger.error("Request {} API did not return JSON: {}".format(url, resp.status_code))
    except requests.exceptions.Timeout:
        logger.error("Request API timed out")
    return data

def check_for_archive_images(request_id=None, token=None):
    '''
    Call Archive API to obtain all frames for request_id
    Follow links to get all frames and filter out non-reduced frames and returns
    fully-reduced data in preference to quicklook data
    '''
    reduced_data = []
    quicklook_data = []
    auth_header = {'Authorization': 'Token {}'.format(token)}

    base_url = settings.ARCHIVE_FRAMES_URL
    archive_url = '%s?limit=10&REQNUM=%s&OBSTYPE=EXPOSE' % (base_url, request_id)

    frames = []
    data = fetch_archive_frames(auth_header, archive_url, frames)
    for datum in data:
        headers_url = u'%s%d/headers' % (settings.ARCHIVE_FRAMES_URL, datum['id'])
        datum[u'headers'] = headers_url
        if datum['RLEVEL'] == 91:
            reduced_data.append(datum)
        elif datum['RLEVEL'] == 11:
            quicklook_data.append(datum)
    if len(reduced_data) >= len(quicklook_data):
        return reduced_data
    else:
        return quicklook_data

def fetch_archive_frames(auth_header, archive_url, frames):

    data = lco_api_call(archive_url, auth_header)
    if data.get('count', 0) > 0:
        frames += data['results']
        if data['next']:
            fetch_archive_frames(auth_header, data['next'], frames)

    return frames

def download_files(frames, output_path, verbose=False, dbg=False):
    '''Downloads and saves to disk, the specified files from the new Science
    Archive. Returns a list of the frames that were downloaded.
    Takes a dictionary <frames> (keyed by reduction levels and produced by
    get_frame_data() or get_catalog_data()) of lists of JSON responses from the
    archive API and downloads the files to <output_path>. Lower reduction level
    files (e.g. -e10 quicklook files) will not be downloaded if a higher
    reduction level already exists and frames will not be downloaded if they
    already exist. If [verbose] is set to True, the filename of the downloaded
    file will be printed.'''

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    downloaded_frames = []
    for reduction_lvl in frames.keys():
        logger.debug(reduction_lvl)
        frames_to_download = frames[reduction_lvl]
        for frame in frames_to_download:
            logger.debug(frame['filename'])
            filename = os.path.join(output_path, frame['filename'])
            archive_md5 = frame['version_set'][-1]['md5']
            if check_for_existing_file(filename, archive_md5, dbg, verbose) or \
                check_for_bad_file(filename):
                logger.info("Skipping existing file {}".format(frame['filename']))
            else:
                logger.info("Writing file to {}".format(filename))
                downloaded_frames.append(filename)
                with open(filename, 'wb') as f:
                    f.write(requests.get(frame['url']).content)
    return downloaded_frames
