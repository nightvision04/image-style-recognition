
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


        filepath = '../imgur/metadata/' + filename + "_full.txt"
        filestring = ""
        with open(filepath,'r') as f:
            for line in f:
                filestring += line
        self.meta = json.loads(filestring)

        tags_array = []
        self.metadata = {
                    'id':self.meta['images'][0]['id'],
                    'tags':tags_array,
                    'label':'imgur'
        }

        return self



con.clear_table('imgur_convolution')
con.clear_table('imgur_grayscale')

i=0
for filename in os.listdir('../imgur/images'):

    # No support for gifs yet
    if '.jpg' or '.png' or '.tiff' or '.bmp' in filename:
        filepath = "../imgur/images/"+filename
        print(filepath)
        img = cv2.imread(filepath)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        if i==0:
            # Load once, then update
            imagedata = ImageData(img)

        i+=1
        if i> 1900:
            break

        imagedata.import_training_data('imgur',filename,img)
