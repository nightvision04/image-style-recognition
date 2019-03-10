
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
    i+=1
    if i> 1900:
        break
    filepath = "../imgur/images/"+filename
    print(filepath)

    img = cv2.imread(filepath)
    imagedata = ImageData(img)
    imagedata.get_metadata(filename.split('.')[0])
    imagedata.convolution_strips({
                        'operation':'insert_table',
                        'img':None,
                        'table':'imgur_convolution',
                        'filters':[''],
                        'size':25
                        })

    img = cv2.imread(filepath)
    imagedata = ImageData(img)
    imagedata.get_metadata(filename.split('.')[0])
    imagedata.convolution_strips({
                        'operation':'insert_table',
                        'img':None,
                        'table':'imgur_grayscale',
                        'filters':['grayscale_high_contrast'],
                        'size':50
                        })
