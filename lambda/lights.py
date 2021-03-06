from __future__ import print_function
import json
import boto3

client = boto3.client('iot-data')

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(output, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hello World "
    reprompt_text = None
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(speech_output, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Goodbye "
    should_end_session = True
    return build_response({}, build_speechlet_response(speech_output, should_end_session))


def hello(intent, session):
    session_attributes = {}
    firstname = intent['slots']['firstname']['value']
    reprompt_text = None
    if firstname == 'junaid':
        speech_output = 'Hello <prosody rate="20%"> Jew </prosody><prosody rate="50%"><phoneme alphabet="ipa" ph="u"> u </phoneme></prosody><prosody rate="50%"><phoneme alphabet="ipa" ph="u"> u </phoneme></prosody><prosody rate="50%"><phoneme alphabet="ipa" ph="u"> u </phoneme></prosody><prosody rate="50%"><phoneme alphabet="ipa" ph="n"> n </phoneme></prosody><prosody pitch="+50%" rate="20%"><phoneme alphabet="ipa" ph="eɪ"> a </phoneme></prosody><prosody pitch="+50%" rate="20%"><phoneme alphabet="ipa" ph="eɪ"> a </phoneme></prosody><prosody pitch="+50%" rate="20%"><phoneme alphabet="ipa" ph="eɪ"> a </phoneme></prosody><prosody rate="50%"><phoneme alphabet="ipa" ph="d"> d </phoneme></prosody> Nice to Meet You'
    elif firstname == 'casey':
        speech_output = 'Hello <prosody rate="50%"><phoneme alphabet="ipa" ph="c"> c </phoneme></prosody><prosody rate="50%"><phoneme alphabet="ipa" ph="eɪ"> a </phoneme></prosody><prosody rate="50%"><phoneme alphabet="ipa" ph="eɪ"> a </phoneme></prosody><prosody rate="50%"><phoneme alphabet="ipa" ph="eɪ"> a </phoneme></prosody><prosody rate="50%"><phoneme alphabet="ipa" ph="eɪ"> a </phoneme></prosody><prosody rate="50%"><phoneme alphabet="ipa" ph="eɪ"> a </phoneme></prosody><prosody rate="50%"><phoneme alphabet="ipa" ph="eɪ"> a </phoneme></prosody> Nice to meet you'
    else:
        speech_output = 'Hello {} Nice to Meet You'.format(firstname)
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(speech_output, should_end_session))

def iot(intent, session):
    session_attributes = {}
    device_id = 'RaspberryPi'
    state = intent['slots']['lightstate']['value']
    # if state == 'on':
    #     print('on')
    # else:
    #     print('off')

    response = client.update_thing_shadow(
        thingName=device_id,
        payload=json.dumps({
            'state': {
                'desired': {
                    'lights': state,
                    'effect': 'none'
                }
            }
        })
    )

    speech_output = 'Now turning all of the lights {}'.format(state)
    return build_response(session_attributes, build_speechlet_response(speech_output, should_end_session=True))

def iot_effect(intent, session):
    session_attributes = {}
    device_id = 'RaspberryPi'
    effect = intent['slots']['lighteffect']['value']

    response = client.update_thing_shadow(
        thingName=device_id,
        payload=json.dumps({
            'state': {
                'desired': {
                    'lights': 'on',
                    'effect': effect
                }
            }
        })
    )

    speech_output = 'Now attempting to {} the lights'.format(effect)
    return build_response(session_attributes, build_speechlet_response(speech_output, should_end_session=True))

# --------------- Specific Events ------------------

def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    if intent_name == "HelloIntent":
        return hello(intent, session)
    elif intent_name == "IotIntent":
        return iot(intent, session)
    elif intent_name == "IotEffectIntent":
        return iot_effect(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


# --------------- Generic Events ------------------

def on_session_started(session_started_request, session):
    print(
        "on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
    return get_welcome_response()


def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
    print("event.session.application.applicationId=" + event['session']['application']['applicationId'])
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])