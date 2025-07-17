from services.cloudinary_service import upload_video_to_cloudinary
from utils.transcription import download_audio, transcribe_audio, download_video, transcribe_video
from utils.key_moment import extract_key_moments, create_key_moment_clip
from utils.ai_key_moment import extract_ai_key_moments, create_ai_key_moment_clip
from utils.video_processing import extract_video_key_moments, create_video_clip_with_captions
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

def process_video_podcast(video_url):
    """Process video podcast to extract key moments with captions"""
    video_path = download_video(video_url)
    transcript_segments = transcribe_video(video_path)
    key_moments = extract_video_key_moments(transcript_segments)
    
    clip_urls = []
    import shutil
    
    for idx, moment in enumerate(key_moments):
        local_clip_path = None
        try:
            print(f"🎬 Creating video clip for moment: {moment.get('title', f'Moment {idx+1}')}")
            local_clip_path = create_video_clip_with_captions(video_path, moment, idx, transcript_segments)
            clip_url = upload_video_to_cloudinary(local_clip_path)
            clip_urls.append({
                'url': clip_url,
                'title': moment.get('title', f'Key Moment {idx+1}'),
                'description': moment.get('description', ''),
                'start_time': moment.get('start', 0),
                'end_time': moment.get('end', 0)
            })
            print(f"✅ Uploaded clip: {clip_url}")
            
            # Cleanup local clip file
            if os.path.exists(local_clip_path):
                os.remove(local_clip_path)
                
        except Exception as e:
            print(f"⚠️ Skipping moment {idx} due to error: {e}")
            # Cleanup local files if error occurs
            if local_clip_path and os.path.exists(local_clip_path):
                os.remove(local_clip_path)
    
    # Cleanup input video file
    if os.path.exists(video_path):
        os.remove(video_path)
    
    # Cleanup video_clips folder
    clips_dir = "video_clips"
    if os.path.exists(clips_dir) and os.path.isdir(clips_dir):
        shutil.rmtree(clips_dir)
    
    return clip_urls

def generate_abstract_summary(podcast_url):
    """Generate an abstract summary from podcast transcript"""
    import mimetypes
    from utils.vertex_ai_helper import generate_content_with_vertex_ai
    
    # Determine if it's audio or video based on URL
    content_type, _ = mimetypes.guess_type(podcast_url)
    
    if content_type and content_type.startswith('video'):
        # Process as video
        video_path = download_video(podcast_url)
        transcript_segments = transcribe_video(video_path)
        # Cleanup video file
        if os.path.exists(video_path):
            os.remove(video_path)
    else:
        # Process as audio
        audio_path = download_audio(podcast_url)
        transcript_segments = transcribe_audio(audio_path)
        # Cleanup audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
    
    # Create transcript text
    transcript_text = "\n".join([seg["text"] for seg in transcript_segments])
    
    # Generate abstract summary with markdown formatting
    prompt = f"""
You are a helpful assistant. Create a well-formatted markdown summary of the following podcast transcript (in 200 words).

The summary should be structured as follows:
1. **Overview** (2-3 sentences capturing the main theme)
2. **Key Points** (bullet points with the most important insights)
3. **Main Takeaways** (3-5 actionable insights or conclusions)

Format requirements:
- Use markdown headers (##), bold text (**text**), and bullet points (-)
- Write in first person as if the speaker is explaining ("I discussed...", "My main point is...")
- Keep the overview concise (100-120 words)
- Include 4-6 key points as bullet points
- Provide 3-5 main takeaways
- Use clear, engaging language that maintains the speaker's voice

Transcript:
{transcript_text}

Markdown Summary:
"""
    
    summary = generate_content_with_vertex_ai(prompt)
    
    return summary

def process_ai_podcast(audio_url):
    """Process audio podcast with AI-generated images instead of stock footage"""
    audio_path = download_audio(audio_url)
    transcript_segments = transcribe_audio(audio_path)
    key_moments = extract_ai_key_moments(transcript_segments)
    video_urls = []
    import shutil
    
    for idx, moment in enumerate(key_moments):
        local_video_path = None
        try:
            print(f"🎨 Creating AI clip for moment: {moment.get('script', f'Moment {idx+1}')[:50]}...")
            local_video_path = create_ai_key_moment_clip(moment, idx)
            video_url = upload_video_to_cloudinary(local_video_path)
            video_urls.append(video_url)
            print(f"✅ Uploaded AI clip: {video_url}")
            if os.path.exists(local_video_path):
                os.remove(local_video_path)
        except Exception as e:
            print(f"⚠️ Skipping AI moment {idx} due to error: {e}")
            # Cleanup local files if error occurs
            if local_video_path and os.path.exists(local_video_path):
                os.remove(local_video_path)
            if os.path.exists("input_audio.mp3"):
                os.remove("input_audio.mp3")
            ai_moments_dir = "ai_key_moments"
            if os.path.exists(ai_moments_dir) and os.path.isdir(ai_moments_dir):
                shutil.rmtree(ai_moments_dir)
    
    # Cleanup input audio file
    if os.path.exists("input_audio.mp3"):
        os.remove("input_audio.mp3")
    
    # Cleanup ai_key_moments folder
    ai_moments_dir = "ai_key_moments"
    if os.path.exists(ai_moments_dir) and os.path.isdir(ai_moments_dir):
        shutil.rmtree(ai_moments_dir)
    
    return video_urls
