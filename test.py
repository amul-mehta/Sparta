import sys
import json
import requests

conv = {'month': '6', 'year': '2015'}
s = json.dumps(conv)
print s
res = requests.post("http://127.0.0.1:5000/predict",data=s)
print res.text

res = requests.post("http://127.0.0.1:5000/balance")
print res.text


conv = {'latitude': '40.7127837', 'longitude': '-74.00594130000002'}
s = json.dumps(conv)
res = requests.post("http://127.0.0.1:5000/nearestLocation", data = s)
print res.text

res = requests.post("http://127.0.0.1:5000/openHours", data = s)
print res.text

