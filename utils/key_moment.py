import os
import requests
import base64
import tempfile
import vertexai
from vertexai.generative_models import GenerativeModel
import json
import re
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips
)

WIDTH, HEIGHT = 432, 768
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 28

PROMPT = '''You are a helpful assistant. Analyze the following podcast transcript and extract the top 3 most important key moments.\n\nFor each key moment, return:\n- `keywords`: An array of 5 to 6 **single-word**, highly descriptive keywords related to the visual theme or concept (e.g., ["technology", "innovation", "robotics", "future", "healthcare", "AI"]).\n- `script`: A **first-person summary** of the moment written in a natural, conversational tone (e.g., "I realized...", "We discussed..."). The script should be approximately **60–75 words**, or **25–30 seconds** when read aloud.\n\nMake the summaries insightful and engaging. Use **ONLY JSON format** in your response — do NOT include timestamps, speaker names, or bullet points.\n\nExample output:\n[\n  {\n    "keywords": ["AI", "robotics", "healthcare", "future", "data", "ethics", "technology"],\n    "script": "I talked about how artificial intelligence is completely transforming fields like healthcare and education. We explored how AI-driven tools are becoming more accessible and discussed the importance of responsible innovation. I realized the future isn't just about technology—it's also about how humans use it thoughtfully and ethically."\n  },\n  ...\n]\n\nTranscript:\n'''

def extract_key_moments(transcript_segments):
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
    transcript_text = "\n".join([t["text"] for t in transcript_segments])
    prompt = PROMPT + transcript_text
    response = model.generate_content(prompt)
    result = response.text
    json_match = re.search(r"\[\s*{.*?}\s*\]", result, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))
    raise ValueError("No valid JSON array found in the response.")

PEXELS_API_KEY = "WTNkkXXZ0fNZikmrKeRjhEM1lC5wQPZT4qcdc7haAPUDopfRXICU3z2H"

def fetch_stock_clip(keyword, duration=5):
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": keyword, "orientation": "portrait", "per_page": 1}
    resp = requests.get(url, headers=headers, params=params).json()
    if not resp.get("videos"):
        print(f"❌ No videos found for keyword: {keyword}")
        return None
    video_url = resp["videos"][0]["video_files"][0]["link"]
    local_path = f"{keyword}_clip.mp4"
    with open(local_path, "wb") as f:
        f.write(requests.get(video_url).content)
    return VideoFileClip(local_path).subclipped(0, duration).resized((WIDTH, HEIGHT))

def generate_caption_clips(script, idx, total_dur):
    words = script.split()
    chunks = [' '.join(words[i-3:i+1]) for i in range(len(words))]
    dur = total_dur / len(chunks)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    clips = []
    img_files = []
    for j, chunk in enumerate(chunks):
        img = Image.new("RGBA", (WIDTH, HEIGHT))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0,0), chunk, font=font)
        x = (WIDTH - (bbox[2]-bbox[0]))//2
        y = (HEIGHT - (bbox[3]-bbox[1]))//2
        draw.text((x,y), chunk, font=font, fill="white")
        fname = f"caption_{idx}_{j}.png"
        img.save(fname)
        img_files.append(fname)
        clips.append(
            ImageClip(fname, transparent=True)
                .with_start(j*dur)
                .with_duration(dur)
                .with_position("center")
        )
    return clips, img_files

def create_key_moment_clip(moment, idx):
    outdir = "key_moments"
    os.makedirs(outdir, exist_ok=True)
    audio_file = f"speech_{idx}.mp3"
    tts = gTTS(text=moment['script'], lang='en')
    tts.save(audio_file)
    audio = AudioFileClip(audio_file)
    total_dur = audio.duration
    clips = [c for kw in moment['keywords'] if (c := fetch_stock_clip(kw))]
    if not clips:
        raise Exception("No stock clips found")
    per = total_dur / len(clips)
    clips = [c.with_duration(per).resized((WIDTH, HEIGHT)) for c in clips]
    video = concatenate_videoclips(clips).with_duration(total_dur)
    captions, img_files = generate_caption_clips(moment['script'], idx, total_dur)
    final = CompositeVideoClip([video, *captions]).with_audio(audio).with_duration(total_dur)
    outfile = os.path.join(outdir, f"keymoment_{idx}.mp4")
    final.write_videofile(outfile, fps=24, codec="libx264", audio_codec="aac")
    audio.close()
    if os.path.exists(audio_file):
        os.remove(audio_file)
    for fname in img_files:
        if os.path.exists(fname):
            os.remove(fname)
    for c in clips:
        if hasattr(c, 'filename') and c.filename and os.path.exists(c.filename):
            os.remove(c.filename)
    return outfile
