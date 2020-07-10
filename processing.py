# Flask modules
from werkzeug.utils      import secure_filename

# App modules
from app                 import app

# Processing modules
import glob
import numpy as np
import os
import pandas as pd
import statistics
import math
from os                  import system
from osgeo               import gdal
from pandas              import DataFrame
from PIL                 import Image
from sklearn             import metrics
from sklearn.ensemble    import RandomForestRegressor

# Return TRUE if uploaded file is in txt/TIF format
ALLOWED_EXTENSIONS = set(['txt', 'TIF'])

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Save file in temporary folder
def save_as_temporary(inputFile):
    filename = secure_filename(inputFile.filename)
    outputPath = os.path.join(app.instance_path, 'tmp', filename) 
    inputFile.save(outputPath)
    return outputPath

# Clip input raster with farm shapefile to obtain area of study
def clip_area(rasterPath, outputPath):
    cutline = r"D:\flask-dashboard-atlantis\shapefile\\Lahan300.shp"
    filename = rasterPath.split("\\")[-1]
    output = outputPath + "/CLIP_" + filename
    os.system('gdalwarp -of GTiff -cutline  {} -cl Lahan300 -crop_to_cutline {} {}'.format(cutline, rasterPath, output))
    return output

# Get radiance multiplication and add constant from metadata file
def get_metadata(pathMetadata):
    f = open(pathMetadata, 'r')
    radMultBand = {}
    radAddBand = {}
    refMultBand = {}
    refAddBand = {}
    k1ConstantBand = {}
    k2ConstantBand = {}
    sunElevation = 0

    for line in f:
        if (line.find ("RADIANCE_MULT_BAND") >= 0 ):
            s = line.split("=")
            the_band = int(s[0].split("_")[3])
            if the_band in [10, 11]:
                radMultBand[the_band] = float ( s[-1] )
        elif (line.find ("RADIANCE_ADD_BAND") >= 0 ):
            s = line.split("=")
            the_band = int(s[0].split("_")[3])
            if the_band in [10, 11]:
                radAddBand[the_band] = float ( s[-1] )
        elif (line.find ("K1_CONSTANT_BAND") >= 0 ):
            s = line.split("=")
            the_band = int(s[0].split("_")[3])
            if the_band in [10, 11]:
                k1ConstantBand[the_band] = float ( s[-1] )
        elif (line.find ("K2_CONSTANT_BAND") >= 0 ):
            s = line.split("=")
            the_band = int(s[0].split("_")[3])
            if the_band in [10, 11]:
                k2ConstantBand[the_band] = float ( s[-1] )
        elif (line.find ("REFLECTANCE_MULT_BAND") >= 0 ):
            s = line.split("=")
            the_band = int(s[0].split("_")[3])
            if the_band in [4, 5]:
                refMultBand[the_band] = float ( s[-1] )
        elif (line.find ("REFLECTANCE_ADD_BAND") >= 0 ):
            s = line.split("=")
            the_band = int(s[0].split("_")[3])
            if the_band in [4, 5]:
                refAddBand[the_band] = float ( s[-1] )
        elif (line.find ("SUN_ELEVATION") >= 0 ):
            s = line.split("=")
            sunElevation = float ( s[-1] )

    return radMultBand, radAddBand, refMultBand, refAddBand, k1ConstantBand, k2ConstantBand, sunElevation

# Get Top of Atmosphere (TOA) spectral radiance from input raster
# with obtained radiance constant from metadata file
def get_radiance(listRaster, pathMetadata):
    radiance = {}
    reflectance = {}
    tempKelvin = {}
    tempCelcius = {}
    radMultBand, radAddBand, refMultBand, refAddBand, k1ConstantBand, k2ConstantBand, sunElevation = get_metadata(pathMetadata)

    for raster in listRaster:
        gdal_dataset = gdal.Open(raster, gdal.GA_ReadOnly)
        rasterBand = np.array(gdal_dataset.GetRasterBand(1).ReadAsArray())

        s1 = raster.split("\\")[-1]                         # Split to obtain file name
        s2 = int(s1.split("_")[-1].split(".")[0][1:])       # Split to obtain band number as integer

        if s2 in [10, 11]:
            # Convert Digital Numbers (DN) to Top Of Atmosphere (TOA) Radiance
            radiance[s2] = np.add(np.multiply(rasterBand, radMultBand[s2]), radAddBand[s2])
            # Obtain at-satellite brightness temperature for band 10 and 11
            tempKelvin[s2] = np.true_divide(k2ConstantBand[s2], np.log(np.add(np.true_divide(k1ConstantBand[s2], radiance[s2]), 1)))
            tempCelcius[s2] = np.subtract(tempKelvin[s2], 273.15)
        elif s2 in [4, 5]:
            # Convert Digital Numbers (DN) to Top Of Atmosphere (TOA) Radiance
            reflectance[s2] = np.true_divide(np.add(np.multiply(rasterBand, refMultBand[s2]), refAddBand[s2]), math.sin(sunElevation))

    return radiance, reflectance, tempCelcius

