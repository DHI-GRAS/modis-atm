import re
import os
import math
import glob
import datetime
import platform
import subprocess
from xml.etree import ElementTree as ET

import numpy as np
from osgeo import gdal, osr

from . import io_utils as io_utils
from gdal_utils import gdal_binaries as gbin

# Constants
C_gdalwarp = gbin.find_gdal_exe('gdalwarp')

if platform.system() == "Windows":
    wd = os.path.dirname(os.path.abspath(__file__))
    C_daac2disk = os.path.join(wd, "dependency", "Daac2Disk_win.exe")
else:
    wd = os.path.dirname(os.path.abspath(__file__))
    C_daac2disk = os.path.join(wd, "dependency", "Daac2Disk_linux")


def reprojectModisSwath(inFilename, outFilename, projectionString):
    """Reproject MODIS swath"""
    tempFilename = os.path.join(os.path.dirname(outFilename), 'temp.tif')
    try:
        # first reproject to geographic projection
        cmd = C_gdalwarp
        cmd += ' -overwrite -dstnodata -9999 -geoloc'
        cmd += ' -t_srs "+proj=longlat +datum=WGS84 +no_defs" -r bilinear {} {}'.format(inFilename, tempFilename)

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
        for line in iter(proc.stdout.readline, ""):
            print line
        proc.wait()
        check_gdal_success(tempFilename, cmd)

        # then to the required one
        cmd = C_gdalwarp
        cmd += ' -overwrite -dstnodata -9999 -t_srs {}'.format(projectionString)
        cmd += ' -r bilinear {} {}'.format(tempFilename, outFilename)

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
        for line in iter(proc.stdout.readline, ""):
            print line
        proc.wait()
        check_gdal_success(outFilename, cmd)
    finally:
        try:
            os.remove(tempFilename)
        except (WindowsError, OSError):
            pass

def meanValueOfExtent(inFilename, extent, scaleFactor, fillValue, roiShape=None):
    # extent is of the form [minX, maxY, maxX, minY] in projected values
    # open image and read metadata
    img = gdal.Open(inFilename, gdal.GA_ReadOnly)
    bandNum = img.RasterCount
    rasterGeoTrans = img.GetGeoTransform()
    outData = np.zeros((img.RasterCount))

    # For each band calculate the mean of valid pixels in the extent.
    # If ROI shapefile is given then ignore the extent and clip the image with
    # the ROI instead
    if roiShape:
        clippedImg = io_utils.clipRasterWithShape(img, roiShape)
        for band in range(bandNum):
            subsetData = clippedImg.GetRasterBand(band+1).ReadAsArray()
            outData[band] = np.nanmean(subsetData[subsetData != fillValue]*scaleFactor)
        clippedImg = None
    else:
        # convert extent from geographic to pixel values
        [minX, maxY, maxX, minY] = extent
        pixExtent = (
                io_utils.world2Pixel(rasterGeoTrans, minX, maxY) +
                io_utils.world2Pixel(rasterGeoTrans, maxX, minY))
        for band in range(bandNum):
            inData = img.GetRasterBand(band+1).ReadAsArray()
            subsetData = inData[pixExtent[1]:pixExtent[3]+1, pixExtent[0]:pixExtent[2]+1]
            outData[band] = np.nanmean(subsetData[subsetData != fillValue]*scaleFactor)

    img = None
    return outData

def percentileValueOfImage(inFilename, scaleFactor, fillValue, percentile = 90):
    # open image and read metadata
    img = gdal.Open(inFilename, gdal.GA_ReadOnly)
    bandNum = img.RasterCount

    # for each band calculate the max of valid pixels in the image
    outData = np.zeros((img.RasterCount))
    for band in range(bandNum):
        inData = img.GetRasterBand(band+1).ReadAsArray()
        outData[band] = np.percentile(inData[inData!=fillValue]*scaleFactor, percentile)

    img = None
    return outData

# Find a MODIS file in a list of files with an overpass closest to the given
# time
def findClosestOverpass(filesMOD, time):
    difference = 10000
    for fileMOD in filesMOD if not isinstance(filesMOD, basestring) else [filesMOD]:
        match = re.search("A\d{7}\.(\d{2})(\d{2})\.\d{3}\..*\.hdf", fileMOD)
        overpassTime = float(match.group(1)) + float(match.group(2))/60.0
        if abs(time-overpassTime) < difference:
            difference = abs(time-overpassTime)
            closestFile = fileMOD

    return closestFile

# Sort the MODIS file list by how close their overpass is to the given time
def sortByClosestOverpass(filesMOD, time):
    unsortedDict = {}
    for fileMOD in filesMOD if not isinstance(filesMOD, basestring) else [filesMOD]:
        match = re.search("A\d{7}\.(\d{2})(\d{2})\.\d{3}\..*\.hdf", fileMOD)
        overpassTime = float(match.group(1)) + float(match.group(2))/60.0
        overpassTimeDifference = abs(time-overpassTime)
        unsortedDict[overpassTimeDifference] = fileMOD
        sortedKeys = sorted(unsortedDict.keys())
    return [unsortedDict[key] for key in sortedKeys]


