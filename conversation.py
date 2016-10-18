import sys
import speech_recognition

from watson_developer_cloud import ConversationV1
from watson_developer_cloud import WatsonException
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import TextToSpeechV1
from pyaudio import PyAudio

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

    SPEECHTOTEXT_IBM_USERNAME = '9230abde-b92c-49ff-9ed7-7d23d4d3f9b5'
    SPEECHTOTEXT_IBM_PASSWORD = 'YV8ISnaxRhbJ'

    CONVERSATION_IBM_USERNAME = 'e3592cb8-04cd-4a02-a2df-00b9d890c2a0'
    CONVERSATION_IBM_PASSWORD = 'ouAZEesIzE2q'
    CONVERSATION_IBM_WORKSPACE= '7d29a542-327b-4e49-807d-e933f199709f'

    TEXTTOSPEECH_IBM_USERNAME = 'ad400dc7-4c75-42bb-abeb-638a24349e13'
    TEXTTOSPEECH_IBM_PASSWORD = 'TiZUvc5YgPav'

    TONEANALIZER_IBM_USERNAME = '50f87320-b579-41f5-8f2c-3500a703e9b7'
    TONEANALIZER_IBM_PASSWORD = 'Id4tqQbQN08i'

    speachrecognition = speech_recognition.Recognizer()
    conversation_context,conversation_response = pass_to_conversation(CONVERSATION_IBM_USERNAME, CONVERSATION_IBM_PASSWORD, CONVERSATION_IBM_WORKSPACE, conversation_text, conversation_context)
    pass_to_texttospeach(TEXTTOSPEECH_IBM_USERNAME, TEXTTOSPEECH_IBM_PASSWORD, conversation_response)
    print('Watson: %s' % conversation_response)

    while True:
        '''
       with speech_recognition.Microphone() as source:
        audio = speachrecognition.listen(source)

        try:
            conversation_text = speachrecognition.recognize_ibm(audio, username=SPEECHTOTEXT_IBM_USERNAME, password=SPEECHTOTEXT_IBM_PASSWORD)
        except speech_recognition.UnknownValueError:
            conversation_text = ''
        except speech_recognition.RequestError as error:
            conversation_text = ''
        '''

        conversation_text = input("You: ")

        if conversation_text == '':
            print('You: <not recognized, say again>')
        else:
            #toneanalizer_response = pass_to_toneanalizer(TONEANALIZER_IBM_USERNAME, TONEANALIZER_IBM_PASSWORD, conversation_text)
            conversation_context,conversation_response = pass_to_conversation(CONVERSATION_IBM_USERNAME, CONVERSATION_IBM_PASSWORD, CONVERSATION_IBM_WORKSPACE, conversation_text, conversation_context)
            pass_to_texttospeach(TEXTTOSPEECH_IBM_USERNAME, TEXTTOSPEECH_IBM_PASSWORD, conversation_response)
            print('Watson: %s' % conversation_response)

        if 'bye' in conversation_text:
            sys.exit(0)

if __name__ == '__main__':
    main(sys.argv)
