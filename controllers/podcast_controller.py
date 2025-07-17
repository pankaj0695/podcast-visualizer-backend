from services.cloudinary_service import upload_video_to_cloudinary
from utils.transcription import download_audio, transcribe_audio
from utils.key_moment import extract_key_moments, create_key_moment_clip
import os

def process_podcast(audio_url):
    audio_path = download_audio(audio_url)
    transcript_segments = transcribe_audio(audio_path)
    key_moments = extract_key_moments(transcript_segments)
    video_urls = []
    import shutil
    for idx, moment in enumerate(key_moments):
        local_video_path = None
        try:
            print(f"🎬 Creating clip for keywords: {moment['keywords']}")
            local_video_path = create_key_moment_clip(moment, idx)
            video_url = upload_video_to_cloudinary(local_video_path)
            video_urls.append(video_url)
            print(f"✅ Uploaded: {video_url}")
            if os.path.exists(local_video_path):
                os.remove(local_video_path)
        except Exception as e:
            print(f"⚠️ Skipping moment {idx} due to error: {e}")
            # Cleanup local files if error occurs
            if local_video_path and os.path.exists(local_video_path):
                os.remove(local_video_path)
            if os.path.exists("input_audio.mp3"):
                os.remove("input_audio.mp3")
            key_moments_dir = "key_moments"
            if os.path.exists(key_moments_dir) and os.path.isdir(key_moments_dir):
                shutil.rmtree(key_moments_dir)
    # Cleanup input audio file
    if os.path.exists("input_audio.mp3"):
        os.remove("input_audio.mp3")
    # Cleanup key_moments folder
    key_moments_dir = "key_moments"
    if os.path.exists(key_moments_dir) and os.path.isdir(key_moments_dir):
        shutil.rmtree(key_moments_dir)
    return video_urls
