import model_creator as mc
import cv2
import numpy as np
import time
import connections as con



class ImageParser:

    def __init__(self):
        from sklearn.externals import joblib

        self.lookslikefilm_model = joblib.load('../models/lookslikefilm_convolution.pickle')
        self.unsplash_model = joblib.load('../models/unsplash_model.pickle')
        print('Unsplash model loaded')

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



    def convolution_strips(self,operation_dict):
        '''
        Split each section into the image into a 1d array and insert as training data

        operation options = {
                            'operation':['insert_table','classify_image']
                            'img':None
                            'table':[None,'imgur_convolution','unsplash_convolution']
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
        self.shrink()



        # Redefine size after shrinking image
        self.width = len(self.img[0])
        self.height = len(self.img)
        self.w_loops = self.width // 25
        self.h_loops = self.height // 25

        self.h_ranges=[]
        # Create convolution squares from center mass
        for j in range(0,(self.h_loops*25),25):
            self.h_ranges.append(j)


        self.w_ranges=[]
        for i in range(0,(self.w_loops*25),25):
            self.w_ranges.append(i)

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

        img = cv2.imread(filepath)
        self.convolution_strips({
                            'operation':'classify_image',
                            'img':img,
                            'table':None,
                            })
        print('Loaded {}'.format(filepath))


        thumbpath = 'static/images/downloads/thumbs/' + filepath.split('static/images/downloads/')[1]
        cv2.imwrite(thumbpath,self.img)

        probability_series = []

        t1=time.time()
        for i in range(len(self.x)):



            llf_result = self.lookslikefilm_model.predict([self.x[i]])
            us_result = self.unsplash_model.predict([self.x[i]])
            probability_series.append(llf_result)
            probability_series.append(us_result)
            bin_count=i
        t2=time.time()
        print ("{} seconds".format(t2-t1))
        probability_series = np.array(probability_series)
        result = (np.sum(probability_series) / bin_count)
        print("Predicted {0} across {1} scans".format(result,bin_count))
        return result
