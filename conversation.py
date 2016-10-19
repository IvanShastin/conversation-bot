import sys
import speech_recognition
import wolframalpha
import json

from watson_developer_cloud import ConversationV1
from watson_developer_cloud import WatsonException
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import TextToSpeechV1
from pyaudio import PyAudio
from getopt import getopt
from getopt import GetoptError

__author__ = 'Ruslan Iakhin'

def get_input_type(argv):
    input_type = 'text'

    if len(argv) <= 1:
        print("usage: %s --input <text|voice>" % argv[0])
        sys.exit(2)

    try:
        opts, args = getopt(argv[1:],"i:","input=")
        
        for opt, arg in opts:
            if opt == '--input':
                input_type = arg
            else:
                print("usage: %s --input <text|voice>" % argv[0])
                sys.exit(2)

    except GetoptError as error:
        print(error)
        sys.exit(2)
    return input_type

def pass_to_wolfram(app_id, query):
    response = ''
    client = wolframalpha.Client(app_id)
    response = client.query(query)
    return response
def pass_to_texttospeach(username, password, text):
    RATE      = 22050
    SAMPWIDTH = 2
    NCHANNELS = 1
    CHANK     = 2048
    ACCEPT    = 'audio/wav'

    texttospeach = TextToSpeechV1(
        username = username,
        password = password
    )

    response = texttospeach.synthesize(
        text   = text,
        accept = ACCEPT
    )
    audio = PyAudio()
    stream = audio.open(format=audio.get_format_from_width(SAMPWIDTH),
                        channels=NCHANNELS,
                        rate=RATE,
                        output=True)
    stream.write(response)
    stream.stop_stream()
    stream.close()
    audio.terminate()
def pass_to_toneanalizer(username, password, text):
    response = ''

    toneanalizer = ToneAnalyzerV3(
        username = username,
        password = password,
        version='2016-05-19'
    )

    response = toneanalizer.tone(
        text = text
    )
    return response

def pass_to_conversation(username, password, workspace, text, context):
    response = ''

    conversation = ConversationV1(
        username = username,
        password = password,
        version  = '2016-07-11'  
    )
    
    conversation_response = conversation.message(
        workspace_id = workspace,
        message_input= {'text': text },
        context = context
    )
    context = conversation_response['context']

    if len(conversation_response['output']['text']) > 0:
        for output_text in conversation_response['output']['text']:
            if len(output_text) > 0:
                response += output_text
    else:
        response = 'I didn`t understand you.'

    return context, response

def main(argv):
    conversation_context  = {}
    conversation_text     = ''
    conversation_response = ''
    input_type            = 'text'

    SPEECHTOTEXT_IBM_USERNAME = '9230abde-b92c-49ff-9ed7-7d23d4d3f9b5'
    SPEECHTOTEXT_IBM_PASSWORD = 'YV8ISnaxRhbJ'

    CONVERSATION_IBM_USERNAME = 'e3592cb8-04cd-4a02-a2df-00b9d890c2a0'
    CONVERSATION_IBM_PASSWORD = 'ouAZEesIzE2q'
    CONVERSATION_IBM_WORKSPACE= 'c5537e88-4bb6-4dbb-bc5b-f265a0586925'

    TEXTTOSPEECH_IBM_USERNAME = 'ad400dc7-4c75-42bb-abeb-638a24349e13'
    TEXTTOSPEECH_IBM_PASSWORD = 'TiZUvc5YgPav'

    TONEANALIZER_IBM_USERNAME = '50f87320-b579-41f5-8f2c-3500a703e9b7'
    TONEANALIZER_IBM_PASSWORD = 'Id4tqQbQN08i'

    WOLFRAM_APP_ID            = '7JJH75-G2WEATH25E'

    input_type = get_input_type(argv)
    
    if input_type == 'voice':
        speachrecognition = speech_recognition.Recognizer()

    conversation_context,conversation_response = pass_to_conversation(CONVERSATION_IBM_USERNAME, CONVERSATION_IBM_PASSWORD, CONVERSATION_IBM_WORKSPACE, conversation_text, conversation_context)
    pass_to_texttospeach(TEXTTOSPEECH_IBM_USERNAME, TEXTTOSPEECH_IBM_PASSWORD, conversation_response)
    print('Watson: %s' % conversation_response)

    while True:
        if input_type == 'voice':
            with speech_recognition.Microphone() as source:
                audio = speachrecognition.listen(source)

            try:
                conversation_text = speachrecognition.recognize_ibm(audio, username=SPEECHTOTEXT_IBM_USERNAME, password=SPEECHTOTEXT_IBM_PASSWORD)
            except speech_recognition.UnknownValueError:
                conversation_text = ''
            except speech_recognition.RequestError as error:
                conversation_text = ''

            print('You: %s' % conversation_text)
        else:
            if sys.version_info < (3,0):
                conversation_text = raw_input("You: ")
            else:
                conversation_text = input("You: ")

        if conversation_text == '':
            print('You: <not recognized, say again>')
        else:
            toneanalizer_response = pass_to_toneanalizer(TONEANALIZER_IBM_USERNAME, TONEANALIZER_IBM_PASSWORD, conversation_text)
            conversation_context,conversation_response = pass_to_conversation(CONVERSATION_IBM_USERNAME, CONVERSATION_IBM_PASSWORD, CONVERSATION_IBM_WORKSPACE, conversation_text, conversation_context)
            #pass_to_texttospeach(TEXTTOSPEECH_IBM_USERNAME, TEXTTOSPEECH_IBM_PASSWORD, conversation_response)
            print('Watson: %s' % conversation_response)

            print(conversation_context)
            for tone in toneanalizer_response['document_tone']['tone_categories'][0]['tones']:
                if tone['score'] > 0.5:
                    print(tone)
                    conversation_context['tone'] = tone['tone_name']

        if 'bye' in conversation_text:
            sys.exit(0)

if __name__ == '__main__':
    main(sys.argv)
