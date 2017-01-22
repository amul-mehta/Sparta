from operator import sub

from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
import csv
from flask import Flask, request
import requests
import datetime
import sqlite3
import json

app = Flask(__name__)

gmaps_key = 'AIzaSyCf-ptFKCPN9Tp5sxdx02nXBSsl8pZmSv8'

recipient = ['amul','luke']

def predict_savings(month,year):
    income = XX[len(XX) - 1] [2]
    XY  = [ [ int(month),int(year),int(income) ] ]
    return model.predict(XY)




"""class Predict(Resource):
    def put(self):
        print request.data
        return {'q': predict(request.form['month'],request.form['year'])}


api.add_resource(Predict, '/predict')"""



@app.route('/login', methods = ['GET'])
def login():
    userid = request.args.get('userid')
    paswd = request.args.get('password')
    aid = request.args.get('aid')

    conn = sqlite3.connect('usr.db')
    cursor = conn.cursor()
    print userid
    cursor.execute("SELECT count(*) FROM AUTH WHERE userid = ?", (userid,))
    data = cursor.fetchone()[0]
    if data == 0:
        conn_str = "INSERT INTO AUTH (USERID,AID,PASSWORD) \
              VALUES (\'"+ userid + "\',\'"+ aid +"\',\'"+ paswd + "\')"
        print conn_str
        conn.execute(conn_str)
        result = {'success': True, 'message': "Logged in successfuly"}
    else:
        result = {'success': False, 'message': "User already logged in please log out from other sessions."}

    conn.commit()
    conn.close()

    return json.dumps(result)

@app.route('/logout', methods = ['POST'])
def logout():
    jsondata = request.data
    print jsondata
    data = json.loads(jsondata)
    userid = data['userid']
    aid = data['aid']

    conn = sqlite3.connect('usr.db')
    cursor = conn.cursor()

    cr = cursor.execute("DELETE FROM AUTH WHERE userid ="+userid+ " AND aid =" + aid)
    conn.commit()
    if cr.arraysize == 1 :
        result = {'success': True, 'message': "Logged out successfuly"}
    else:
        result = {'success': True, 'message': "Logged Out from every place."}

    conn.close()
    return json.dumps(result)



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
    #TODO : add reccomendations of next available time slots.
    success = True
    msg = ""
    time = request.args.get('time')
    day = request.args.get('day')
    lat = request.args.get('latitude')
    lon = request.args.get('longitude')
    datafile = open('appointment.csv', 'r')
    #datafile = open(, 'r')
    datareader = csv.reader(datafile, delimiter=',')
    data = []
    flag = True
    for row in datareader:
        if flag:
            flag = False
        else:
            data.append(row)
    print len(data)

    now = datetime.datetime.now().ctime()
    now_date =int(now.split()[2])
    print now_date
    # if date is of next month then reply no
    nearest = getNearestLocation(lat,lon,False)
    day = 21 #0-29/30
    month = 1
    hour = 13
    min = 25
    print "HELLOO"
    if now_date > (day+1):
        success = False
        msg = "Sorry, You entered an Invalid Date"
        return json.dumps({'success': success,'message':msg})

    diff = min - 30

    if diff < 0:
        min = 30
    else:
        min = 00
        hour = (hour + 1) % 24
    print hour
    print "HELLOO"
    if hour >= 0 and hour < 9 :
        success = False
        msg = "Bank does not operate on these hours"
    elif hour >= 18 and hour <= 24:
        success = False
        msg = "Bank does not operate on these hours"

    if not success:
        return json.dumps({'success': success, 'message': msg})
    print "HELLOO"
    time_slot_hour = (hour - 9) * 2
    print time_slot_hour

    time_slot_min = min - 00
    if time_slot_min >= 0:
        time_slot_hour+=1

    if data[day][time_slot_hour] != '1':
        success = True
        msg = "Your appointment is successfully confirmed at "+ getTimes([day,time_slot_hour])
        data[day][time_slot_hour] = '1'
        datafile.close()
        datafile = open('appointment.csv','w')
        df = csv.writer(datafile,delimiter=',')
        df.writerows(data)

    elif data[day][time_slot_hour] == '1':
        success = False
        msg = "Time Slot not available on the given date and place.  "
        first = getNextAppointments(data,day,time_slot_hour)
        msg += "Next Available Appointments are at : "
        msg += getTimes(first[0]) + " , " + getTimes(first[1]) + " , "+ getTimes(first[2])


    return json.dumps({'success': success, 'message': msg})


def getNextAppointments(data,day,time_slot_hour):
    first = []
    count = 0
    for days in range (0, len(data)):
        for slots in range(0, len(data[0])):
            if days == day:
                if(slots > time_slot_hour):
                    if slots != '1':
                        if count < 3:
                            count += 1
                            d_s = []
                            d_s.append(days)
                            d_s.append(slots)
                            first.append(d_s)
                    else:
                        return first
            elif days > day :
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
    return str(day) + 'th '+str(slot)+':'+ extra







if __name__ == '__main__':

    conn = sqlite3.connect('usr.db')

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


