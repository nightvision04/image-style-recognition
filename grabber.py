import requests
import json


access_key = '31ee1eb531e43c16e7a2b34bfee6bdc11948b6431e89a78f1fb36c476a71ccab'
secret_key = 'eb92f7dd0889a7beea3ca0befdfa32f1f11dea4d98bacc292a8ca9a8a0f828dc'

query = input()
url = 'https://api.unsplash.com/search/photos?client_id='+access_key+'&query='+query

print(url)

r = requests.get(url)

print(r.json())
