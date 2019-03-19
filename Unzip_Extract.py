import pydicom
import matplotlib.pyplot as plt
import glob
import os
import json
import zipfile
import shutil


inputDir = "D:\\OPTIMAM"
outputDir = "D:\\Images"

for fileName in os.listdir(inputDir):
    print("Current file:", fileName)#folder name = Patient code for images and metadata as well

    #Uncompressing zipped files that contain DICOM images
    zip_ref = zipfile.ZipFile(inputDir +'\\' + fileName, 'r')
    zip_ref.extractall(inputDir)
    zip_ref.close()

    clientID = str(fileName).replace('.zip', '')
    metadataFile = "D:\\OPTIMAM" + "\\data\\" + clientID + '\\nbss_' + clientID + '.json'

    print("MetaData File:", metadataFile)
    # Image counts
    imgSavedCount = 0
    imgSkippedCount = 0  # The count of images marked as 'For Processing', those images don't seem suitable for ML

    statsFile = open("stats.txt", "a")  # This file records statsitics on the images processed
    logFile = open("log.txt", "a")  # This file records exceptions (e.g. unexpected label, or missing DICOM tag)
    for file in glob.iglob(inputDir +"\\"+ clientID + '\\**\\*.dcm', recursive=True):
        #print(imgID)
        imgID = os.path.basename(file).split(".dcm")[0]
        dataset = pydicom.dcmread(file) #Reading the DICOM file

        try:
            if dataset.PresentationIntentType == "FOR PRESENTATION":#We only looking for unprocessed images
                #patientAge = dataset.PatientAge
                imgLaterality = dataset.ImageLaterality

                #Get the image label from json file
                #For example, the json file of optm1 should be found in: OPTIMAM\data\optm1\nbss_optm1.json
                with open(metadataFile) as f:
                    metadata = json.load(f)
                imgLabel = metadata['Classification']
                print("Label:", imgLabel)

                if imgLabel == "M":
                    plt.imsave(arr=dataset.pixel_array, fname=outputDir+"\\Malignant\\" + str(imgID)+"_"+str(imgLaterality)+".jpg", cmap=plt.cm.gray)
                    imgSavedCount = imgSavedCount + 1
                elif imgLabel == "B":
                    plt.imsave(arr=dataset.pixel_array, fname=outputDir+"\\Benign\\" + str(imgID)+"_"+str(imgLaterality)+".jpg", cmap=plt.cm.gray)
                    imgSavedCount = imgSavedCount + 1
                elif imgLabel == "CI":
                    plt.imsave(arr=dataset.pixel_array, fname=outputDir+"\\CI\\" + str(imgID)+"_"+str(imgLaterality)+".jpg", cmap=plt.cm.gray)
                    imgSavedCount = imgSavedCount + 1
                elif imgLabel == "N":
                    plt.imsave(arr=dataset.pixel_array, fname=outputDir+"\\Negative\\" + str(imgID)+"_"+str(imgLaterality)+".jpg", cmap=plt.cm.gray)
                    imgSavedCount = imgSavedCount + 1
                else:
                    print("Unexpected Label!")
                    logFile.write(clientID + ":Label=" + str(imgLabel) + "\n")
            else:
                imgSkippedCount = imgSkippedCount + 1
        except:
            print("Exception: Missing DICOM Tag in ",imgID)
            logFile.write(clientID + ":" + str(imgID) + "\n")

    print(imgSavedCount, " images saved.")
    print(imgSkippedCount, " images skipped.")
    os.remove(inputDir + '\\' + fileName)
    shutil.rmtree(inputDir + '\\' + clientID)
    statsFile.write(clientID + "," + str(imgSavedCount) + "," + str(imgSkippedCount) + "\n")
    statsFile.close()
    logFile.close()
