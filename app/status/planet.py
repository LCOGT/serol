from PIL import Image, ImageChops
from astropy.io import fits
import glob
import logging
import numpy as np

def planet_data_scale(data):
    data[data<0.]=0.
    std = np.sqrt(np.mean(data))
    cutoff = 3*std + np.mean(data)
    return data, cutoff

def scale_for_jupiter(filename):
    hdul = fits.open(filename)
    data = hdul[1].data
    min_val = np.percentile(data,99.9)
    data -= min_val
    data, cutoff = planet_data_scale(data)
    data[data<cutoff] = 0.
    data = data**2.
    scaled_planet = data*256./(data.max())
    return scaled_planet

def scale_for_moons(filename):
    hdul = fits.open(filename)
    data = hdul[1].data
    data[data<0.] = 0.
    data = np.arcsinh(data)
    moon_med = np.median(data)
    moon_max_val = np.percentile(data,99.95)
    data -= moon_med
    scaled_moon = data*256./(moon_max_val)
    return scaled_moon

def create_jupiter_image(infile, outfile):
    jupiter_data = scale_for_jupiter(infile)
    moons_data = scale_for_moons(infile)
    im_j = Image.fromarray(jupiter_data)
    im_m = Image.fromarray(moons_data)
    im = Image.blend(im_j.convert('RGB'), im_m.convert('RGB'), 0.4)
    if im.mode != 'L':
        im = im.convert('L')
    im.save(outfile)
    return

def create_saturn_image(infile, outfile):
    '''
    Makes a single colour Saturn image, rotating and cropping appropriately
    '''
    data = fits.getdata(infile)
    min_val = np.percentile(data,99.9)
    data -= min_val
    scaled_planet = data*256./(data.max())
    tmp_im = Image.fromarray(scaled_planet)
    tmp_im.crop((w/2-dp, h/2-dp, w/2+200, h/2+200))
    tmp_im.transpose(method=Image.ROTATE_90)
    tmp_im.convert('RGB')
    tmp_im.save(outfile)
    return


def planet_centre_coord(filename):
    # Extract photometry info for brightest object i.e. the planet
    hdu = fits.open(filename)
    x = hdu[2].data[0][0]
    y = hdu[2].data[0][1]
    return x,y

def crop_image(filename):
    im = Image.open(filename)
    area = (200, 0, 1300, 1000)
    im.crop(area).save(filename)
    return

def planet_process(infile, outfile, planet):
    if planet.lower() in ['jupiter','uranus']:
        create_jupiter_image(infile, outfile)
    elif planet.lower() == 'saturn':
        create_saturn_image(infile, outfile)
    crop_image(outfile)
    return True
