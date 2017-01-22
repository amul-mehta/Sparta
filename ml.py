from operator import sub

from scipy.stats._discrete_distns import planck_gen
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import LabelBinarizer
import csv
from flask import Flask, request
import requests
import dateutil.parser



import json

app = Flask(__name__)

gmaps_key = 'AIzaSyCf-ptFKCPN9Tp5sxdx02nXBSsl8pZmSv8'

recipient = ['amul','aashish']

def predict_savings(month,year):
    income = XX[len(XX) - 1] [2]
    XY  = [ [ int(month),int(year),int(income) ] ]
    return model.predict(XY)




"""class Predict(Resource):
    def put(self):
        print request.data
        return {'q': predict(request.form['month'],request.form['year'])}


api.add_resource(Predict, '/predict')"""

@app.route('/predict', methods = ['GET'])
def predict():
    month = request.args.get('month')
    year = request.args.get('year')
    result = {'success':True, 'predict':int(predict_savings(month,year)[0])}
    return json.dumps(result)


@app.route('/balance', methods = ['GET'])
def balance():
    uid = request.args.get('userId')
    print uid
    result = {'success':True,'balance': balance}
    return json.dumps(result)

@app.route('/nearestLocation', methods = ['GET'])
def nearestLocation():
    lat = float(request.args.get('latitude'))
    lon = float(request.args.get('longitude'))
    success,res = getNearestLocation(lat,lon,False)
    if success:
        result = {'success':True, 'nearestLocations':res}
    else:
        result= {'success':False, 'nearestLocations':'null'}
    return json.dumps(result)


def getNearestLocation(lat,lon,placeId):
    payload={'location': str(lat) + ','+ str(lon) , 'radius' : 20000 , 'type': 'bank', 'keyword' : 'bank of america', 'key' : gmaps_key}
    r = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json',  params=payload)
    #https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=-33.8670522,151.1957362&radius=500&type=restaurant&keyword=cruise&key=YOUR_API_KEY
    #r = requests.put('https://maps.googleapis.com/maps/api/place/nearbysearch/json', )
    json_results = r.json()
    print json_results
    success = True
    add ='null'
    if(json_results['status'] != 'OK'):
        success = False
    else:
        add = json_results['results'][0]['vicinity']
        placeid = json_results['results'][0]['place_id']
        if placeId:
            return placeid
    return success,add



@app.route('/openHours', methods = ['GET'])
def openHours():
    lat = float(request.args.get('latitude'))
    lon = float(request.args.get('longitude'))
    dy = int(request.args.get('day'))

    success, res = getOpenHours(lat, lon,dy)
    if success:
        result = {'success': True, 'openHours': res}
    else:
        result = {'success': False, 'openHours': 'null'}
    return json.dumps(result)


def getOpenHours(lat,lon,day):
    placeId = getNearestLocation(lat,lon,True)
    payload={'placeid': placeId , 'key' : gmaps_key}
    r = requests.get('https://maps.googleapis.com/maps/api/place/details/json',  params=payload)
    #https://maps.googleapis.com/maps/api/place/details/json?placeid=ChIJN1t_tDeuEmsRUsoyG83frY4&key=YOUR_API_KEY
    #r = requests.put('https://maps.googleapis.com/maps/api/place/nearbysearch/json', )
    json_results = r.json()
    print json_results
    success = True
    add ='null'
    if(json_results['status'] != 'OK'):
        success = False
    else:
        today = ' '.join(json_results['result']['opening_hours']['weekday_text'][day-1].split(":")[1:]).replace(u'\u2013','-')
        tomorrow = ' '.join(json_results['result']['opening_hours']['weekday_text'][(day) % 7].split(":")[1:]).replace(u'\u2013','-')
        current =   json_results['result']['opening_hours']['open_now']
        success = True
        add = {'today':today,'tomorrow':tomorrow,'current':current}
    return success,add

######################################################################################################################################################


@app.route('/transferMoney', methods = ['GET'])
def transferMoney():
    success = False
    global balance
    msg = ""
    #input : contact name and amount
    name = request.args.get('name')
    amount = float(request.args.get('amount'))
    if (name in recipient) :
        if (amount < balance):
            balance = balance - amount
            success = True
            msg = str(amount) + " has been successfully submitted for transfer to "+ name
        else:
            msg = "Sorry, You do not have sufficient balance in your account"
    else:
        msg = "Sorry, Cannot find " + name + " in the recipient List"


    result = {"success": success,"message" : msg }
    return json.dumps(result)



@app.route('/scheduleAppointment', methods = ['GET'])
def scheduleAppointment():
    success = False
    msg = ""
    time = request.args.get('time')
    day = int(request.args.get('day'))
    lat = request.args.get('latitude')
    lon = request.args.get('longitude')
    datafile = open('appointment.csv', 'r')
    datareader = csv.reader(datafile, delimiter=',')
    data = []
    for row in datareader:
        data.append(row)
    print (data)

    # if date is of next month then reply no
    nearest = getNearestLocation(lat,lon,false)
    day = 10
    month = 2
    hour = 13
    min = 25
    diff = min - 30
    if diff < 0:
        min = 30
    else:
        min = 00
        hour = (hour + 1) % 24

    if hour >= 0 and hour < 9 :
        success = False
        msg = "Bank does not operate on these hours"
    elif hour >= 18 and hour <= 24:
        success = False
        msg = "Bank does not operate on these hours"

    return json.dumps({'lol' : 50})
    """
    if ( in recipient) :
        if (amount < balance):
            balance = balance - amount
            success = True
            msg = str(amount) + " has been successfully submitted for transfer to "+ name
        else:
            msg = "Sorry, You do not have sufficient balance in your account"
    else:
        msg = "Sorry, Cannot find " + name + " in the recipient List"


    result = {"success": success,"message" : msg }
    return json.dumps(result)"""






if __name__ == '__main__':

    balance = 5000.0

    with open('data.csv', 'rb') as f:
        reader = csv.reader(f)
        your_list = list(reader)

    X = your_list[1:]
    XX = []
    y = []
    for x in X:
        XX.append(x[:-1])
        y.append(int(float(x[-1:][0])))

    XX = [[int(k) for k in x] for x in XX]

    #print XX
    #print y

    classif = OneVsRestClassifier(estimator=SVC(random_state=0))
    model = classif.fit(XX, y)

    app.run(debug=True,host="0.0.0.0")


