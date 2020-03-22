import os
from os import system
from PIL import Image
from osgeo import gdal
import numpy as np
import glob

ALLOWED_EXTENSIONS = set(['txt', 'TIF'])

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def read_image(imgSample):
    img = Image.open(imgSample)
    return img

def read_metadata(pathMetadata):
    f = open(pathMetadata, 'r') #Open metadata file
    radMultBand = {}
    radAddBand = {}
    # k1ConstantBand = {}
    # k2ConstantBand = {}
    # tempKelvin = {}
    # tempCelcius = {}

    for line in f:
        if (line.find ("RADIANCE_MULT_BAND") >= 0 ):
            s = line.split("=") # Split by equal sign
            the_band = int(s[0].split("_")[3]) # Band number as integer
            if the_band in [4, 5, 10, 11]: # Is this one of the bands we want?
                radMultBand[the_band] = float ( s[-1] ) # Get constant as float
        elif (line.find ("RADIANCE_ADD_BAND") >= 0 ):
            s = line.split("=")
            the_band = int(s[0].split("_")[3])
            if the_band in [4, 5, 10, 11]:
                radAddBand[the_band] = float ( s[-1] )

    return radMultBand, radAddBand

def get_reflectance(listRaster, radMultBand, radAddBand):
    reflectance = {}
    proj = None
    geotrans = None
    row = None
    col = None

    for raster in listRaster:
        gdal_dataset = gdal.Open(raster, gdal.GA_ReadOnly)
        rasterBand = np.array(gdal_dataset.GetRasterBand(1).ReadAsArray())\
        
        proj     = gdal_dataset.GetProjection()
        geotrans = gdal_dataset.GetGeoTransform()
        row      = gdal_dataset.RasterYSize
        col      = gdal_dataset.RasterXSize

        # Convert Digital Numbers (DN) to Top Of Atmosphere (TOA) Reflectance
        s1 = raster.split("\\")[-1] # Split to obtain file name
        s2 = int(s1.split("_")[-1].split(".")[0][1:]) # Split to obtain band number as integer
        reflectance[s2] = np.add(np.multiply(rasterBand, radMultBand[s2]), radAddBand[s2])

        # Obtain at-satellite brightness temperature for band 10 and 11
        # if s2 in [10, 11]:
        #     tempKelvin[s2] = np.true_divide(k2ConstantBand[s2], np.log(np.add(np.true_divide(k1ConstantBand[s2], L[s2]), 1)))
        #     tempCelcius[s2] = np.subtract(tempKelvin[s2], 273.15)

    return reflectance, proj, geotrans, row, col

def clip_area(rasterPath, outputPath):
    cutline = r"D:\flask-dashboard-atlantis\shapefile\StudyArea.shp"
    filename = rasterPath.split("\\")[-1]
    output = outputPath + "/CLIP_" + filename
    os.system('gdalwarp -of GTiff -cutline  {} -cl StudyArea -crop_to_cutline {} {}'.format(cutline, rasterPath, output))

# Obtain NDVI value
def get_NDVI(reflectance):
    return np.true_divide(np.subtract(reflectance[5], reflectance[4]), np.add(reflectance[5], reflectance[4]))

# Classify CWSI
def classify_NDVI(data):
    vegetationLevel = np.zeros((275, 257), dtype=int)

    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] < 0.6:                # No vegetation
                vegetationLevel[i][j] = 1
            elif data[i][j] < 0.7:              # Low vegetation
                vegetationLevel[i][j] = 2
            elif data[i][j] < 0.8:              # Medium vegetation
                vegetationLevel[i][j] = 3
            else:                               # High vegetation
                vegetationLevel[i][j] = 4
    
    return vegetationLevel

# Save result as tif file
def save_as_tif(data, outputPath, name, proj, geotrans, row, col):
    output_path = outputPath + name
    driver   = gdal.GetDriverByName("GTiff")
    outdata  = driver.Create(output_path, col, row, 1, gdal.GDT_Float32)
    outband  = outdata.GetRasterBand(1)
    outband.SetNoDataValue(-9999)
    outband.WriteArray(data)
    # Georeference the image
    outdata.SetGeoTransform(geotrans)
    # Write projection information
    outdata.SetProjection(proj)
    outdata.FlushCache()
    outdata = None

def give_color_to_tif(path, name):
    filename = path + name
    ds = gdal.Open(filename, 1)
    band = ds.GetRasterBand(1)

    # create color table
    colors = gdal.ColorTable()

    # set color for each value
    colors.SetColorEntry(1, (44, 130, 201))
    colors.SetColorEntry(2, (44, 201, 144))
    colors.SetColorEntry(3, (238, 230, 87))
    colors.SetColorEntry(4, (252, 96, 66))

    # set color table and color interpretation
    band.SetRasterColorTable(colors)
    band.SetRasterColorInterpretation(gdal.GCI_PaletteIndex)

    # close and save file
    del band, ds