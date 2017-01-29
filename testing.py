from urllib2 import Request, urlopen, URLError
import urllib
import json

#BackEndURL = 'http://ec2-35-162-32-145.us-west-2.compute.amazonaws.com:5000'
BackEndURL = 'https://python-hello-world-flask-amulmehta-2232.mybluemix.net'

def getLatLug(address):

	KEY = 'AIzaSyC6J06KCLzmvuoab3ve5asK0ygAOvF2wVc'
	address = address.replace(' ','+')
	link = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(address,KEY)
	request = Request(link)

	try:
		response = urlopen(request)
		content = json.loads(response.read())
		lat = content['results'][0]['geometry']['location']['lat']
		lng = content['results'][0]['geometry']['location']['lng']
		return (lat,lng)
	except URLError, e:
	    print('No GeoCode. Got an error code:', e)

def getBalance():
    url = 'http://ec2-35-162-32-145.us-west-2.compute.amazonaws.com:5000/balance'
    post_fields = {'userId':123}
    request = Request(url+'?'+urllib.urlencode(post_fields))
    try:
        response = urlopen(request)
        content = json.loads(response.read())

        return content['balance']
    except URLError, e:
        print('No Balance. Got an error code:', e)

def getNearestBank(location):
    lat,lng = location
    url = BackEndURL+'/nearestLocation'
    post_fields = {"latitude": lat, "longitude": lng}
    link = url +'?' + urllib.urlencode(post_fields)
    try:
        request = Request(link)
        #request.get_method = lambda: "POST"
        response = urlopen(request)
        content = json.loads(response.read())
        return content['nearestLocations']

    except URLError, e:
        print('Unable to get nearest bank. Got an error code:', e)
	

def getHour(location,day):
    lat,lng = location
    url = BackEndURL + '/openHours'
    post_fields = {"latitude": lat, "longitude": lng, "day": day}
    link = url +'?' + urllib.urlencode(post_fields)
    try:
        request = Request(link)
        response = urlopen(request)
        content = json.loads(response.read())
        return content['openHours']
    except URLError, e:
        print('Unable to get Hours, Got an error code: ', e)


def transfer(name,amount):
    url = BackEndURL + '/transferMoney'
    post_fields = {'name':name,'amount':amount}
    link = url +'?' + urllib.urlencode(post_fields)
    try:
        request = Request(link)
        response = urlopen(request)
        content = json.loads(response.read())
        message = content['message']
        amount = message.split(' ')[0]
        message = message[len(amount)+1:]
        if amount != 'Sorry,':
            amount = "{0:.2f}".format(round(float(amount),2)).split('.')
            amount = '{} dollars and {} cents '.format(amount[0], amount[1] if amount[1]!='00' else '')
            return amount+message+'.'
        return content['message']+'.'
    except URLError, e:
        print('Unable to transfer, Got an error code: ', e)


def appointment(date,time,location):
    url = BackEndURL + '/scheduleAppointment'
    post_fields = {'time':time,'day':date,'latitude':location[0],'longitude':location[1]}
    link = url + '?' + urllib.urlencode(post_fields)
    #print(link)
    try:
        request = Request(link)
        response = urlopen(request)
        content = json.loads(response.read())
        return content['message']
    except URLError, e:
        print('Unable to make appointment, Got an error code: ', e)

def predict(month,year):
    url = BackEndURL + '/predict'
    post_fields = {'month':month,'year':year}
    link = url + '?' + urllib.urlencode(post_fields)
    try:
        request = Request(link)
        response = urlopen(request)
        content = json.loads(response.read())
        return content['predict']
    except URLError, e:
        print('Unable to generate prediction, Got an error code: ', e)


import socket               # Import socket module




def sendToApp(message):
    url = '35.22.103.23'
    port = 6000
    s = socket.socket()  
    s.connect((url, port))
    s.sendall(message)
    s.close()


#print 'get balance',getBalance()

bostonLocation = getLatLug('detroit')
#print getNearestBank(bostonLocation)

print appointment('2017-01-22','13:30',bostonLocation)
sendToApp('Here I am! From Xueguang')




