
# coding: utf-8

# In[32]:


import connections as con
import json
import cv2
import os
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
def json_loads(a):
    return np.array(json.loads(a))

class X_data:
    ''' This object will contain the models active from the database
        active_dfs = Active_dfs()
        # Creates: Active_dfs().df_dict[pair] for each active pair
    '''
    def __init__(self,connection,table):
        ''' This is run whenever the object is first created
        '''

        self.df =  con.get_id_strips(connection,table)
        self.df['x'] = self.df.apply(lambda row: json_loads(row['x']), axis=1)
        self.df['tags'] = self.df.apply(lambda row: json_loads(row['tags']), axis=1)
        print('Loaded json models')


def load_data(target_name,target_type):
    connection = con.get_connection('image_profile')
    control_table = 'flickr_' + target_type
    control = X_data(connection,control_table)


    control_x, X_test, control_y, y_test = train_test_split(
        control.df.x.values, np.zeros(len(control.df.x.values)), test_size=0.05, random_state=42,shuffle=True)
    connection.close()



    table_name = target_name + '_' + target_type

    connection = con.get_connection('image_profile')
    target = X_data(connection,table_name)
    connection.close()
    target.df.loc[target.df['label']==target_name ,'y'] = 1

    # Remove sample bias
    target_len = len(target.df.x.values)
    control_len = len(control.df.x.values)
    print('target length',target_len)
    print('control length',control_len)

    if target_len > control_len:
        max_len = control_len -1
    else:
        max_len = target_len -1
    print('max length',max_len)
    X = np.concatenate((control_x[0:max_len], target.df.x.values[0:max_len]), axis=0)
    y = np.concatenate((control_y[0:max_len], target.df.y.values[0:max_len]), axis=0)



    return X,y

def test_split(X,y):
    # This fixes the 'setting an array index with a sequence' ValueError

    arr = np.zeros(len(X),dtype=object)
    for i in range(len(X)):
        arr[i]=X[i]

    arr = np.array(arr.tolist())
    X = arr.reshape(len(X),len(X[0]))

    arr = np.zeros(len(y),dtype=object)
    for i in range(len(y)):
        arr[i]=y[i]

    arr = np.array(arr.tolist())
    y = arr.reshape(len(y),1)



    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=42,shuffle=True)

    return X_train, X_test, y_train, y_test

def generate_model(X_train, X_test, y_train, y_test,target_name,target_type):

    print('Training size:',len(X_train))
    print('Testing size:',len(X_test))

    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler()

    from sklearn.decomposition import PCA
    pca = PCA(0.98)

    from sklearn.ensemble import RandomForestClassifier
    rf = RandomForestClassifier()

    from sklearn.pipeline import Pipeline
    pipeline = Pipeline([('scaler', sc), ('pca', pca),('rforest',rf)])

    # Instantiate the grid search model
    from sklearn.model_selection import RandomizedSearchCV
    from sklearn.model_selection import GridSearchCV



    # Create the parameter grid based on the results of random search
    param_grid = {
        'pca__n_components': [0.87,0.89,0.91,0.93,0.95],
        'rforest__bootstrap': [True],
        'rforest__max_depth': [100,110],
        'rforest__max_features': [0.3],
        'rforest__min_samples_leaf': [3],
        'rforest__min_samples_split': [8],
        'rforest__n_estimators': [1200,1400]
    }


    grid_search = GridSearchCV(pipeline, param_grid = param_grid,cv = 2, n_jobs = 6, verbose = 2)

    # Fit the grid search to the data
    grid_search.fit(X_train, y_train)



    # best_params__ = {'bootstrap': True,
    #                  'max_depth': 90,
    #                  'max_features': 2,
    #                  'min_samples_leaf': 3,
    #                  'min_samples_split': 8,
    #                  'n_estimators': 300}

    model = grid_search.best_estimator_
    print('best params:',grid_search.best_params_)
    y_pred = model.predict(X_test)
    from sklearn.metrics import classification_report
    print(classification_report(y_test, y_pred))

    model_name = '../models/' +target_name + '_' + target_type + '.pickle'

    from sklearn.externals import joblib
    joblib.dump(model, model_name)

    return True

# def store_model(dict_,filename):
#     with open(filename, 'wb') as handle:
#         pickle.dump(dict_, handle, protocol=pickle.HIGHEST_PROTOCOL)
#     return True

def load_model(file):
    # Load data (deserialize)
    with open(file, 'rb') as handle:
        unserialized_data = pickle.load(handle)
    return unserialized_data

def start_model(target_name,target_type):
    X,y = load_data(target_name,target_type)
    X_train, X_test, y_train, y_test = test_split(X,y)
    generate_model(X_train, X_test, y_train, y_test,target_name,target_type)


# In[33]:


#X,y = load_data()


# In[34]:


#X_train, X_test, y_train, y_test = test_split(X,y)


# In[35]:


#generate_model(X_train, X_test, y_train, y_test)


# In[ ]:


'''
10x10
best params: {
'rforest__bootstrap': True,
'rforest__max_depth': 110,
'rforest__max_features': 2,
'rforest__min_samples_leaf': 3,
'rforest__min_samples_split': 8,
'rforest__n_estimators': 300}

'''


# In[ ]:


'''
25x25
best params: {'pca__n_components': 0.89,
              'rforest__bootstrap': True,
              'rforest__max_depth': 110,
              'rforest__max_features': 0.3,
              'rforest__min_samples_leaf': 3,
              'rforest__min_samples_split': 8,
              'rforest__n_estimators': 1500}


'''
