#confusion_matrix script
#Author: Martin Rapilly
#Calculates values for the confusion matrix and saves it to a .txt file (True Positive, True Negative, False Positive, False Negative, Overall accuracy, Omission error, Comission error)
#Also creates an image with location of True Positive, True Negative, False Positive and False Negative
#This script works with Python 3

#imports libraries
import os, sys, math, time, datetime
from numpy import *
import numpy as np
from osgeo import gdal
from osgeo import gdal_array
from osgeo import osr

#creates a counter
cntr=1
    
#time variable for processing time measurement
time1 = time.clock()

#defines output path
pathFinal="F:/.../results_script_confusion_matrix"

#defines path for tiffs containing output from index and ratio processing to identify burned areas for Valle Nuevo protected area(VN)
path= "F:/.../VN_resampled"

#defines path for reference image obtained by photointerpretation on LANDSAT-8 images
imgRef="F:/.../VN_reference_tiff.tif"

#allows to see full array in log
np.set_printoptions(threshold=sys.maxsize)
log = open(pathFinal+"\\myprog.log", "a")
sys.stdout = log

#gets full name and create a list of all files in the directory 
ListImages=[]
for file in os.listdir(path):
    if file.endswith(".tif"):
        ListImages.append(os.path.join(path, file))
#sorts the list aphabetically
ListImages.sort()
print ("image list: ", ListImages)

#opens reference image with GDAL to read it as an array
imgRefGDAL=gdal.Open(imgRef)
band0imgRefGDAL = imgRefGDAL.GetRasterBand(1)
arrayBand0imgRefGDAL = band0imgRefGDAL.ReadAsArray()

#initiates a loop to calculate confusion matrix on each output result from indexes and ratio processing to identify burned areas
for imgTest in ListImages:
    
    #creates an empty numpy array with same size as the GDAL array created previously from the reference image
    emptyArray=np.full_like(arrayBand0imgRefGDAL, np.nan, dtype=np.double)
    
    #gets number of columns and rows
    num_rows,num_cols = emptyArray.shape
    print ("X size (col): ", num_cols)
    print ("Y size (row): ", num_rows)

    #opens one image to test with GDAL to read it as an array   
    imgTestGDAL=gdal.Open(imgTest)
    band0imgTestGDAL = imgTestGDAL.GetRasterBand(1)
    arrayBand0imgTestGDAL = band0imgTestGDAL.ReadAsArray()
    
    #sets counter to 0 for True Positive (VP), False Positive (FP), False Negative (FN) and True Negative (VN)
    VP=0
    FP=0
    FN=0
    VN=0

    #initiates loop to check pixel values, pixel by pixel
    for row in range(num_rows):
        for col in range(num_cols):
            #if NaN value in reference image, checks another pixel
            if math.isnan(arrayBand0imgRefGDAL[row][col])or arrayBand0imgRefGDAL[row][col]==-32768 or arrayBand0imgRefGDAL[row][col]==0:
                print ("pixel NaN in reference image")
                
            #else, if pixel value in reference image exists, compares reference value and test value
            else:
                #if imgRef value is 1 (unburned) and imgTest value is NaN (unburned), then save value 4 in empty array (True Negative) and increment True Negative counter
                if arrayBand0imgRefGDAL[row][col]==1 and (math.isnan(arrayBand0imgTestGDAL[row][col])or arrayBand0imgTestGDAL[row][col]==-32768):
                    #counts one more pixel as a True Negative
                    VN=VN+1
                    #saves the True Negative value (4) in emptyArray
                    emptyArray[row][col]=4
                    
                #if imgRef value is 1 (unburned) and imgTest value is superior to 0(burned), then save value 2 in empty array (False Positive) and increment False Positive counter
                elif arrayBand0imgRefGDAL[row][col]==1 and arrayBand0imgTestGDAL[row][col]>0:
                    #counts one more pixel as a False Positive
                    FP=FP+1
                    #saves the False Positive value (2) in emptyArray
                    emptyArray[row][col]=2
                    
                #if imgRef value is 2 (burned) and imgTest value is NaN(unburned), then save value 3 in empty array (False Negative) and increment False Negative counter  
                elif arrayBand0imgRefGDAL[row][col]==2 and (math.isnan(arrayBand0imgTestGDAL[row][col])or arrayBand0imgTestGDAL[row][col]==-32768):
                    #counts one more pixel as a False Negative
                    FN=FN+1
                    #saves the False Negative value (3) in emptyArray
                    emptyArray[row][col]=3
                    
                #if imgRef value is 2 (burned) and imgTest value is superior to 0(burned),then save value 1 in empty array (True Positive) and increment True Positive counter
                elif arrayBand0imgRefGDAL[row][col]==2 and arrayBand0imgTestGDAL[row][col]>0:
                    #counts one more pixel as a True Positive
                    VP=VP+1
                    #saves the True Positive value (1) in emptyArray
                    emptyArray[row][col]=1    
                
    #calculates TP, FN, FP, TN values for one image tested
    print ("VP count is: ", str(VP))
    print ("FP count is: ", str(FP))
    print ("FN count is: ", str(FN))
    print ("VN count is: ", str(VN))
    
    #calculates the Overall Accuracy
    if VP+VN+FP+FN>0:
        OA=(VP+VN)/(VP+VN+FP+FN)
    else:
        OA=-9999

    #calculates the Omission Error
    if FN+VP>0:
        OE=FN/(FN+VP)
    else:
        OE=-9999
    #calculates the Comission Error
    if FP+VP>0:
        CE=FP/(FP+VP)
    else:
        CE=-9999
    print ("Overall Accuracy: ", str(OA))

    #saves the outputs to a text file; the name of the file presents the Overall Accuracy, Omission Error and Comission Error
    f=open(pathFinal+"/"+str(round(OA,5))+"_"+str(round(OE,5))+"_"+str(round(CE,5))+"_"+str(cntr)+"_"+imgTest[-32:-4]+".txt", "w")
    f.write("VP, FP, FN, VN: "+ str(VP)+ " / "+ str(FP)+" / "+ str(FN)+" / "+str(VN)+"\n"+"OA, OE, CE: "+str(OA)+ " / "+str(OE)+ " / "+str(CE))
    f.close()
    
    #saves the outputs to a numpy array 
    np.save(pathFinal+"/"+"ConfusionMatrix_"+str(round(OA,5))+"_"+str(round(OE,5))+"_"+str(round(CE,5))+"_"+str(cntr)+"_"+imgTest[-32:-4]+".csv", emptyArray)

    #increments counter for next image checked
    cntr=cntr+1
                    
time2 = time.clock()
print ("Process done in "+ str((time2-time1)/3600) + " hours")
