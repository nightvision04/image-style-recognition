
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

        id = filename.split('.')[0]

        tags_array = []
        self.metadata = {
                    'id':id,
                    'tags':tags_array,
                    'label':'flickr'
        }

        return self



con.clear_table('flickr_convolution')
con.clear_table('flickr_grayscale')

i=0
for filename in os.listdir('../flickr/images'):
    filepath = "../flickr/images/"+filename
    print(filepath)
    img = cv2.imread(filepath)
    if i==0:
        # Load once, then update
        imagedata = ImageData(img)

    i+=1
    if i> 1900:
        break
    imagedata.import_training_data('flickr',filename,img)
