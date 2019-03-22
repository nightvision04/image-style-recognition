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
        self.unsplash_model = joblib.load('../models/unsplash_convolution.pickle')
        self.lookslikefilm_grayscale = joblib.load('../models/lookslikefilm_grayscale.pickle')
        self.unsplash_grayscale = joblib.load('../models/unsplash_grayscale.pickle')

        self.side_min_size = 90
        self.grayscale_size = 45
        self.color_size = 30




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


    def generate_thumbnail(self,size,filepath):
        self.width = len(self.img[0])
        self.height = len(self.img)
        if (self.width / self.height) > 1:
            self.orientation = 'landscape'
        if (self.width / self.height) < 1:
            self.orientation = 'portrait'
        if (self.width / self.height) == 1:
            self.orientation = 'square'
        self.shrink(size)

        if 'instagram_accounts' in filepath:
            username = filepath.split('/')[2]
            parent = filepath.split('/')[0] + '/' + filepath.split('/')[1] + '/'
            img_path = filepath.split('/')[3]
            thumbpath = parent + username + '/thumbs/' + img_path
        else:
            thumbpath = 'static/images/downloads/thumbs/' + filepath.split('static/images/downloads/')[1]
        cv2.imwrite(thumbpath,self.img)


    def convolution_strips(self,operation_dict):
        '''
        Split each section into the image into a 1d array and insert as training data

        operation options = {
                            'operation':['insert_table','classify_image']
                            'img':None
                            'table':[None,'imgur_convolution','unsplash_convolution']
                            'filters': ['grayscale']
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
        self.shrink(self.side_min_size)


        # Redefine size after shrinking image
        self.width = len(self.img[0])
        self.height = len(self.img)
        self.w_loops = self.width // operation_dict['size']
        self.h_loops = self.height // operation_dict['size']

        self.h_ranges=[]
        # Create an array of searchable convolution squares, defined by search 'size'
        for j in range(0,((self.h_loops*operation_dict['size'])+1),operation_dict['size']):
            self.h_ranges.append(j)
        #self.h_ranges.append(self.height)

        self.w_ranges=[]
        for i in range(0,((self.w_loops*operation_dict['size'])+1),operation_dict['size']):
            self.w_ranges.append(i)
        #self.w_ranges.append(self.width)

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
            try:
                self.x = np.array(x)
                self.x = self.x.reshape(len(self.x),len(self.x[0]))

            # Recast in case of pixel errors
            except Exception as ValueError:
                arr = np.zeros(len(x),dtype=object)
                for i in range(len(x)):
                    x[i] = np.array(x[i].tolist())
                    arr[i]=x[i].astype(int)

                arr = np.array(arr)
                x = arr.reshape(len(arr),len(arr[0]))
        if operation_dict['operation']=='insert_table':
            strat_connection.close()

        return self


    def import_training_data(self,source,filename,img):

        operation = 'insert_table'
        table_color = '{}_convolution'.format(source)
        table_grayscale = '{}_grayscale'.format(source)

        self.img = img
        self.get_metadata(filename.split('.')[0])
        self.convolution_strips({
                            'operation':operation,
                            'img':None,
                            'table':table_color,
                            'filters':[''],
                            'size':self.color_size
                            })

        self.img = img
        self.get_metadata(filename.split('.')[0])
        self.convolution_strips({
                            'operation':operation,
                            'img':None,
                            'table':table_grayscale,
                            'filters':['grayscale'],
                            'size':self.grayscale_size
                            })
        return self

    def predict_quality(self,filepath):
        '''
        This function expects a local filepath to the image (in the downloads folder).
        Future: Should accept a url.
        '''

        # Color score
        self.img = cv2.imread(filepath)
        self.generate_thumbnail(125,filepath)

        #self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        self.convolution_strips({
                            'operation':'classify_image',
                            'img':self.img,
                            'table':None,
                            'filters':[''],
                            'size':self.color_size
                            })
        print('Loaded {}'.format(filepath))


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
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        self.convolution_strips({
                            'operation':'classify_image',
                            'img':img,
                            'table':None,
                            'filters':['grayscale'],
                            'size':self.grayscale_size
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
