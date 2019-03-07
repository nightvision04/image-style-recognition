import model_creator as mc
import cv2
import numpy as np



class Model:

    def __init__(self,file):
        self.quality_model = mc.load_model('../models/bgr_quality.pickle')
        print('Quality model loaded')

class ImageParser:

    def __init__(self):
        pass

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
        self.w_loops = self.width // 10
        self.h_loops = self.height // 10

        self.h_ranges=[]
        # Create convolution squares from center mass
        for j in range(0,(self.h_loops*10),10):
            self.h_ranges.append(j)


        self.w_ranges=[]
        for i in range(0,(self.w_loops*10),10):
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

        probability_series = []

        for i in range(len(self.x)):
            result = model.quality_model.predict(x[i])
            probability_series.append(result)
            bin_count=i

        probability_series = np.array(probability_series)
        result = (np.sum(probability_series) / bin_count)
        print("Predicted {0} across {1} scans".format(result,bin_count))
        return result

# Load model on startup
model = Model()
