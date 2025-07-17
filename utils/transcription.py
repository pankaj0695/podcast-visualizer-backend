import requests

def download_audio(audio_url, filename="input_audio.mp3"):
    response = requests.get(audio_url)
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename

import whisper

def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["segments"]