def estimateAtmParametersMODIS(fileImg,  modisAtmDir, extent = None,  yearDoy = "", time = -1, roiShape = None):
    # Find the MODIS files in MODIS_ATM directory
    filesMOD05 = []
    filesMOD04 = []
    filesMOD07 = []
    for root, _, files in os.walk(modisAtmDir):
        for name in files:
            match = re.match("^M[OY]D05_L2\.A"+yearDoy, name)
            if match:
                filesMOD05.append(os.path.join(root, name))
            match = re.match("^M[OY]D04_3K\.A"+yearDoy, name)
            if match:
                filesMOD04.append(os.path.join(root, name))
            match = re.match("^M[OY]D07_L2\.A"+yearDoy, name)
            if match:
                filesMOD07.append(os.path.join(root, name))

    if not (len(filesMOD05)>0 and len(filesMOD04)>0 and len(filesMOD07)>0):
        return -1, -1 ,-1

    # if time is given then sort the the files by how close the overpass time
    # is to the given time
    if time > 0:
        filesMOD05 = sortByClosestOverpass(fileMOD05, time)
        filesMOD04 = sortByClosestOverpass(fileMOD04, time)
        filesMOD07 = sortByClosestOverpass(fileMOD07, time)

    fileMOD05 = filesMOD05[0]
    fileMOD04 = filesMOD04[0]
    fileMOD07 = filesMOD07[0]

    fieldMOD05 = 'Water_Vapor_Near_Infrared'
    scaleFactorMOD05 = 0.001
    fillValueMOD05 = -9999

    fieldMOD04 = 'Optical_Depth_Land_And_Ocean'
    scaleFactorMOD04 = 0.001
    fillValueMOD04 =  -9999

    fieldMOD07 = 'Total_Ozone'
    scaleFactorMOD07 = 0.1 * 0.001 # convert to Dobson and then to cm-atm
    fillValueMOD07 = -9999

    # Get the projection and extent (if needed) of the input image
    img = gdal.Open(fileImg, gdal.GA_ReadOnly)
    proj = img.GetProjection()
    # If neither extent or roiShape are given the use the extent of the
    # whole input image
    if extent is None and roiShape is None:
        gt=img.GetGeoTransform()
        cols = img.RasterXSize
        rows = img.RasterYSize
        ext = io_utils.getExtent(gt,cols,rows)
        # Extent is projected coordinates of UL and BR pixels
        extent = [ext[0][0], ext[0][1], ext[2][0], ext[2][1]]
    img = None

    # get AOT
    fileStr = 'HDF4_EOS:EOS_SWATH:"'+fileMOD04+'":mod04:'+fieldMOD04
    outFilename = os.path.join(os.path.dirname(fileMOD04), fieldMOD04+'.tif')
    reprojectModisSwath(fileStr, outFilename, proj)
    aot = meanValueOfExtent(outFilename, extent, scaleFactorMOD04, fillValueMOD04, roiShape)
    # If can't read the AOT of the extent (most probably due ot cloud) use the 50th percentile AOT of the image
    if math.isnan(aot[0]):
        print("Getting backup AOT!!")
        aot = percentileValueOfImage(outFilename, scaleFactorMOD04, fillValueMOD04, 50)

    # get water vapour
    fileStr = 'HDF4_EOS:EOS_SWATH:"'+fileMOD05+'":mod05:'+fieldMOD05
    outFilename = os.path.join(os.path.dirname(fileMOD05), fieldMOD05+'.tif')
    reprojectModisSwath(fileStr, outFilename, proj)
    wv = meanValueOfExtent(outFilename, extent, scaleFactorMOD05, fillValueMOD05, roiShape)

    # get ozone
    fileStr = 'HDF4_EOS:EOS_SWATH:"'+fileMOD07+'":mod07:'+fieldMOD07
    outFilename = os.path.join(os.path.dirname(fileMOD07), fieldMOD07+'.tif')
    reprojectModisSwath(fileStr, outFilename, proj)
    ozone = meanValueOfExtent(outFilename, extent, scaleFactorMOD07, fillValueMOD07, roiShape)

    return aot, wv, ozone

def downloadAtmParametersMODIS(imagePath, metadataPath, sensor):
    # Get overpass time from metadata

    #######################################################
    # Get ROI as the image extent in geographic coordinates

    # First get extent in projected coordinates
    img = gdal.Open(imagePath, gdal.GA_ReadOnly)
    gt = img.GetGeoTransform()
    cols = img.RasterXSize
    rows = img.RasterYSize
    ext = io_utils.getExtent(gt,cols,rows)

    # Then reproject to geographic
    src_srs = osr.SpatialReference()
    src_srs.ImportFromWkt(img.GetProjection())
    tgt_srs = src_srs.CloneGeogCS()
    geo_ext = io_utils.reprojectCoords(ext,src_srs,tgt_srs)
    # get LL and UR pixels
    extent = [geo_ext[1], geo_ext[3]]

    #########################################################
    # Call daac2disk to donwload the data
    version = str(6)
    downloadDir = os.path.join(os.path.dirname(imagePath), "temp", "MODIS_ATM")
    workingDir = os.path.join(os.path.dirname(imagePath), "temp")
    if not os.path.exists(downloadDir):
        os.makedirs(downloadDir)
    for shortname in ["MOD05_L2", "MOD04_3K", "MOD07_L2"]:
        print "Downloading "+shortname
        cmd = prepareDaac2DiskCommand(shortname, version, extent, date, date, downloadDir)
        print cmd
        proc = subprocess.Popen(cmd, shell=True, cwd=workingDir, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.communicate(input="y")

    return downloadDir
