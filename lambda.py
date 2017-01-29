# Author: Xueguang Lu
# Banking Alexa skill support script
from __future__ import print_function
from urllib2 import Request, urlopen, URLError
import json
import datetime as dt
import urllib

# --------------- Helpers for calling API layer ----------------------

#BackEndURL = 'https://python-hello-world-flask-amulmehta-2232.mybluemix.net'
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
        response = urlopen(request)
        content = json.loads(response.read())
        return content['nearestLocations']

    except URLError, e:
        print('Unable to get nearest bank. Got an error code:', e)
    
def getHour(location,day):
    lat,lng = location
    print(location,day)
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
    post_fields = {'name':name.lower(),'amount':amount}
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
            amount = '{} dollars {}'.format(amount[0], "and "+amount[1]+' cents ' if amount[1]!='00' else '')
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
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
         'may':5,
         'jun':6,
         'jul':7,
         'aug':8,
         'sep':9,
         'oct':10,
         'nov':11,
         'dec':12
        }
    month = m[month[:3].lower()]
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

def sendToApp(message):
    url = '35.22.103.23'
    port = 6000
    #post_fields = {'m':name}
    #link = url + '?' + urllib.urlencode(post_fields)
    
    s = socket.socket()         # Create a socket object
    s.connect((url, port))
    s.sendall(message)
    s.close()

# -------------------- Response Builders -----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    #sendToApp(output)
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def build_my_response(session_attributes, card_title, output, reprompt_text):
    return build_response(session_attributes, build_speechlet_response(
        card_title,output,reprompt_text,False))

def parsehour(hour):
    result = ''
    hour = hour.split('-')
    for i in hour:
        i = i.strip().split(' ')
        for n in i:
            if n != '00':
                result+= n+' '
        result+='to '
    return result[:-4]

# --------------- Functions that control the skill's basic behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "How can I help you with your banking?" 
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You can ask about your balance, make transfers," \
                    " make appointments, inquire nearest branch information, etc. " 
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using Bank Buddy, " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# -------------- Attribute helpers -------------------

def add_location_to_attributes(session,address):
    session['attributes']['Location'] = getLatLug(address)

def log_intent_to_attributes(session,intent_name):
    if session.get('attributes', {}): 
        if "IntentLog" in session.get('attributes', {}):
            session['attributes']['IntentLog'].append(intent_name)
        else:
            session['attributes']['IntentLog'] = [intent_name]
    else:
        session['attributes'] = {'IntentLog':[intent_name]}
        
def add_date_time_to_attributes(session,datetime):
    session['attributes']['datetime'] = datetime

def add_weekday_to_attributes(session,weekday):
    session['attributes']['weekday'] = weekday

# -------------- Costom Intent Handlers -----------------

def query_balance(intent,session):
    session_attributes = {}
    if session.get('attributes', {}):
        session_attributes = session['attributes']
    card_title = intent['name']
    balance = getBalance() 
    balance = "{0:.2f}".format(round(balance,2)).split('.')
    speech_output = "Your available balance is currently {} dollars {} cents".format(balance[0],int(balance[1])) 
    reprompt_text = "Is there anything else I can help you?"
    return build_my_response(session_attributes,card_title,speech_output,reprompt_text)


def get_nearest_branch(intent,session):
    session_attributes = {}
    if session.get('attributes', {}):
        session_attributes = session['attributes']
    card_title = intent['name']
    address = ''
    if "value" in intent['slots']['Address']:
        address = intent['slots']['Address']['value']
    if "value" in intent['slots']['City']:
        address += intent['slots']['City']['value']
    if address != '':
        nearest_branch = getNearestBank(getLatLug(address))
        if not nearest_branch:
            speech_output = "There is currently no bank near you, we are working on it."
        else:
            speech_output = "I found a branch that is closest to you at "+nearest_branch
        reprompt_text = "Is there anything else I can help you?"
        add_location_to_attributes(session,address)
    else:
        speech_output = "Please give me an address so that I can search nearest branch for you."
        reprompt_text = speech_output
    return build_my_response(session_attributes,card_title,speech_output,reprompt_text)

def address_only(intent,session):
    session_attributes = {}
    if session.get('attributes', {}):
        session_attributes = session['attributes']
    log = session['attributes']['IntentLog']
    address = ''
    if "value" in intent['slots']['Address']:
        address = intent['slots']['Address']['value']
    if "value" in intent['slots']['City']:
        address += ', '+intent['slots']['City']['value']
    if address:
        add_location_to_attributes(session,address)

    for i in xrange(len(log)):
        if log[len(log)-i-1] == "GetNearestBranchIntent":
            return get_nearest_branch(intent, session)
        elif log[len(log)-i-1] == "AppointmentIntent":
            return make_appointment(intent, session)
        elif log[len(log)-i-1] == "GetOpenHourIntent":
            return get_open_hour(intent, session)
        elif log[len(log)-i-1] == "AppointmentIntent":
            return make_appointment(intent,session)
    return get_welcome_response()


def make_appointment(intent,session): 
    session_attributes = {}
    if session.get('attributes', {}):
        session_attributes = session['attributes']
    log = session['attributes']['IntentLog']
    today = dt.datetime.today().strftime("%Y-%m-%d")
    date = time = location = None

    if 'Time' in session_attributes:
        time = session_attributes['Time']
    if 'Date' in session_attributes:
        date = session_attributes['Date']
    if 'Location' in session_attributes:
        location = session_attributes['Location']

    if 'Time' in intent['slots'] and 'value' in intent['slots']['Time']:
        time = intent['slots']['Time']['value']
        session_attributes['Time'] = time
    if 'Date' in intent['slots'] and 'value' in intent['slots']['Date']:
        date = intent['slots']['Date']['value']
        session_attributes['Date'] = date
    else:
        date = today
    
    if not time:
        speech_output = 'What time do you want to schedule the appointment?'
    elif not location:
        speech_output = 'What location do you want to schedule the appointment? You can, say, 36 Main st.'
    else:
        # TODO try get appointment at the time 
        # on sucess:
        speech_output = appointment(date,time,location)
        #speech_output = 'We got you an appointment at {}{} sucessfully, see you then.'.format(time,date if date!=today else '')
    print(speech_output)
    return build_my_response(session_attributes,intent['name'],speech_output,speech_output)

