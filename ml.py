from operator import sub

from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
import csv
from flask import Flask, request
import requests
from datetime import datetime
import sqlite3
import xgboost as xgb
import numpy as np
import json,os
#######################################################################################################################

app = Flask(__name__)

gmaps_key = 'AIzaSyCf-ptFKCPN9Tp5sxdx02nXBSsl8pZmSv8'

recipient = ['amul','luke','jack','joseph','john']

#######################################################################################################################
#todo : clean the code
def predict_savings(month,year):
    income = training[len(training) - 1] [2] #get most recent income and predict using it.
    trainData  = [ [ int(month),int(year),float(income) ] ]
    trainData = np.array(trainData)
    trainData = xgb.DMatrix(trainData)
    return bst.predict(trainData)

#######################################################################################################################

@app.route('/login', methods = ['GET'])
def login():
    userid = request.args.get('userid')
    paswd = request.args.get('password')
    aid = request.args.get('aid')

    conn = sqlite3.connect('usr.db')
    cursor = conn.cursor()
    print userid
    cursor.execute("SELECT count(*) FROM AUTH WHERE userid = ? and password = ?", (userid,paswd,))
    data = cursor.fetchone()[0]
    if data == 0:
        result = {'success': False, 'message': "Username,password combination does not match"}

    else:
        conn.execute("INSERT INTO AUTH (USERID,AID,PASSWORD) VALUES( ? , ? , ? )", (userid, aid, paswd))
        result = {'success': True, 'message': "Logged in successfuly"}

    conn.commit()
    conn.close()

    return json.dumps(result)

#######################################################################################################################

@app.route('/logout', methods = ['GET'])
def logout():
    userid = request.args.get('userid')
    aid = request.args.get('aid')
    # TODO : Logout from all the sessions.
    result = {'success': True, 'message': "Logged out successfuly"}
    return json.dumps(result)

#######################################################################################################################

def sendMessage(jsonRes):
    #test function to send the data directly to phone instead of
    ed= " echo -e " + str(jsonRes) +" | nc 35.22.103.23 6000 "
    os.system(ed)

#######################################################################################################################

@app.route('/predict', methods = ['GET'])
def predict():
    month = request.args.get('month')
    year = request.args.get('year')
    result = {'success':True, 'predict':int(predict_savings(month,year)[0])} # predict the savings based month and year.
    sendMessage(result)
    return json.dumps(result)

#######################################################################################################################

@app.route('/balance', methods = ['GET'])
def balance():
    # return available balance
    uid = request.args.get('userId')
    result = {'success':True,'balance': balance}
    sendMessage(result)                                                             
    return json.dumps(result)

#####################################################################################################################

@app.route('/nearestLocation', methods = ['GET'])
def nearestLocation():
    #get the latitude and longitude of the user-specified location or user's current location
    lat = float(request.args.get('latitude'))
    lon = float(request.args.get('longitude'))
    success,res = getNearestLocation(lat,lon,False) # get the information of the bank nearest to the given loacation.
    if success:
        result = {'success':True, 'nearestLocations':res}
    else:
        result= {'success':False, 'nearestLocations':'null'}
    return json.dumps(result)


def getNearestLocation(lat,lon,placeId):
    #search the nearest bank of america within 20kms of the given location
    payload={'location': str(lat) + ','+ str(lon) , 'radius' : 20000 ,
             'type': 'bank', 'keyword' : 'bank of america', 'key' : gmaps_key}
    r = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json',  params=payload)
    json_results = r.json()
    #print json_results
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

#######################################################################################################################

@app.route('/openHours', methods = ['GET'])
def openHours():
    #get operating hours of the nearest bank
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
    #get the open hours for the bank location
    placeId = getNearestLocation(lat,lon,True)
    payload={'placeid': placeId , 'key' : gmaps_key}
    r = requests.get('https://maps.googleapis.com/maps/api/place/details/json',  params=payload)
    json_results = r.json()
    print json_results
    success = True
    add ='null'
    if(json_results['status'] != 'OK'):
        success = False
    else:
        #get todays open hours
        today = ' '.join(json_results['result']['opening_hours']['weekday_text'][day-1].split(":")[1:]).replace(u'\u2013','-')
        #get tomorrows open hours
        tomorrow = ' '.join(json_results['result']['opening_hours']['weekday_text'][(day) % 7].split(":")[1:]).replace(u'\u2013','-')
        # is it currently open or not
        current =   json_results['result']['opening_hours']['open_now']
        success = True
        add = {'today':today,'tomorrow':tomorrow,'current':current}
    return success,add

#######################################################################################################################

@app.route('/transferMoney', methods = ['GET'])
def transferMoney():
    # Transfer money to the recipient
    success = False
    global balance
    msg = ""
    name = request.args.get('name')
    amount = float(request.args.get('amount'))
    # only transfer the amount if the name is in the recipient list
    if (name in recipient) :
        # if the amount to transfer is less than the available balance only then transfer the amount
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

#######################################################################################################################

