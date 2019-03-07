import pymysql
import pymysql.cursors
import numpy as np
import pickle
import json
import pandas as pd


def get_connection(db_):
    ''' Prepares database-specific connection, which is used to be passed into sql connection functions. Expects a database name string.
    '''
    connect = pymysql.connect(host='localhost',
                                 user='user_insert',
                                 password='EhtcThisMachine!',
                                 db=db_,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connect


def insert_strip(array,metadata,orientation,strat_connection,table):
    '''
    Insert convolution strip into db
    '''


    try:
        with strat_connection.cursor() as cursor:
            query = ("INSERT INTO `{}` SET  id=%(id)s, x=%(x)s,orientation=%(orientation)s,tags=%(tags)s,label=%(label)s".format(table))
            data_entry ={
                    'id':metadata['id'],
                    'x':json.dumps(array.tolist()), # Can load again to numpy with json.loads()
                    'orientation':orientation,
                    'tags':json.dumps(metadata['tags']),
                    'label':metadata['label']
            }

            cursor.execute(query,data_entry)
            strat_connection.commit()
    except Exception as e:
        print(e)

    return True


def get_id_strips(strat_connection,table):
    '''
    Get convolution_strips from db
    '''
    try:
        with strat_connection.cursor() as cursor:
            query = ("SELECT * FROM `{}`".format(table))
            df = pd.read_sql(query,strat_connection)
    except Exception as e:
        print(e)
    return df

print('loaded connections')
