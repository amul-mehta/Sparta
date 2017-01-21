from __future__ import print_function
from urllib2 import Request, urlopen, URLError
import json
import datetime as dt

# --------------- Helpers that build all of the responses ----------------------

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
    url = BackEndURL+'/balance'
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
    url = BackEndURL+'/nearest_bank'
    post_fields = {"latitude": lat, "longitude": lng}
    request = Request(url,data=str(post_fields))
    try:
        response = urlopen(request)
        content = json.loads(response.read())
        return content['nearestLocations']
    except URLError, e:
        print('Unable to get nearest bank. Got an error code:', e)

def build_speechlet_response(title, output, reprompt_text, should_end_session):
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

# --------------- Functions that control the skill's behavior ------------------

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
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# -------------- Attribute helpers -------------------

def add_location_to_attributes(session,address):
    session['attributes']['Location'] = getLatLug(address)

def log_intent_to_attributes(session,intent_name):
    if session.get('attributes', {}) and "IntentLog" in session.get('attributes', {}):
        session['attributes']['IntentLog'].append(intent_name)
    else:
        session['attributes']['IntentLog'] = [intent_name]

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

    if "value" in intent['slots']['Address']:
        address = intent['slots']['Address']['value']
        if "value" in intent['slots']['City']:
            address += intent['slots']['City']['value']
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

    for i in xrange(len(log)):
        if log[len(log)-i-1] == "GetNearestBranchIntent":
            return get_nearest_branch(intent, session)
        elif log[len(log)-i-1] == "AppointmentIntent":
            return make_appointment(intent, session)
    return get_welcome_response()

def make_appointment(intent,session):
    session_attributes = {}
    if session.get('attributes', {}):
        session_attributes = session['attributes']
    log = session['attributes']['IntentLog']

    if 'value' in intent['slots']['Time']:

        if 'value' in intent['slots']['Date']:
            date = intent['slots']['Date']['value']
        else:
            date = dt.datetime.today().strftime("%m/%d/%Y")

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
    elif intent_name == "AppointmentIntent":
        return make_appointment(intent, session)
    elif intent_name == "TransferMoneyIntent":
        return make_transfer(intent, session)
    elif intent_name == "GetOpenHourIntent":
        return get_open_hour(intent, session)
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
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
