import sys
import json
import requests

"""conv = {'month': '6', 'year': '2015'}
#s = json.dumps(conv)
#print s
s=conv
res = requests.get("http://127.0.0.1:5000/predict",params=s)
print res.text

res = requests.get("http://127.0.0.1:5000/balance")
print res.text


s = {'latitude': '40.7127837', 'longitude': '-74.00594130000002'}

res = requests.get("http://127.0.0.1:5000/nearestLocation", params = s)
print res.text

s = {'latitude': '40.7127837', 'longitude': '-74.00594130000002','day': 6}


res = requests.get("http://127.0.0.1:5000/openHours", params = s)
print res.text
"""
s = {'time': '13:25', 'day': '17-01-28','latitude': '40.7127837', 'longitude': '-74.00594130000002'}

res = requests.get("http://127.0.0.1:5000/scheduleAppointment", params = s)
print res.text

s = {'userid': 'vaibhavrsadfandi', 'password': 'sgfdgg','aid': 'dfgdfgessd33'}

res = requests.get("http://127.0.0.1:5000/login", params = s)
print res.text