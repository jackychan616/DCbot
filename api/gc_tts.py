"""Synthesizes speech from the input string of text."""
from google.cloud import texttospeech
from google.oauth2 import service_account
import os
credentials = 'C:/Users/jacky/AppData/Roaming/gcloud/application_default_credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials


class TTS():
    def __init__(self,text,Lang_code):
        self.text = text
        self.Lang_code =Lang_code
    async def getAudio(self):
        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(text=self.text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=self.Lang_code, ssml_gender=texttospeech.SsmlVoiceGender.FEMALE 
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=1
        )

        response = client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )
        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')
        return