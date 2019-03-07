
# coding: utf-8


import connections as con
import json
import cv2
import os
import pandas as pd

# Open files

i=0
for filename in os.listdir('imgur/images/'):
    i+=1

    if i> 1:
        break

    filepath = 'imgur/metadata/' + filename.split('.')[0]+"_full.txt"


def json_loads(a):
    return json.loads(a)

class X_data:
    ''' This object will contain the models active from the database
        active_dfs = Active_dfs()
        # Creates: Active_dfs().df_dict[pair] for each active pair
    '''
    def __init__(self,id,connection,table):
        ''' This is run whenever the object is first created
        '''

        self.df =  con.get_id_strips(id,connection,table)
        self.df['x'] = self.all_models.df(lambda row: json_loads(row['x']), axis=1)
        self.df['tags'] = self.df.apply(lambda row: json_loads(row['tags']), axis=1)
        print('Loaded json models')


id = filename.split('.')[0]
connection = con.get_connection('image_profile')
X = X_data(id,connection,'imgur_convolution')
connection.close()


# In[42]:



X.df
