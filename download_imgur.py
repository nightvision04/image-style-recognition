
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
        self.aspect_r = int(height)/int(width)
        self.format= 'jpg'

    def view(self):

        print(self.id)
        print(self.height)
        print(self.width)
        print(self.url)
        print('fmt:',self.format)

        return self

    def store_meta(self,result):

        # Write condensed meta
        filename = 'imgur/metadata/'+self.id+'.txt'
        meta = {
        'id':self.id,
        'height':self.height,
        'width':self.width,
        'url_small':self.url_small,
        'url_full':self.url_full,
        'aspect_r':self.aspect_r,
        'format':self.format
        }

        file = open(filename,'w')
        file.write(json.dumps(meta))
        file.close()

        # Write verbose meta
        filename = 'imgur/metadata/'+self.id+'_full.txt'
        file = open(filename,'w')
        file.write(json.dumps(result))
        file.close()

    def download(self):

        # If jpg
        if self.format=='jpg':
            filepath = 'imgur/images/'+self.id+'.jpg'
            response = requests.get(self.url_small)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)





        return self



clientId='67009bcf62d03cf'



for i in range(1,5000):

    query = 'people'
    url = 'https://api.imgur.com/3/gallery/search/{{sort}}/{{window}}/{}?q=people'.format(i)
    payload = {}
    headers = {
      'Authorization': 'Client-ID 67009bcf62d03cf'
    }
    response = requests.request('GET', url, headers = headers, data = payload, allow_redirects=False, timeout=7200)

    print('Retrieving page {0}'.format(i))
    print(url)


    for j in range(50):

        try:
            if response.json()['data'][j]['images'][0]['type'] == 'image/jpeg':
                #Do something

                url = response.json()['data'][j]['images'][0]['link']
                id = response.json()['data'][j]['id']
                width = response.json()['data'][j]['cover_width']
                height = response.json()['data'][j]['cover_height']

                img = Image(id,height,width,url,url)
                img.store_meta(response.json()['data'][j])
                img.download()


        except Exception as e:
            print(e)







    time.sleep(90)


# In[99]:
