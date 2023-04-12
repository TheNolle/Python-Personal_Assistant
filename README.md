# Voice-Activated Chatbot

This repository contains a voice-activated chatbot that listens for audio input, detects the wake word (either 'bing' or 'gpt'), and processes the user's request using either the Bing or GPT-3.5-turbo chat model. The resulting response is then synthesized into speech using Amazon Polly, and the audio is played back to the user.


## Requirements
To use this chatbot, you'll need the following libraries:
- openai
- asyncio
- re
- whisper
- boto3
- pydub
- speech_recognition
- EdgeGPT

Please make sure to install all the dependencies using the following command:
```py
pip install openai asyncio re whisper boto3 pydub SpeechRecognition EdgeGPT
```


## Configuration
Before using the chatbot, make sure to set up your OpenAI API key and Amazon Polly credentials.
1. Store your OpenAI API key in a config.json file:
```json
{
    "openai_api_key": "your-openai-api-key"
}
```

2. Configure your Amazon Web Services (AWS) credentials. You can do this by setting up the AWS CLI or by setting the following environment variables:
```bash
export AWS_ACCESS_KEY_ID=your-aws-access-key-id
export AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
export AWS_REGION=your-aws-region
```


## Running the Chatbot
To run the chatbot, simply execute the following command:
```py
python main.py
```

The chatbot will listen for the wake words 'ok bin' or 'ok chat' and respond to your voice commands using the Bing or GPT-3.5-turbo model, respectively.