def get_open_hour(intent,session):
    session_attributes = {}
    if session.get('attributes', {}):
        session_attributes = session['attributes']
    date = time = day = location = None
    if 'datetime' in session_attributes:
        [date, time] = session_attributes['datetime']
    if 'weekday' in session_attributes:
        day = session_attributes['weekday']
    
    if 'Location' in session_attributes:
        location = session_attributes['Location']
   
    if 'Date' in intent['slots'] and 'value' in intent['slots']['Date']:
        date = Intent['slots']['Date']['value']
    elif not day:
        day = dt.datetime.today().weekday()
    if "Time" in intent['slots'] and 'value' in intent['slots']['Time']:
        time = Intent['slots']['Date']['value']
    if 'Day' in intent['slots'] and 'value' in intent['slots']['Day']:
        day = Intent['slots']['Day']['value']

    if date and not day:
        year, month, day = (int(x) for x in date.split('-'))   
        day = datetime.date(year, month, day).weekday()

    if date or time:
        add_date_time_to_attributes(session,[date,time])
    if day:
        add_weekday_to_attributes(session,day)

    if not location:
        speech_output = "Please give me an address so that I can search nearest branch for you."
        reprompt_text = speech_output
        return build_my_response(session_attributes,intent['name'],speech_output,reprompt_text)

    hours = getHour(location,day)
    current = 'open' if hours['current'] else 'closed'
    today = parsehour(hours['today'])
    tomorrow = parsehour(hours['tomorrow'])
    tomorrow = 'bank open tomorrow from '+tomorrow if tomorrow != 'Closed' else 'tomorrow will {}be Closed all day.'.format('also ' if today=='Closed' else '')
    today = 'it opens today from '+today if today != 'Closed' else 'it\'s Closed today all day'
    speech_output = "Bank is currently {}, {}, {}".format(current,today,tomorrow)
    return build_my_response(session_attributes,intent['name'],speech_output,speech_output)


def make_transfer(intent,session):
    session_attributes = {}
    if session.get('attributes', {}):
        session_attributes = session['attributes']
    recipient = amount = None

    if 'Person' in session_attributes:
        recipient = session_attributes["Person"]
    if 'Amount' in session_attributes:
        amount = session_attributes['Amount']

    if 'Person' in intent['slots'] and 'value' in intent['slots']['Person']:
        recipient = intent['slots']['Person']['value']
        session_attributes['Person'] = recipient
    if 'Amount' in intent['slots'] and 'value' in intent['slots']['Amount']:
        amount = intent['slots']['Amount']['value']
        session_attributes['Amount'] = amount

    if amount and not recipient:
        speech_output = "Who do you want this transfer to go to? For example, say, to Luke."
    elif recipient and not amount:
        speech_output = "How much do you want this transfer to be? For example, say, 100 dollars."
    elif recipient and amount:
        speech_output = transfer(recipient,amount)
        del session_attributes['Amount']
        del session_attributes['Person']
    else:
        speech_output = "For transfering money, you can say: for example, transfer 100 dollars to Luke."
    return build_my_response(session_attributes,intent['name'],speech_output,speech_output)

def person_only_handler(intent,session):
    log = session['attributes']['IntentLog']
    for i in xrange(len(log)):
        if log[-2] == "TransferMoneyIntent":
            return make_transfer(intent, session)
    return get_welcome_response()


def predict_handler(intent,session):
    session_attributes = {}
    if session.get('attributes', {}):
        session_attributes = session['attributes']
    month = None

    if "Month" in session_attributes:
        month = session_attributes['Month']

    if "Month" in intent['slots'] and 'value' in intent['slots']['Month']:
        month = intent['slots']['Month']['value']
    
    if not month:
        speech_output = "Please tell me a speicifc month, for example, say, July."
    else:
        speech_output = "You expected saving for {} is {} dollars.".format(month,predict(month,2017))

    return build_my_response(session_attributes,intent['name'],speech_output,speech_output)


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    log_intent_to_attributes(session,intent_name)

    # Dispatch to your skill's intent handlers
    if intent_name == "GetBalanceIntent":
        return query_balance(intent, session)
    elif intent_name == "GetNearestBranchIntent":
        return get_nearest_branch(intent, session)
    elif intent_name == "AddressOnlyIntent":
        return address_only(intent,session)
    elif intent_name == "AppointmentIntent" or intent_name == "TimeOnlyIntent":
        return make_appointment(intent, session)
    elif intent_name == "TransferMoneyIntent" or intent_name == "MoneyOnlyIntent":
        return make_transfer(intent, session)
    elif intent_name == "PersonOnlyIntent":
        return person_only_handler(intent,session)
    elif intent_name == "GetOpenHourIntent":
        return get_open_hour(intent, session)
    elif intent_name == "PredictIntent" or intent_name == "MonthOnlyIntent":
        return predict_handler(intent,session)
    elif intent_name == "AMAZON.YesIntent":
        return yes_handler()
    elif intent_name == "AMAZON.NoIntent":
        return no_handler()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
         "amzn1.ask.skill.0fb6a300-ef40-4108-a5b8-aa7086bd3f48"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
