
# coding: utf-8

# In[1]:


import connections as con
import json
import cv2
import os
import pandas as pd
import numpy as np
import pickle

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
    
    
def load_data():
    connection = con.get_connection('image_profile')
    imgur = X_data(connection,'imgur_convolution')    
    connection.close()
    imgur.df.loc[imgur.df['label']=='imgur' ,'y'] = 0


    connection = con.get_connection('image_profile')
    unsplash = X_data(connection,'unsplash_convolution')    
    connection.close()
    unsplash.df.loc[unsplash.df['label']=='unsplash' ,'y'] = 1

    X = np.concatenate((imgur.df.x.values, unsplash.df.x.values), axis=0)
    y = np.concatenate((imgur.df.y.values, unsplash.df.y.values), axis=0)
    
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

    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=42,shuffle=True)
    
    return X_train, X_test, y_train, y_test

def generate_model(X_train, X_test, y_train, y_test):

    print('Training size:',len(X_train))
    print('Testing size:',len(X_test))

    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler()  

    from sklearn.decomposition import PCA
    pca = PCA(0.95)  

    from sklearn.ensemble import RandomForestClassifier
    rf = RandomForestClassifier()

    from sklearn.pipeline import Pipeline
    pipeline = Pipeline([('scaler', sc), ('pca', pca),('rforest',rf)])

    # Instantiate the grid search model
    from sklearn.model_selection import RandomizedSearchCV
    from sklearn.model_selection import GridSearchCV

    # Create the parameter grid based on the results of random search 
    param_grid = {
        'rforest__bootstrap': [True],
        'rforest__max_depth': [80, 90, 100, 110],
        'rforest__max_features': [2],
        'rforest__min_samples_leaf': [3],
        'rforest__min_samples_split': [8, ],
        'rforest__n_estimators': [100, 200, 300]
    }
    grid_search = GridSearchCV(pipeline, param_grid = param_grid,cv = 2, n_jobs = 1, verbose = 2)

    # Fit the grid search to the data
    grid_search.fit(X_train, y_train)
    grid_search.best_params_

    # best_params__ = {'bootstrap': True,
    #                  'max_depth': 90,
    #                  'max_features': 2,
    #                  'min_samples_leaf': 3,
    #                  'min_samples_split': 8,
    #                  'n_estimators': 300}

    model = grid_search.best_estimator_
    y_pred = model.predict(X_test)
    from sklearn.metrics import classification_report
    print(classification_report(y_test, y_pred))

    return pipeline

def store_model(model,filename):
    with open(filename, 'wb') as handle:
        pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return True

def load_model(file):
    # Load data (deserialize)
    with open(file, 'rb') as handle:
        unserialized_data = pickle.load(handle)
    return unserialized_data

def create_quality_model():
    X,y = load_data()
    X_train, X_test, y_train, y_test = test_split(X,y)
    model = generate_model(X_train, X_test, y_train, y_test)
    store_model(model,'../models/quality_model.pickle')


# In[2]:





# In[4]:





# In[5]:




