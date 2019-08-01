from astropy.io import fits
from astroscrappy import detect_cosmics
from django.conf import settings
from fits2image.conversions import fits_to_jpg
from glob import glob
from fits_align.align import affineremap
from fits_align.ident import make_transforms
from numpy import shape, median
from tempfile import mkdtemp
import logging
import os
import requests
import shutil
import six

from memory_profiler import profile

from status.planet import planet_process

logger = logging.getLogger(__name__)

def lco_api_call(url, token):
    '''
    Get status of RequestID from the Valhalla API
    '''
    headers = {'Authorization': 'Token {}'.format(token)}
    try:
        r = requests.get(url, headers=headers, timeout=20.0)
    except requests.exceptions.Timeout:
        msg = "Observing portal API timed out"
        logger.error(msg)
        params['error_msg'] = msg
        return False, msg

    if r.status_code in [200,201]:
        logger.debug('Recieved data')
        return True, r.json()
    else:
        logger.error("Could not send request: {}".format(r.content))
        return False, r.content

def get_archive_data(out_dir, request_id):
    # Only look for data which has completed
    url = "{}?REQNUM={}&ordering=-id".format(settings.ARCHIVE_FRAMES_URL, request_id)
    success, r = lco_api_call(url, settings.ARCHIVE_TOKEN)
    if success:
        logger.debug('Downloading {}'.format(request_id))
        dl_status = dl_sort_data_files(r, out_dir)
        if not dl_status:
            logger.debug('No files available')
            return False
    else:
        logger.debug('API call failed')
        return False
    return True

def get_thumbnail(out_file, frameid):
    # Only look for data which has completed
    url = settings.THUMB_SERVICE.format(frameid)
    success, r = lco_api_call(url, settings.ARCHIVE_TOKEN)
    if success:
        logger.debug('Downloading {}'.format(request_id))
        dl_status = download_file(out_file, r['url'])
        if not dl_status:
            logger.debug('No colour image available')
            return False
    else:
        logger.debug('API call failed')
        return False
    return True

def download_file(out_file, url):
    logger.debug("Downloading: {}".format(out_file))
    dt = requests.get(url)
    f = open(out_file, 'wb')
    f.write(dt.content)
    f.close()
    return

def dl_sort_data_files(r, out_path):
    '''
    Downloads the highest reduction level available
    '''
    rlevels = {'91':[],'0':[]}
    raw = False
    files = []
    # Make subdirectory
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    for res in r['results']:
        rl = str(res['RLEVEL'])
        if rl not in ['91','0']:
            logger.debug("Ancient pipeline product {}".format(rl))
            continue
        rlevels[rl].append({'filename':res['filename'],'url':res['url']})
    if len(rlevels['91']) == 0:
        logger.debug("No Image files available")
        return False
    for response in rlevels['91']:
        out_file = os.path.join(out_path, response['filename'])
        download_file(out_file, response['url'])
    return True

def write_clean_data(filelist):
    '''
    Overwrite FITS files with cleaned and scaled data
    - Data is read into uncompressed FITS file to remove dependency on FPack
    '''
    img_list =[]
    for i, file_in in enumerate(filelist):
        data, hdrs = fits.getdata(file_in, header=True)
        filtr = hdrs['filter']
        path = os.path.split(file_in)[0]
        new_filename = os.path.join(path,"{}.fits".format(filtr))
        data = clean_data(data)
        hdu = fits.PrimaryHDU(data, header=hdrs)
        hdu.writeto(new_filename)
        img_list.append(new_filename)

    del hdu
    del data
    return img_list

def reproject_files(ref_image, images_to_align, tmpdir):
    logger.info("Reprojecting data")
    identifications = make_transforms(ref_image, images_to_align[1:3])

    aligned_images = []
    for id in identifications:
        if id.ok:
            aligned_img = affineremap(id.ukn.filepath, id.trans, outdir=tmpdir)
            aligned_images.append(aligned_img)

    img_list = [ref_image]+aligned_images
    if len(img_list) != 3:
        return images_to_align
    return img_list


def remove_cr(data):
    '''
    Removes high value pixels which are presumed to be cosmic ray hits.
    '''
    m, imdata = detect_cosmics(data, readnoise=20., gain=1.4, sigclip=5., sigfrac=.5, objlim=6.)
    return imdata

def clean_data(data):
    '''
    - Remove bogus (i.e. negative) pixels
    - Remove Cosmic Rays
    - Subtract the median sky value
    '''
    # Level out the colour balance in the frames
    logger.info('--- Begin CR removal ---')
    median_val = median(data)
    data[data<0.]=median_val
    # Run astroScrappy to remove pesky cosmic rays
    data = remove_cr(data)
    logger.debug('Median=%s' % median_val)
    logger.debug('Max after median=%s' % data.max())
    return data

def sort_files_for_colour(file_list, colour_template):
    colours = {v:k for k,v in colour_template.items()}
    for f in file_list:
        data, hdrs = fits.getdata(f, header=True)
        del data # free up memory
        filtr = hdrs['filter']
        order = colour_template.get(filtr, None)
        if not order:
            logger.debug('{} is not a recognised colour filter'.format(filtr))
            return False
        colours[order] = f
    file_list = [colours[str(i)] for i in range(1,4)]
    assert len(file_list) == 3

    return file_list


def make_request_image(filename, request_id, targetname, category=None, name=None, frameid=None):
    image_status = 0
    try:
        tmp_dir = os.path.join(settings.TMP_DIR,request_id)
    except AttributeError:
        tmp_dir = mkdtemp()
    resp = get_archive_data(tmp_dir, request_id)
    if not resp:
        logger.error('Failed to get data')
        shutil.rmtree(tmp_dir)
        return image_status

    img_list = sorted(glob(os.path.join(tmp_dir,"*.fz")))
    num_files = len(img_list)
    if num_files == 0:
        return image_status

    logger.debug("{} files downloaded".format(num_files))
    if category == '1.1':
        logger.debug("Processing planet")
        r = planet_process(infile=img_list[0], outfile=filename, planet=targetname)
        image_status = 2
    else:
        if len(img_list) == 3:
            logger.debug('Reprojecting {} files'.format(len(img_list)))
            img_list = reproject_files(img_list[0], img_list, tmp_dir)
        img_list = write_clean_data(img_list)
        logger.debug('Sorting for colour')
        if len(img_list) != 3:
            logger.debug('Creating colour image')
            r = fits_to_jpg(img_list[0], filename, width=1000, height=1000)
            if not r and frameid:
                r = get_thumbnail(filename, frameid)
            image_status = 2
        else:
            img_list = sort_files_for_colour(img_list, colour_template=settings.COLOUR_TEMPLATE)
            r = fits_to_jpg(img_list, filename, width=1000, height=1000, color=True)
            image_status = 1
    if r:
        shutil.rmtree(tmp_dir)
        return image_status
    else:
        logger.error('Failed to make image for {}'.format(request_id))
        return image_status

def check_data_balance(header):
    '''
    Before attempting to make a colour image, make sure each image has actual data in it
    ** Not implemented yet **
    '''
    if header.get('L1MEDIAN', 0) > 100:
        return True
    else:
        return False
