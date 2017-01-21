from urllib2 import Request, urlopen, URLError
import urllib
import json

BackEndURL = 'http://ec2-35-162-32-145.us-west-2.compute.amazonaws.com:5000'

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
    request = Request(url,data=str(post_fields))
    try:
        response = urlopen(request)
        content = json.loads(response.read())
        return content['balance']
    except URLError, e:
        print('No Balance. Got an error code:', e)

def getNearestBank(location):
    lat,lng = location
    url = BackEndURL+'/nearestLocation/json?'
    post_fields = {"latitude": str(lat), "longitude": str(lng)}
    data = urllib.urlencode(post_fields)
    print data
    request = Request(url,data=data)
    #request.get_method = lambda: "POST"
    response = urlopen(request)
    content = json.loads(response.read())
    return content['nearestLocations']

    '''
    try:
    except URLError, e:
        print('Unable to get nearest bank. Got an error code:', e)
	'''

bostonLocation = getLatLug('Boston')
print bostonLocation
print getNearestBank(bostonLocation)






