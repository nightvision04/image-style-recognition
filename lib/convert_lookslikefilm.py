
import numpy as np
import cv2
import os
import json
import connections as con
import parser__ as p



class ImageData(p.ImageParser):
    '''This will hold the main frame data in between each loop of the fill function
    '''
    def __init__(self,img):
        self.img = img.copy()
        super().__init__()

    def get_metadata(self,filename):


        filepath = '../lookslikefilm/images/' + filename + "_full.txt"
        filestring = ""
        id = filename.split('.')[0]

        tags_array = []
        self.metadata = {
                    'id':id,
                    'tags':tags_array,
                    'label':'lookslikefilm'
        }

        return self


con.clear_table('lookslikefilm_convolution')
con.clear_table('lookslikefilm_grayscale')

i=0
for filename in os.listdir('../lookslikefilm/images'):

    # No support for gifs yet
    if '.jpg' or '.png' or '.tiff' or '.bmp' in filename:
        filepath = "../lookslikefilm/images/"+filename
        print(filepath)
        img = cv2.imread(filepath)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        if i==0:
            # Load once, then update
            imagedata = ImageData(img)

        i+=1
        if i> 1900:
            break

        imagedata.import_training_data('lookslikefilm',filename,img)
