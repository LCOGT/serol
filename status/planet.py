from PIL import Image
from astropy.io import fits
import numpy as np
from pathlib import Path

def planet_data_scale(data):
    data[data<0.]=0.
    std = np.sqrt(np.mean(data))
    cutoff = 3*std + np.mean(data)
    return data, cutoff

def scale_for_jupiter(filename):
    data = fits.getdata(filename)
    data = data.astype(np.float32)
    min_val = np.percentile(data,99.9)
    data -= min_val
    data, cutoff = planet_data_scale(data)
    data[data<cutoff] = 0.
    data = data**2.
    scaled_planet = data*256./(data.max())
    return scaled_planet

def scale_for_moons(filename):
    data = fits.getdata(filename)
    data = data.astype(np.float32)
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
    im.save(outfile, format='JPEG')
    return

def create_saturn_image(infile, outfile):
    data = fits.getdata(infile).astype(np.float32)

    min_val = np.percentile(data, 99.9)
    data -= min_val
    data[data < 0] = 0

    max_val = data.max()
    if max_val > 0:
        data = data * 255.0 / max_val

    data = np.clip(data, 0, 255).astype(np.uint8)

    im = Image.fromarray(data)

    w, h = im.size
    half_size = 200

    im = im.crop((
        w // 2 - half_size,
        h // 2 - half_size,
        w // 2 + half_size,
        h // 2 + half_size,
    ))

    im = im.transpose(Image.Transpose.ROTATE_90)
    im = im.convert("L")
    im.save(outfile, format="JPEG")

def planet_centre_coord(filename):
    # Extract photometry info for brightest object i.e. the planet
    hdu = fits.open(filename)
    x = hdu[2].data[0][0]
    y = hdu[2].data[0][1]
    return x,y

def crop_image(filename):
    im_file = Path(filename)
    if im_file.is_file():
        im = Image.open(filename)
        s = im.size
        area = (0.25*s[0], 0.25*s[1], 0.75*s[0], 0.75*s[1])
        im.crop(area).rotate(angle=270).save(filename, format='JPEG')
        return True
    else:
        return False

def planet_process(infile, outfile, planet):
    if planet.lower() in ['jupiter','uranus','mars']:
        create_jupiter_image(infile, outfile)
    elif planet.lower() == 'saturn':
        create_saturn_image(infile, outfile)
    crop_image(outfile)
    return True
