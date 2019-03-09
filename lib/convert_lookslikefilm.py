
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

    def shrink(self):
        '''
        Divide current size by 100 to find reduce-factor
        '''

        if self.orientation == 'landscape':
            factor = 100 / self.height
        if self.orientation == 'portrait':
            factor = 100 / self.width
        if self.orientation == 'square':
            factor = 100 / self.width # Can be height or width

        self.img = cv2.resize(self.img,None,fx=factor, fy=factor, interpolation = cv2.INTER_CUBIC)

        return self



i=0
for filename in os.listdir('../lookslikefilm/images'):

    i+=1
    if i> 1900:
        break
    filepath = "../lookslikefilm/images/"+filename
    print(filepath)

    img = cv2.imread(filepath)
    try:
        imagedata = ImageData(img)
    except AttributeError:
        continue
    imagedata.get_metadata(filename.split('.')[0])
    imagedata.convolution_strips({
                        'operation':'insert_table',
                        'img':None,
                        'table':'lookslikefilm_convolution',
                        })
