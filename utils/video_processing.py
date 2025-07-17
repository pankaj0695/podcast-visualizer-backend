import os
import re
import json
import tempfile
import base64
import vertexai
from vertexai.generative_models import GenerativeModel
from moviepy import (
    VideoFileClip,
    ImageClip,
    CompositeVideoClip
)

def extract_video_key_moments(transcript_segments):
    """Extract key moments from video transcript using Vertex AI Gemini"""
    
    # Set up Vertex AI credentials
    credentials_base64 = os.environ.get("GOOGLE_CREDENTIALS_JSON_BASE64")
    if not credentials_base64:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON_BASE64 not found in environment variables")
    
    key_file_path = os.path.join(tempfile.gettempdir(), "key.json")
    with open(key_file_path, "w") as f:
        f.write(base64.b64decode(credentials_base64).decode("utf-8"))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path
    
    project_id = os.environ.get("GCP_PROJECT_ID")
    location = os.environ.get("LOCATION")
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel("gemini-2.5-flash")
    
    # Create transcript with timestamps
    transcript_text = "\n".join(
        f"[{round(seg['start'])}-{round(seg['end'])}] {seg['text']}" for seg in transcript_segments
    )
    
    prompt = f"""
You are a helpful assistant. Analyze the following podcast transcript and identify 2-3 key moments.
Return their start and end times.

Return the response in JSON format with the following structure:
[
  {{
    "title": "Brief descriptive title",
    "start": start_time_in_seconds,
    "end": end_time_in_seconds,
  }}
]

Make sure the time segments are around 30 seconds each (between 25-35 seconds). Focus on the most engaging and insightful moments that can standalone as short clips.

Transcript:
{transcript_text}
"""
    
    response = model.generate_content(prompt)
    result = response.text
    
    # Extract JSON from response
    json_match = re.search(r'\[.*?\]', result, re.DOTALL)
    if json_match:
        try:
            key_moments = json.loads(json_match.group(0))
            # Validate and clean up the moments
            validated_moments = []
            for moment in key_moments:
                if all(key in moment for key in ['title', 'start', 'end']):
                    # Ensure reasonable clip length (around 30 seconds, max 35)
                    duration = moment['end'] - moment['start']
                    if duration > 35:
                        moment['end'] = moment['start'] + 30
                    elif duration < 25:
                        moment['end'] = moment['start'] + 30
                    validated_moments.append(moment)
            return validated_moments
        except json.JSONDecodeError:
            pass
    
    raise ValueError("No valid JSON array found in the response.")

def create_video_clip_with_captions(video_path, moment, idx, transcript_segments):
    """Create a video clip with captions from the original video using MoviePy"""
    
    # Create output directory
    output_dir = "video_clips"
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the original video
    video = VideoFileClip(video_path)
    start_time = moment['start']
    end_time = moment['end']
    clip = video.subclipped(start_time, end_time)
    # Filter transcript segments to only those within the clip's start/end time
    clip_start = moment['start']
    clip_end = moment['end']
    filtered_segments = [seg for seg in transcript_segments if seg.get('start', 0) >= clip_start and seg.get('end', 0) <= clip_end]
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = 28
    img_files = []
    caption_clips = []
    # For each filtered transcript segment, chunk into 4-word captions and time them to the segment
    for seg in filtered_segments:
        words = seg['text'].split()
        seg_start = seg.get('start', 0)
        seg_end = seg.get('end', 0)
        seg_duration = seg_end - seg_start if seg_end > seg_start else clip.duration / len(filtered_segments)
        # Use key_moment.py style: chunks = [' '.join(words[i-3:i+1]) for i in range(len(words))]
        if len(words) <= 4:
            chunks = [' '.join(words)]
        else:
            chunks = [' '.join(words[max(0,i-3):i+1]) for i in range(len(words))]
        chunk_duration = seg_duration / len(chunks) if chunks else seg_duration
        for k, chunk in enumerate(chunks):
            img = make_caption_image_center(chunk, clip.w, clip.h, idx, len(img_files), font_path, font_size)
            img_files.append(img)
            # Calculate relative timing for the clip (subtract clip_start to make it relative)
            caption_start_time = (seg_start - clip_start) + k * chunk_duration
            caption_clips.append(
                ImageClip(img, transparent=True)
                    .with_start(caption_start_time)
                    .with_duration(chunk_duration)
                    .with_position(("center", "bottom"))
            )
    final = CompositeVideoClip([clip, *caption_clips]).with_duration(clip.duration)
    output_path = os.path.join(output_dir, f"clip_{idx+1}_{clip_start}s_to_{clip_end}s.mp4")
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=24
    )
    video.close()
    clip.close()
    for c in caption_clips:
        c.close()
    final.close()
    for fname in img_files:
        if os.path.exists(fname):
            os.remove(fname)
    return output_path

def make_caption_image_center(text, width, height, idx, chunk_idx, font_path, font_size):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (int(width), int(height)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0,0), text, font=font)
    x = (width - (bbox[2]-bbox[0]))//2
    y = height - (bbox[3]-bbox[1]) - 60  # Position at bottom with margin
    draw.rectangle([(x-10, y-10), (x+bbox[2]-bbox[0]+10, y+bbox[3]-bbox[1]+10)], fill=(0,0,0,180))
    draw.text((x, y), text, font=font, fill="white")
    fname = f"caption_video_{idx}_{chunk_idx}.png"
    img.save(fname)
    return fname

def chunk_caption_text(text, chunk_size=4):
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