@app.route('/scheduleAppointment', methods = ['GET'])
def scheduleAppointment():

    """
    Schedule appointment if the requested spot is free at that time. otherwise return the next three timeslots which are
    availabe.

    """

    success = True
    msg = ""
    time = request.args.get('time')
    day = request.args.get('day')
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    today = str(datetime.now())

    today_day = int(today.split()[0].split('-')[2])
    today_month = int(today.split()[0].split('-')[1])

    month = int(day.split('-')[1])
    day = int(day.split('-')[2])  # 0 - 29/30
    hour = int(time.split(':')[0])
    min = int(time.split(':')[1])

    if month != today_month or day < today_day :
        success = False
        msg = "Sorry, It is an Invalid Date"
        return json.dumps({'success': success, 'message': msg})

    # round to the nearest hour as the appointment are available at 30 min intervals.
    diff = min - 30
    print diff
    if diff == 0 or diff == -30:
        min = min
    elif diff < 0:
        min = 30
    else:
        min = 00
        hour = (hour + 1) % 24
    if (hour >= 0 and hour < 9) or (hour >= 18 and hour <= 24):
        success = False
        msg = "Bank does not operate on these hours"
        return json.dumps({'success': success, 'message': msg})

    day = day - 1  # change day so as to ease array access



    appointmentAvailabilityFile = open('appointment.csv', 'r')

    datareader = csv.reader(appointmentAvailabilityFile, delimiter=',')
    appointmentAvailability = []  # Contains the appointment availability data.

    firstRow = True
    for row in datareader:
        appointmentAvailability.append(row)

    appointmentAvailabilityFile.close()

    # get the array position mapping in the appointment availability data
    time_slot_hour = (hour - 9) * 2 # go to the starting hour index (operating-hours - 1 = 9)

    time_slot_min = min
    if time_slot_min == 30:
        time_slot_hour += 1

    print time_slot_hour,day
    if appointmentAvailability[day][time_slot_hour] != '1':
        success = True
        suc, nearest = getNearestLocation(latitude, longitude, False) # get the nearest location address
        msg = "Your appointment is successfully confirmed on " + getTimes([day, time_slot_hour]) + " at " + nearest
        appointmentAvailability[day][time_slot_hour] = '1'
        datafile = open('appointment.csv', 'wb')
        df = csv.writer(datafile, delimiter=',')
        df.writerows(appointmentAvailability)
        appointmentAvailabilityFile.close()

    elif appointmentAvailability[day][time_slot_hour] == '1':
        success = False
        msg = "Time Slot not available on the given date and place.  "
        first = getNextAppointments(appointmentAvailability, day, time_slot_hour)
        msg += "Next Available Appointments are at : "
        msg += getTimes(first[0]) + " , " + getTimes(first[1]) + " , " + getTimes(first[2])
    return  json.dumps({'success': success, 'message': msg})

def getNextAppointments(appointmentAvailability,day,time_slot):
    # get the next 3 available appointments

    first = []
    count = 0
    for slots in range(time_slot+1,len(appointmentAvailability[0])):
        #print appointmentAvailability[day][slots]
        if slots != '1':
            if count < 3:
                count += 1
                d_s = []
                d_s.append(day)
                d_s.append(slots)
                first.append(d_s)
            else:
                return first


    for days in range (day+1, len(appointmentAvailability)):
        for slots in range(0, len(appointmentAvailability[0])):
            if slots != '1':
                if count < 3:
                    count += 1
                    d_s = []
                    d_s.append(days)
                    d_s.append(slots)
                    first.append(d_s)
            else:
                return first
    return first

def getTimes(times):

    day = times[0]
    print day

    slot = times[1]
    extra = '00'
    if(slot % 2 == 0):
        slot = slot/2
    else :
        slot =int (slot / 2)
        extra = '30'
    slot = int(slot) + 9
    return str(day+1) + 'th '+str(slot)+':'+ extra

#######################################################################################################################

if __name__ == '__main__':

    conn = sqlite3.connect('usr.db')

    balance = 5000.0 # initial balance

    with open('data.csv', 'rb') as f:
        # data format : month, year, income, savings
        reader = csv.reader(f)
        accountData = list(reader)


    #print accountData

    rawData = accountData[1:] # data without the heading row

    #print rawData

    training = [] #month, year, income
    results = [] #avings

    for x in rawData:
        training.append(x[:-1])
        #print (x[:-1])
        results.append(float(x[-1:][0]))

    training = [[int(k) for k in x] for x in training]

    #print XX
    #print y

    #Todo : change the classifier
    """ classif = OneVsRestClassifier(estimator=SVC(random_state=0))
    model = classif.fit(training, results)
    income = training[len(training) - 1][2]
    test_data = [[int(5), int(2017), int(5000)]]
    model.predict(test_data) """

    dtrain = xgb.DMatrix(training, label=results)
    param = {'bst:max_depth': 5, 'bst:eta': 1, 'silent': 1, 'objective': 'reg:linear'}
    param['nthread'] = 4
    param['eval_metric'] = 'auc'
    plst = param.items()
    plst += [('eval_metric', 'ams@0')]

    num_round = 10
    bst = xgb.train(plst, dtrain, num_round)

    app.run(debug=True,host="0.0.0.0")


######################################################################################################################