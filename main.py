# Import required libraries
import openai
import asyncio
import re
import whisper
import boto3
import pydub
from pydub import playback
import speech_recognition as sr
from EdgeGPT import Chatbot, ConversationStyle
import json

# Set OpenAI API key
with open('config.json') as config_file:
    config = json.load(config_file)
    openai.api_key = config['openai_api_key']

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Define wake words
BING_WAKE_WORD = 'bing'
GPT_WAKE_WORD = 'gpt'

# Function to get wake word from the recognized phrase
def get_wake_word(phrase):
    if BING_WAKE_WORD in phrase.lower():
        return BING_WAKE_WORD
    elif GPT_WAKE_WORD in phrase.lower():
        return GPT_WAKE_WORD
    else:
        return None

# Function to synthesize speech using Amazon Polly
def synthesize_speech(text, output_filename):
    polly = boto3.client('polly', region_name='us-west-2')
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Salli',
        Engine='neural'
    )

    with open(output_filename, 'wb') as f:
        f.write(response['AudioStream'].read())


# Function to play audio file
def play_audio(file):
    sound = pydub.AudioSegment.from_file(file, format='mp3')
    playback.play(sound)


# Main async function
async def main():
    while True:
        # Capture audio with microphone
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print(f'Waiting for wake words \'ok bin\' or \'ok chat\'...')
            while True:
                # Listen for user input and transcribe
                audio = recognizer.listen(source)
                try:
                    with open('audio.wav', 'wb') as f:
                        f.write(audio.get_wav_data())
                    model = whisper.load_model('tiny')
                    result = model.transcribe('audio.wav')
                    phrase = result['text']
                    print(f'You said: {phrase}')

                    # Check if the wake word is present
                    wake_word = get_wake_word(phrase)
                    if wake_word is not None:
                        break
                    else:
                        print('Not a wake word. Try again.')
                except Exception as e:
                    print('Error transcribing audio: {0}'.format(e))
                    continue

            # Ask for prompt
            print('Speak a prompt...')
            synthesize_speech('What can I help you with?', 'response.mp3')
            play_audio('response.mp3')
            audio = recognizer.listen(source)

            # Transcribe user prompt
            try:
                with open('audio_prompt.wav', 'wb') as f:
                    f.write(audio.get_wav_data())
                model = whisper.load_model('base')
                result = model.transcribe('audio_prompt.wav')
                user_input = result['text']
                print(f'You said: {user_input}')
            except Exception as e:
                print('Error transcribing audio: {0}'.format(e))
                continue

            # Handle Bing wake word
            if wake_word == BING_WAKE_WORD:
                bot = Chatbot(cookiePath='cookies.json')
                response = await bot.ask(prompt=user_input, conversation_style=ConversationStyle.precise)

                for message in response['item']['messages']:
                    if message['author'] == 'bot':
                        bot_response = message['text']

                # Remove footnotes
                bot_response = re.sub('\[\^\d+\^\]', '', bot_response)

                # Get creative response from bot
                bot = Chatbot(cookiePath='cookies.json')
                response = await bot.ask(prompt=user_input, conversation_style=ConversationStyle.creative)
                for message in response['item']['messages']:
                    if message['author'] == 'bot':
                        bot_response = message['text']

                # Remove footnotes
                bot_response = re.sub('\[\^\d+\^\]', '', bot_response)


            # Handle GPT wake word
            else:
                response = openai.ChatCompletion.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {'role': 'system', 'content':
                         'You are a helpful assistant.'},
                        {'role': 'user', 'content': user_input},
                    ],
                    temperature=0.5,
                    max_tokens=150,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    n=1,
                    stop=['\nUser:'],
                )

                # Get bot response
                bot_response = response['choices'][0]['message']['content']

        # Output bot response and synthesize speech
        print('Bot\'s response:', bot_response)
        synthesize_speech(bot_response, 'response.mp3')
        play_audio('response.mp3')
        await bot.close()

# Run the main function
if __name__ == '__main__':
    asyncio.run(main())