import requests
import whisper

def download_audio(audio_url, filename="input_audio.mp3"):
    response = requests.get(audio_url)
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename

def download_video(video_url, filename="input_video.mp4"):
    """Download video from URL"""
    response = requests.get(video_url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return filename

def transcribe_audio(audio_path):
    """Transcribe audio using local OpenAI Whisper model"""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["segments"]

def transcribe_video(video_path):
    """Transcribe video file using local OpenAI Whisper model with word timestamps"""
    model = whisper.load_model("base")
    result = model.transcribe(video_path, word_timestamps=True)
    
    # Extract transcript with start/end times
    segments = result["segments"]
    transcript_with_timestamps = [
        {"start": seg["start"], "end": seg["end"], "text": seg["text"]} 
        for seg in segments
    ]
    
    return transcript_with_timestamps
