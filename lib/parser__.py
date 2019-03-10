import model_creator as mc
import cv2
import numpy as np
import time
import connections as con
import filters
import json



class ImageParser:

    def __init__(self):
        from sklearn.externals import joblib

        self.lookslikefilm_model = joblib.load('../models/lookslikefilm_convolution.pickle')
        self.unsplash_model = joblib.load('../models/unsplash_model.pickle')
        self.lookslikefilm_grayscale = joblib.load('../models/lookslikefilm_grayscale.pickle')
        self.unsplash_grayscale = joblib.load('../models/unsplash_grayscale.pickle')
        print('Unsplash model loaded')

    def shrink(self,output_size):
        '''
        Divide current size by 100 to find reduce-factor
        '''

        if self.orientation == 'landscape':
            factor = output_size / self.height
        if self.orientation == 'portrait':
            factor = output_size / self.width
        if self.orientation == 'square':
            factor = output_size / self.width # Can be height or width

        self.img = cv2.resize(self.img,None,fx=factor, fy=factor, interpolation = cv2.INTER_CUBIC)

        return self



    def convolution_strips(self,operation_dict):
        '''
        Split each section into the image into a 1d array and insert as training data

        operation options = {
                            'operation':['insert_table','classify_image']
                            'img':None
                            'table':[None,'imgur_convolution','unsplash_convolution']
                            'filters': ['grayscale_high_contrast']
                            'size': [any number between 2 and 253]
                            }

        '''

        if operation_dict['operation']=='classify_image':
            self.img = operation_dict['img']

        self.width = len(self.img[0])
        self.height = len(self.img)
        if (self.width / self.height) > 1:
            self.orientation = 'landscape'
        if (self.width / self.height) < 1:
            self.orientation = 'portrait'
        if (self.width / self.height) == 1:
            self.orientation = 'square'
        self.shrink(100)


        # Redefine size after shrinking image
        self.width = len(self.img[0])
        self.height = len(self.img)
        self.w_loops = self.width // operation_dict['size']
        self.h_loops = self.height // operation_dict['size']

        self.h_ranges=[]
        # Create an array of searchable convolution squares, defined by search 'size'
        for j in range(0,(self.h_loops*operation_dict['size']),operation_dict['size']):
            self.h_ranges.append(j)
        self.h_ranges.append(self.height)

        self.w_ranges=[]
        for i in range(0,(self.w_loops*operation_dict['size']),operation_dict['size']):
            self.w_ranges.append(i)
        self.w_ranges.append(self.width)

        for filter in operation_dict['filters']:
            self.img = filters.runfilter(self.img,filter)

        if operation_dict['operation']=='insert_table':
            strat_connection = con.get_connection('image_profile')
            table = operation_dict['table']

        x=[]

        for i in range(len(self.h_ranges)):
            for j in range(len(self.w_ranges)):

                # We only want to create records for standardized square shapes. Reject other shapes
                if (i < len(self.h_ranges)-1) and (j < len(self.w_ranges)-1):
                    arr1d = np.array([self.img[k][l] for l in range(self.w_ranges[j],self.w_ranges[j+1]) for k in range(self.h_ranges[i],self.h_ranges[i+1])]).ravel() # make an even



                    if operation_dict['operation']=='classify_image':
                        x.append(arr1d)

                    if operation_dict['operation']=='insert_table':
                        result = con.insert_strip(arr1d,self.metadata,self.orientation,strat_connection,table)

        if operation_dict['operation']=='classify_image':
            self.x = np.array(x).reshape(len(x),len(x[0]))

        if operation_dict['operation']=='insert_table':
            strat_connection.close()

        return self





    def predict_quality(self,filepath):
        '''
        This function expects a local filepath to the image (in the downloads folder).
        Future: Should accept a url.
        '''

        # Color score
        img = cv2.imread(filepath)
        self.convolution_strips({
                            'operation':'classify_image',
                            'img':img,
                            'table':None,
                            'filters':[''],
                            'size':25
                            })
        print('Loaded {}'.format(filepath))

        # Save the 100x100 px thumb
        thumbpath = 'static/images/downloads/thumbs/' + filepath.split('static/images/downloads/')[1]
        cv2.imwrite(thumbpath,self.img)

        t1=time.time()
        lookslikefilm_color = []
        unsplash_color = []
        t1=time.time()
        for i in range(len(self.x)):
            lookslikefilm_color.append( self.lookslikefilm_model.predict([self.x[i]]) )
            unsplash_color.append( self.unsplash_model.predict([self.x[i]]) )
        bin_count=len(self.x)
        # weight scores
        lookslikefilm_color = np.sum(np.array(lookslikefilm_color) / bin_count)
        unsplash_color = np.sum(np.array(unsplash_color) / bin_count)



        # Framing Score
        img = cv2.imread(filepath)
        self.convolution_strips({
                            'operation':'classify_image',
                            'img':img,
                            'table':None,
                            'filters':['grayscale_high_contrast'],
                            'size':50
                            })
        print('Loaded {}'.format(filepath))

        lookslikefilm_framing = []
        unsplash_framing = []

        for i in range(len(self.x)):
            lookslikefilm_framing.append( self.lookslikefilm_grayscale.predict([self.x[i]]) )
            unsplash_framing.append( self.unsplash_grayscale.predict([self.x[i]]) )
        bin_count=len(self.x)
        # weight scores
        lookslikefilm_framing = np.sum(np.array(lookslikefilm_framing) / bin_count)
        unsplash_framing = np.sum(np.array(unsplash_framing) / bin_count)


        overall_score = (lookslikefilm_color + unsplash_color + lookslikefilm_framing + unsplash_framing) / 4

        t2=time.time()
        print ("{} seconds".format(t2-t1))
        print("Predicted {0} across {1} scans".format(overall_score,bin_count))
        return json.dumps({'Overall Style':overall_score,
                'Filmic Style':lookslikefilm_color,
                'Modern Style':unsplash_color,
                'Glamour Framing':lookslikefilm_framing,
                'Modern Framing':unsplash_framing})
