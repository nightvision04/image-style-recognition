
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

        filepath = "../unsplash/metadata/"+filename+'_full.txt'

        filestring = ""
        with open(filepath,'r') as f:
            for line in f:
                filestring +=line

        self.meta = json.loads(filestring)
        tags_array = []
        for i in range(len(self.meta['tags'])):
            tags_array.append(self.meta['tags'][i]['title'])

        self.metadata = {
                    'id':self.meta['id'],
                    'tags':tags_array,
                    'label':'unsplash'
        }

        return self


con.clear_table('unsplash_convolution')
con.clear_table('unsplash_grayscale')

i=0
for filename in os.listdir('../unsplash/images'):
    i+=1
    if i> 1900:
        break
    filepath = "../unsplash/images/"+filename
    print(filepath)

    img = cv2.imread(filepath)
    imagedata = ImageData(img)
    imagedata.import_training_data('unsplash',filename,img)
