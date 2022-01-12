import rasterio
import numpy as np


def histogram(image_file):
    """Calculates the histogram for a given (single band) image file."""

    # with rasterio.open(image_file) as src:
    #     band = src.read()

    # hist, _ = np.histogram(band, bins=2)

    return ["first: ", image_file[0], " & second: ", image_file[1]]

# print(histogram("/data/MTDA/TIFFDERIVED/PROBAV_L3_S1_TOC_333M/2016/20160131/PROBAV_S1_TOC_20160131_333M_V101/PROBAV_S1_TOC_X18Y02_20160131_333M_V101_NDVI.tif"))
