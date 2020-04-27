import sys
import argparse
import os


import pyexiv2
import pandas as pd
import datetime as dt

# Get argment
parser = argparse.ArgumentParser()
parser.add_argument("--csv", help="CSV file", type=str)

#
# Get csv file name.
#
def getCsvFileName():
    return parser.parse_args().csv

#
# Read data from a csv file which is the list for conversion.
#
def readCsvData():
    fileName = getCsvFileName()

    if os.path.isfile(fileName) == True:
        # Read csv file.
        data = pd.read_csv(fileName)
    else :
        # Error : file does not exist.
        print("file does not exist :", fileName)
        exit()

    # Return a csv data.
    return data

#
# open Exif file.
#
def openImgData( filename ):
    if os.path.isfile( filename ) == True:
        return pyexiv2.Image( filename )
    else :
        print("file does not exist :", filename )
        exit()


def convDeg2Dms( deg ):
    d = int(deg)
    tmp_m = (deg - d) * 60
    m = int(tmp_m)
    s = round((tmp_m - m) * 60, 2)
    return d, m, s

def getDmsString( degree, minutes, seconds ):
    return (str(degree) + "/1 " + str(minutes) +"/1 "+ str(int(seconds * 100)) +"/100")

# main
if __name__ == '__main__':
    # read meta data
    csvData = readCsvData()

    # counter
    num =  0

    while num < len(csvData):
        img = openImgData( csvData.loc[num, "filename"] )
        metadata = img.read_exif()

        # delete unnecessary tags.
        if 'Exif.Image.Make' in metadata:
            del metadata['Exif.Image.Make']

        if 'Exif.Image.Model' in metadata:
            del metadata['Exif.Image.Model']

        if 'Exif.Image.Software' in metadata:
            del metadata['Exif.Image.Software']

        # update shooting date.
        dt = dt.datetime(csvData.loc[num, "year"], csvData.loc[num, "month"], csvData.loc[num, "day"], csvData.loc[num, "hour"], csvData.loc[num, "min"], 0)
        metadata['Exif.Image.DateTime'] = dt.strftime("%Y:%m:%d %H:%M:%S")
        metadata['Exif.Image.DateTimeOriginal'] = dt.strftime("%Y:%m:%d %H:%M:%S")
        metadata['Exif.Photo.DateTimeOriginal'] = dt.strftime("%Y:%m:%d %H:%M:%S")
        metadata['Exif.Photo.DateTimeDigitized'] = dt.strftime("%Y:%m:%d %H:%M:%S")

        # create geotag (latitude and longitude as GPS information).
        metadata['Exif.GPSInfo.GPSVersionID'] = '2 2 0 0'

        if csvData.loc[num, "latitude"] > 0:
            metadata['Exif.GPSInfo.GPSLatitudeRef'] = "N"
        else:
            metadata['Exif.GPSInfo.GPSLatitudeRef'] = "S"
        
        d, m, s = convDeg2Dms( csvData.loc[num, "latitude"] )
        metadata['Exif.GPSInfo.GPSLatitude'] = getDmsString( d, m, s )

        if csvData.loc[num, "longitude"] > 0:
            metadata['Exif.GPSInfo.GPSLongitudeRef'] = "E"
        else:
            metadata['Exif.GPSInfo.GPSLongitudeRef'] = "W"

        d, m, s = convDeg2Dms( csvData.loc[num, "longitude"] )
        metadata['Exif.GPSInfo.GPSLongitude'] = getDmsString( d, m, s )

        #print(metadata)

        # once delete old (original) metadata before modification.
        img.clear_exif()
        img.modify_exif( metadata )

        # close image file.
        img.close()

        # update counter.
        num += 1 
