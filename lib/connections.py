import pymysql
import pymysql.cursors
import numpy as np
import pickle
import json
import pandas as pd
import hashlib
import datetime


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


def clear_table(table):
    connection = get_connection('image_profile')

    try:
        with connection.cursor() as cursor:
            query = ("DELETE FROM {};").format(table)
            cursor.execute(query)
            connection.commit()
            print('Cleared data from {}'.format(table))
    except Exception as e:
        print(e)
    connection.close()

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


def check_credentials(email,password,ip,connection):

    password = password.encode('utf-8')
    m = hashlib.sha1()
    m.update(password)
    result = m.hexdigest()
    print(result)
    print(ip)

    try:
        with connection.cursor() as cursor:
            query = ("SELECT `password` FROM `users` WHERE `email`=%(email)s;")
            data_entry = {
                'email':email
            }
            df = pd.read_sql(query, connection,params=data_entry)
            if len(df) == 0:
                return False

            m = hashlib.sha1()
            m.update(password)
            result = m.hexdigest()
            print(df.iloc[0]['password'])
            if df.iloc[0]['password'] == result:

                query = ("INSERT INTO `login_attempts` SET `email`=%(email)s,`status`=%(status)s,`datetime`=%(datetime)s,`ip`=%(ip)s;")
                data_entry = {
                    'email':email,
                    'status': 'success',
                    'datetime': datetime.datetime.now(),
                    'ip':ip
                }
                cursor.execute(query,data_entry)
                connection.commit()

                print('Login success')

                return True
            else:
                query = ("INSERT INTO `login_attempts` SET `email`=%(email)s,`status`=%(status)s,`datetime`=%(datetime)s,`ip`=%(ip)s ;")
                data_entry = {
                    'email':email,
                    'status': 'failed',
                    'datetime':datetime.datetime.now(),
                    'ip':ip
                }
                cursor.execute(query,data_entry)
                connection.commit()
                print('Login failed')
                return False

    except Exception as a:
        print ("SQL ERROR: "+str(a))
        return False