# Obtain NDVI value and save the result as an image in PNG
# Return NDVI as numpy array
def get_NDVI(path, pathMetadata):
    listRaster = glob.glob(path + "/*.tif")
    radiance, reflectance, tempCelcius = get_radiance(listRaster, pathMetadata)
    NDVI = np.true_divide(np.subtract(reflectance[5], reflectance[4]), np.add(reflectance[5], reflectance[4]))
    # classNDVI = classify_NDVI(NDVI)
    # save_as_tif(NDVI, path, "/NDVI.TIF", proj, geotrans, row, col)
    # give_color_to_tif(path, "/NDVI.TIF")

    # img_path = path + "//NDVI.TIF"
    norm = (NDVI.astype(np.float)-NDVI.min())*255.0 / (NDVI.max()-NDVI.min())
    pil_img = Image.fromarray(norm)
    output_path = "app\\static\\assets\\img\\NDVI.png"
    pil_img.convert('L').save(output_path)

    return NDVI

# Obtain CWSI value
def get_CWSI(filename, path, pathMetadata, pathWaterVapor):
    listRaster = glob.glob(path + "/*.tif")
    radiance, reflectance, tempCelcius = get_radiance(listRaster, pathMetadata)
    NDVI = np.true_divide(np.subtract(reflectance[5], reflectance[4]), np.add(reflectance[5], reflectance[4]))
    
    # Obtain emissivity (E) from NDVI Threshold-Based Models (Skokovic et al.)
    Pv = np.power(np.true_divide(np.subtract(NDVI, 0.2), 0.3), 2)
    E10 = np.zeros((50, 78))
    E11 = np.zeros((50, 78))
    for i in range(len(NDVI)):
        for j in range(len(NDVI[i])):
            if NDVI[i][j] < 0.2:
                E10[i][j] = 0.979 - 0.046 * reflectance[4][i][j]
                E11[i][j] = 0.982 - 0.027 * reflectance[4][i][j]
            elif NDVI[i][j] <= 0.5:
                E10[i][j] = 0.987 * Pv[i][j] + 0.971 * (1 - Pv[i][j])
                E11[i][j] = 0.989 * Pv[i][j] + 0.977 * (1 - Pv[i][j])
            else:
                E10[i][j] = 0.987
                E11[i][j] = 0.989
    
    # Get water vapor content
    df = pd.read_csv(pathWaterVapor)
    w = df.iloc[978][2922]
    if w > 10:
        w = 3.86

    # Calculate tau 10 and 11 based on mid-latitude summer region model
    tau10 = -0.0164*(w**2) - 0.04203*w + 0.9715
    tau11 = -0.01218*(w**2) - 0.07735*w + 0.9603

    # Obtain L
    L10 = np.subtract(np.multiply(0.4464, tempCelcius[10]), 66.61)
    L11 = np.subtract(np.multiply(0.4831, tempCelcius[11]), 71.23)

    # Obtain LST based on Split Window Algorithm (SWA) method
    A10 = np.multiply(E10, tau10)
    A11 = np.multiply(E11, tau11)
    C10 = np.multiply((1-tau10), np.add(1, np.multiply(np.subtract(1, E10), tau10)))
    C11 = np.multiply((1-tau11), np.add(1, np.multiply(np.subtract(1, E11), tau11)))
    B0 = np.true_divide(np.subtract(np.multiply(np.multiply(C11, np.subtract(np.subtract(1, A10), C10)), L10), np.multiply(np.multiply(C10, np.subtract(np.subtract(1, A11), C11)), L11)), np.subtract(np.multiply(C11, A10), np.multiply(C10, A11)))
    B1 = np.true_divide(C10, np.subtract(np.multiply(C11, A10), np.multiply(C10, A11)))
    LST = np.add(tempCelcius[10], np.add(np.multiply(B1, np.subtract(tempCelcius[10], tempCelcius[11])), B0))

    # # Obtain hot and cold pixel value
    # coldNDVI = []
    # hotNDVI = []
    # countCold = 0
    # countHot = 0

    # for i in range(len(NDVI)):
    #     for j in range(len(NDVI[i])):
    #         if NDVI[i][j] > 0.2:
    #             hotNDVI.append(LST[i][j])
    #             countHot += 1
    #         if NDVI[i][j] > 0.5:
    #             coldNDVI.append(LST[i][j])
    #             countCold += 1

    # coldNDVI.sort()
    # hotNDVI.sort(reverse = True)

    # if countCold == 0:
    #     coldPixel = 0
    # else:
    #     coldPixel = statistics.median(coldNDVI[0:countCold//10])

    # if countHot == 0:
    #     hotPixel = 0
    # else:
    #     hotPixel = statistics.median(hotNDVI[0:countHot//10])

    # Obtain CWSI
    # CWSI = np.true_divide(np.subtract(LST, coldPixel), (hotPixel - coldPixel))
    CWSI = np.true_divide(np.subtract(LST, LST.min()), (LST.max() - LST.min()))

    img = Image.new( 'RGB', (78,50), "black") # create a new black image
    pixels = img.load() # create the pixel map
    red_px = 0
    orange_px = 0

    for i in range(img.size[0]):    # for every col:
        for j in range(img.size[1]):    # for every row:
            if CWSI[j, i] < 0.2:
                pixels[i, j] = (70, 167, 177)
            elif CWSI[j, i] < 0.4:
                pixels[i, j] = (171, 221, 164)
            elif CWSI[j, i] < 0.6:
                pixels[i, j] = (255, 255, 191)
            elif CWSI[j, i] < 0.8:
                pixels[i, j] = (253, 174, 97)
                orange_px += 1
            else:
                pixels[i, j] = (215, 25, 28)
                red_px += 1

    tanggal = filename.split("_")[3]
    output_path = "app\\static\\assets\\img\\cwsi\\" + tanggal + ".png"
    output_path_db = "/static/assets/img/cwsi/" + tanggal + ".png"
    img.save(output_path, 'PNG', compress_level=0)

    ndvi_a1 = NDVI[9][36]
    ndvi_a2 = NDVI[8][44]
    ndvi_b1 = NDVI[14][49]
    ndvi_b2 = NDVI[14][58]
    ndvi_c1 = NDVI[30][28]
    ndvi_c2 = NDVI[30][39]
    ndvi_d1 = NDVI[24][39]
    ndvi_d2 = NDVI[30][53]
    ndvi_e1 = NDVI[38][17]
    ndvi_e2 = NDVI[37][24]

    cwsi_a1 = CWSI[9][36]
    cwsi_a2 = CWSI[8][44]
    cwsi_b1 = CWSI[14][49]
    cwsi_b2 = CWSI[14][58]
    cwsi_c1 = CWSI[30][28]
    cwsi_c2 = CWSI[30][39]
    cwsi_d1 = CWSI[24][39]
    cwsi_d2 = CWSI[30][53]
    cwsi_e1 = CWSI[38][17]
    cwsi_e2 = CWSI[37][24]

    return tanggal, output_path_db, red_px, orange_px, ndvi_a1, ndvi_a2, ndvi_b1, ndvi_b2, ndvi_c1, ndvi_c2, ndvi_d1, ndvi_d2, ndvi_e1, ndvi_e2, cwsi_a1, cwsi_a2, cwsi_b1, cwsi_b2, cwsi_c1, cwsi_c2, cwsi_d1, cwsi_d2, cwsi_e1, cwsi_e2

