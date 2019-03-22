
# coding: utf-8

# In[168]:


# coding: utf-8

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

    X_target = target.df.x.values
    y_target = target.df.y.values
    X_control = control_x
    y_control = control_y

    # Each time this function is run, the data conforms closer to the target contrast distribution, at the cost of samples.
    for i in range(2):
        X_target,y_target,X_control,y_control = fit_training_data(X_target,y_target,X_control,y_control,target_type)
        print('fit_training_data() loop {}'.format((i+1)))
        print('X_target len',len(X_target))
        print('X_control len',len(X_control))

    X = np.concatenate((X_control, X_target), axis=0)
    y = np.concatenate((y_control, y_target), axis=0)



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
    pca = PCA()

    from sklearn.ensemble import RandomForestClassifier
    rf = RandomForestClassifier()

    from sklearn.pipeline import Pipeline
    pipeline = Pipeline([('scaler', sc), ('pca', pca),('rforest',rf)])

    # Instantiate the grid search model
    from sklearn.model_selection import RandomizedSearchCV
    from sklearn.model_selection import GridSearchCV



    # Create the parameter grid based on the results of random search
    param_grid = {
        'pca__n_components': [0.87,0.89,0.91,0.93,0.95,0.97,0.99],
        'rforest__bootstrap': [True],
        'rforest__max_depth': [110],
        'rforest__max_features': [0.3],
        'rforest__min_samples_leaf': [3],
        'rforest__min_samples_split': [8],
        'rforest__n_estimators': [1200]
    }


    grid_search = GridSearchCV(pipeline, param_grid = param_grid,cv = 2, n_jobs = 4, verbose = 2)

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


# In[169]:



def generate_X_stats(X,X_control,target_type):


    print(X.shape)
    print(X_control.shape)

    if target_type== 'grayscale':
        pixel_dimensions = 1
        square_size = 45
    else:
        pixel_dimensions = 3
        square_size = 30

    from scipy import stats


    X_morph = []
    for i in range(len(X)):



        hsl_features = np.zeros([1,pixel_dimensions])
        img =  X[i].reshape(int(len(X[i]) / (square_size*pixel_dimensions)),int(len(X[i]) / (square_size*pixel_dimensions)),pixel_dimensions ).astype('uint8')

        # Get stats for contrast
        if target_type== 'grayscale':
            val_std = np.std(img, axis=0)[0] # Value std_dev
            X_morph.append(val_std)
        else:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Convert to float64 for higher precision stat descriptions
            hsv = hsv.reshape(int(len(X[i]) / pixel_dimensions),pixel_dimensions ).astype('float32')
            val_std = np.std(hsv, axis=0)[2] # Value std_dev
            X_morph.append(val_std)

    X_morph = np.array(X_morph)


    X_morph_control = []
    for i in range(len(X_control)):

        hsl_features = np.zeros([1,pixel_dimensions])
        img =  X_control[i].reshape(int(len(X_control[i]) / (square_size*pixel_dimensions)),int(len(X_control[i]) / (square_size*pixel_dimensions)),pixel_dimensions ).astype('uint8')

        # Get stats for contrast
        if target_type== 'grayscale':
            val_std = np.std(img, axis=0)[0] # Value std_dev
            X_morph_control.append(val_std)
        else:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Convert to float64 for higher precision stat descriptions
            hsv = hsv.reshape(int(len(X_control[i]) / pixel_dimensions),pixel_dimensions ).astype('float32')
            val_std = np.std(hsv, axis=0)[2] # Value std_dev
            X_morph_control.append(val_std)

    X_morph_control = np.array(X_morph_control)

    return X_morph,X_morph_control


# In[170]:


def generate_bin_sizes(sample_length):

    from scipy.stats import truncnorm
    def get_truncated_normal(mean=50, sd=20, low=0, upp=100):
        return truncnorm(
            (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

    norm_dist = get_truncated_normal(mean=50, sd=20, low=0, upp=100)
    res = 1000000
    norm_dist_shape = norm_dist.rvs(res)

    # Set bin sizes - eg (bin_sizes[0] means between 0-4, bin_sizes[5] means between 5-9, etc..)
    bin_sizes ={}
    bin_count = {}
    for i in range(0,130,5):
        bin_sizes[i] = int(len(norm_dist_shape[(norm_dist_shape >= i) & (norm_dist_shape < (i+5))]) / res * sample_length)
        bin_count[i] = 0
    return bin_sizes, bin_count


def conform_x_to_dist(X,bin_sizes,bin_count):

    X_bool = []

    for val in X:
        yep=False
        for i in range(0,130,5):
            if (val >= i) & (val < (i+5)) :
                if bin_count[i] < bin_sizes[i]:
                    yep= True
                    bin_count[i]+=1
                    X_bool.append(True)
                else:
                    yep= True
                    X_bool.append(False)
        if yep==False:
            print(val)

    return np.array(X_bool)

def fit_training_data(X,y,X_control,y_control,target_type):

    # Get hsv stats for training sets
    X_morph,X_morph_control = generate_X_stats(X,X_control,target_type)

    # Resize training sets to reflect normally distributed contrast complexity.
    X_morph_bin_sizes,X_morph_bin_count = generate_bin_sizes(len(X_morph))
    X_bool = conform_x_to_dist(X_morph,X_morph_bin_sizes,X_morph_bin_count)
    X = X[X_bool==True]
    y = y[X_bool==True]

    X_morph_control_bin_sizes,X_morph_control_bin_count = generate_bin_sizes(len(X_morph))
    X_bool_control = conform_x_to_dist(X_morph_control,X_morph_control_bin_sizes,X_morph_control_bin_count)
    X_control = X_control[X_bool_control==True]
    y_control = y_control[X_bool_control==True]

    return X,y,X_control,y_control



# In[167]:


# import seaborn as sns
# sns.distplot(X_morph[X_bool])
# sns.distplot(X_morph_control[X_bool_control])


# In[ ]:


# grayscale
# {'pca__n_components': 0.93,
#  'rforest__bootstrap': True,
#  'rforest__max_depth': 110,
#  'rforest__max_features': 0.3,
#  'rforest__min_samples_leaf': 3,
#  'rforest__min_samples_split': 8,
#  'rforest__n_estimators': 1200}


# In[ ]:


# color

# {'pca__n_components': 0.87,
#  'rforest__bootstrap': True,
#  'rforest__max_depth': 110,
#  'rforest__max_features': 0.3,
#  'rforest__min_samples_leaf': 3,
#  'rforest__min_samples_split': 8,
#  'rforest__n_estimators': 1200}
