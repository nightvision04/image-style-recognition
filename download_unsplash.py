
# coding: utf-8

# In[97]:


import requests
import json
import urllib
import time


class Image():
    
    def __init__(self,id,height,width,url_small,url_full):
        
        self.id = id
        self.height = height
        self.width = width
        self.url_small = url_small
        self.url_full = url_full
        self.aspect_r = height/width
        self.format= url.split('&fm=')[1].split('&')[0]
        
    def view(self):
        
        print(self.id)
        print(self.height)
        print(self.width)
        print(self.url)
        print('fmt:',self.format)
        
        return self
    
    def store_meta(self,result):
        
        # Write condensed meta
        filename = self.id+'.txt'
        meta = {'id':self.id,
        'height':self.height,
        'width':self.width,
        'url_small':self.url_small,
        'url_full':self.url_full,
        'aspect_r':self.aspect_r,
        'format':self.format
        }
        
        file = open(filename,”w”) 
        file.write(meta) 
        file.close() 
        
        # Write verbose meta
        filename = self.id+'_full.txt'
        file.write(result) 
        file.close() 
    
    def download(self):
        
        # If jpg
        if self.format=='jpg':
            filepath = 'unsplash/'+self.id+'.jpg'
            print(filepath)
            urllib.request.urlretrieve(self.url_small, filepath)
        return self

    

access_key = '31ee1eb531e43c16e7a2b34bfee6bdc11948b6431e89a78f1fb36c476a71ccab'
secret_key = 'eb92f7dd0889a7beea3ca0befdfa32f1f11dea4d98bacc292a8ca9a8a0f828dc'

query = 'people'

for i in range(5000):

    # Loop search/download every 90 seconds
    url = 'https://api.unsplash.com/search/photos?client_id='+access_key+'&query='+query+'&page='+i

    r = requests.get(url)

    for result in r.json()['results']:

        img = Image(result['id'],result['height'],result['width'],result['urls']['small'])
        img.store_meta(result)
        img.download()
        
    
    time.sleep(90)


# In[99]:



    
    