# Obtain red pixel and drought area change percentage since last month
def get_drought_monitoring(last_two_month_data):
    red_pixel_percent = (last_two_month_data[0][3] - last_two_month_data[1][3])*100 / last_two_month_data[1][3]
    pixel_drought_this_month = last_two_month_data[0][3] + last_two_month_data[0][4]
    pixel_drought_last_month = last_two_month_data[1][3] + last_two_month_data[1][4]
    drought_area_percent = (pixel_drought_this_month - pixel_drought_last_month)*100 / pixel_drought_last_month
    return "{:.2f}".format(red_pixel_percent), "{:.2f}".format(drought_area_percent*900/10000)

def make_dataframe(lahan, period, cwsi, ndvi):
    listCWSI1 = []
    listCWSI2 = []
    listNDVI1 = []
    listNDVI2 = []
    if lahan == "A":
        for i in cwsi:
            listCWSI1.append(i[2])
            listCWSI2.append(i[3])
        for j in ndvi:
            listNDVI1.append(j[2])
            listNDVI2.append(j[3])
    elif lahan == "B":
        for i in cwsi:
            listCWSI1.append(i[4])
            listCWSI2.append(i[5])
        for j in ndvi:
            listNDVI1.append(j[4])
            listNDVI2.append(j[5])
    elif lahan == "C":
        for i in cwsi:
            listCWSI1.append(i[6])
            listCWSI2.append(i[7])
        for j in ndvi:
            listNDVI1.append(j[6])
            listNDVI2.append(j[7])
    elif lahan == "D":
        for i in cwsi:
            listCWSI1.append(i[8])
            listCWSI2.append(i[9])
        for j in ndvi:
            listNDVI1.append(j[8])
            listNDVI2.append(j[9])
    else:
        for i in cwsi:
            listCWSI1.append(i[10])
            listCWSI2.append(i[11])
        for j in ndvi:
            listNDVI1.append(j[10])
            listNDVI2.append(j[11])
    for i in range(0, 1):
        listCWSI1 = np.insert(listCWSI1, len(listCWSI1), np.nan)
        listCWSI2 = np.insert(listCWSI2, len(listCWSI2), np.nan)
        listNDVI1 = np.insert(listNDVI1, len(listNDVI1), np.nan)
        listNDVI2 = np.insert(listNDVI2, len(listNDVI2), np.nan)
    dataframe1 = DataFrame()
    dataframe2 = DataFrame()
    for i in range(3,0,-1):
        dataframe1['CWSI-'+str(i)] = pd.Series(listCWSI1).shift(i)
        dataframe2['CWSI-'+str(i)] = pd.Series(listCWSI2).shift(i)
    for i in range(3,0,-1):
        dataframe1['NDVI-'+str(i)] = pd.Series(listNDVI1).shift(i)
        dataframe2['NDVI-'+str(i)] = pd.Series(listNDVI2).shift(i)
    if period == "1 bulan":
        dataframe1['CWSI'] = pd.Series(listCWSI1)
        dataframe2['CWSI'] = pd.Series(listCWSI2)
    elif period == "2 bulan":
        dataframe1['CWSI'] = pd.Series(listCWSI1).shift(-1)
        dataframe2['CWSI'] = pd.Series(listCWSI2).shift(-1)
    else:
        dataframe1['CWSI'] = pd.Series(listCWSI1).shift(-2)
        dataframe2['CWSI'] = pd.Series(listCWSI2).shift(-2)
    dataframe = dataframe1
    dataframe1 = dataframe1.dropna()
    dataframe2 = dataframe2.dropna()
    df_row_reindex = pd.concat([dataframe1, dataframe2], ignore_index=True)
    return df_row_reindex, dataframe

