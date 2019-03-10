
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

    i+=1
    if i> 1900:
        break
    filepath = "../flickr/images/"+filename
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
                        'table':'flickr_convolution',
                        'filters':[''],
                        'size':25
                        })

    img = cv2.imread(filepath)
    imagedata = ImageData(img)
    imagedata.get_metadata(filename.split('.')[0])
    imagedata.convolution_strips({
                        'operation':'insert_table',
                        'img':None,
                        'table':'flickr_grayscale',
                        'filters':['grayscale_high_contrast'],
                        'size':50
                        })
