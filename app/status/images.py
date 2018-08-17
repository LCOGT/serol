from astropy.io import fits
#from astroscrappy import detect_cosmics
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
    url = "{}{}".format(settings.PORTAL_REQUEST_API, request_id)
    state, req = lco_api_call(url, settings.PORTAL_TOKEN)
    if not state:
        logger.error('Failed')
        return
    if req['state'] == 'COMPLETED':
        subreq_id = req['id']
        url = "{}?REQNUM={}&ordering=-id".format(settings.ARCHIVE_FRAMES_URL, subreq_id)
        success, r = lco_api_call(url, settings.ARCHIVE_TOKEN)
        if success:
            logger.debug('Downloading {}'.format(req['id']))
            dl_status = dl_sort_data_files(r, out_dir)
            if not dl_status:
                logger.debug('No files available')
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
    rlevels = {'91':[],'11':[],'0':[]}
    raw = False
    files = []
    # Make subdirectory
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    for res in r['results']:
        rl = str(res['RLEVEL'])
        if rl not in ['91','11','0']:
            logger.debug("Ancient pipeline product {}".format(rl))
            continue
        rlevels[rl].append({'filename':res['filename'],'url':res['url']})
    if (len(rlevels['91']) >= len(rlevels['11'])) and len(rlevels['91']) > 0:
        files = rlevels['91']
    elif (len(rlevels['11']) >= len(rlevels['0'])) and len(rlevels['11']) > 0:
        files = rlevels['11']
    else:
        logger.debug("No Image files available")
        return False
    for response in files:
        out_file = os.path.join(out_path, response['filename'])
        download_file(out_file, response['url'])
    return True

def write_clean_data(filelist):
    '''
    Overwrite FITS files with cleaned and scaled data
    - Data is read into uncompressed FITS file to remove dependency on FPack
    '''
    img_list =[]
    for file_in in filelist:
        data, hdrs = fits.getdata(file_in, header=True)
        filtr = hdrs['filter']
        new_filename = file_in.replace(".fits", "-{}.fits".format(filtr))
        data = clean_data(data)
        hdu = fits.PrimaryHDU(data, header=hdrs)
        hdu.writeto(new_filename)
        img_list.append(new_filename)

    return img_list

def reproject_files(ref_image, images_to_align, tmpdir='temp/'):
    identifications = make_transforms(ref_image, images_to_align[1:])
    hdu = fits.open(ref_image)
    data = hdu[1].data
    outputshape = shape(data)

    for id in identifications:
        if id.ok:
            affineremap(id.ukn.filepath, id.trans, shape=(outputshape[1],outputshape[0]), outdir=tmpdir)

    aligned_images = sorted(glob(tmpdir+"/*_affineremap.fits"))

    img_list = [ref_image]+aligned_images
    if len(img_list) < 3:
        logging.error('Error creating image: Only {} source files'.format(len(img_list)))
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
    median_val = median(data)
    data[data<0.]=median_val
    # Run astroScrappy to remove pesky cosmic rays
    logger.debug('--- Begin CR removal ---')
    #data = remove_cr(data)
    logger.debug('Median=%s' % median_val)
    logger.debug('Max after median=%s' % data.max())
    return data

def sort_files_for_colour(file_list, colour_template):
    colours = {v:k for k,v in colour_template.items()}
    for f in file_list:
        data, hdrs = fits.getdata(f, header=True)
        filtr = hdrs['filter']
        order = colour_template.get(filtr, None)
        if not order:
            logger.debug('{} is not a recognised colour filter'.format(filtr))
            return False
        colours[order] = f
    file_list = [colours[str(i)] for i in range(1,4)]
    assert len(file_list) == 3

    return file_list

def make_request_image(request_id, targetname, category=None, name=None):
    image_status = 0
    try:
        tmp_dir = os.path.join(settings.TMP_DIR,request_id)
    except AttributeError:
        tmp_dir = mkdtemp()
    resp = get_archive_data(tmp_dir, request_id)
    if not resp:
        logger.error('Failed to get data')
        shutil.rmtree(tmp_dir)
        return False, image_status

    if not name:
        name = "{}-{}.jpg".format(targetname.replace(" ",""), request_id)


    img_list = sorted(glob(os.path.join(tmp_dir,"*.fz")))
    new_filepath = os.path.join(settings.IMAGE_ROOT,name)
    num_files = len(img_list)
    if num_files == 0:
        return False, image_status
    logger.debug("{} files downloaded".format(num_files))
    if category == '1.1':
        r = planet_process(infile=img_list[0],outfile=new_filepath, planet=targetname)
        image_status = 2
    else:
        if len(img_list) == 3:
            logger.debug('Reprojecting {} files'.format(len(img_list)))
            img_list = reproject_files(img_list[0], img_list, tmp_dir)
        img_list = write_clean_data(img_list)
        logger.debug('Sorting for colour')
        if len(img_list) != 3:
            logger.debug('Creating colour image')
            r = fits_to_jpg(img_list[0], new_filepath, width=1000, height=1000)
            image_status = 2
        else:
            img_list = sort_files_for_colour(img_list, colour_template=settings.COLOUR_TEMPLATE)
            r = fits_to_jpg(img_list, new_filepath, width=1000, height=1000, color=True)
            image_status = 1
    if r:
        shutil.rmtree(tmp_dir)
        return new_filepath, image_status
    else:
        logger.error('Failed to make image for {}'.format(request_id))
        return False, image_status

def check_data_balance(header):
    '''
    Before attempting to make a colour image, make sure each image has actual data in it
    ** Not implemented yet **
    '''
    if header.get('L1MEDIAN', 0) > 100:
        return True
    else:
        return False