def predict_cwsi(lahan, period, cwsi, ndvi):
    df_row_reindex, listCWSI1 = make_dataframe(lahan, period, cwsi, ndvi)
    array = df_row_reindex.values
    X = array[:,0:6]
    y = array[:,-1]
    regressor = RandomForestRegressor(n_estimators=400, random_state=1)
    regressor.fit(X, y)
    y_pred = regressor.predict(listCWSI1.values[3:,0:6])
    if period == "1 bulan":
        for i in range(0, 3):
            y_pred = np.insert(y_pred, 0, np.nan)
    elif period == "2 bulan":
        for i in range(0, 4):
            y_pred = np.insert(y_pred, 0, np.nan)
    else:
        for i in range(0, 5):
            y_pred = np.insert(y_pred, 0, np.nan)
    return y_pred

def predict_cwsi_no_ndvi(lahan, period, cwsi, ndvi):
    df_row_reindex, listCWSI1 = make_dataframe(lahan, period, cwsi, ndvi)
    array = df_row_reindex.values
    X = array[:,0:3]
    y = array[:,-1]
    regressor = RandomForestRegressor(n_estimators=400, random_state=1)
    regressor.fit(X, y)
    y_pred = regressor.predict(listCWSI1.values[3:,0:3])
    if period == "1 bulan":
        for i in range(0, 3):
            y_pred = np.insert(y_pred, 0, np.nan)
    elif period == "2 bulan":
        for i in range(0, 4):
            y_pred = np.insert(y_pred, 0, np.nan)
    else:
        for i in range(0, 5):
            y_pred = np.insert(y_pred, 0, np.nan)
    return y_pred

# Classify
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