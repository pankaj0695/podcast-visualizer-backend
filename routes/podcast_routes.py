from flask import Blueprint, request, jsonify
from controllers.podcast_controller import process_podcast, process_video_podcast, generate_abstract_summary, process_ai_podcast

podcast_bp = Blueprint('podcast', __name__)

@podcast_bp.route('/audio-podcast-key-moments', methods=['POST'])
def audio_podcast_key_moments():
    data = request.get_json()
    audio_url = data.get('audio_url')
    if not audio_url:
        return jsonify({'error': 'audio_url is required'}), 400
    video_urls = process_podcast(audio_url)
    return jsonify({'video_urls': video_urls})

@podcast_bp.route('/audio-podcast-ai-key-moments', methods=['POST'])
def audio_podcast_ai_key_moments():
    data = request.get_json()
    audio_url = data.get('audio_url')
    if not audio_url:
        return jsonify({'error': 'audio_url is required'}), 400
    
    try:
        video_urls = process_ai_podcast(audio_url)
        return jsonify({'video_urls': video_urls})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@podcast_bp.route('/video-podcast-key-moments', methods=['POST'])
def video_podcast_key_moments():
    data = request.get_json()
    video_url = data.get('video_url')
    if not video_url:
        return jsonify({'error': 'video_url is required'}), 400
    
    try:
        clip_urls = process_video_podcast(video_url)
        video_urls = [clip['url'] if isinstance(clip, dict) and 'url' in clip else clip for clip in clip_urls]
        return jsonify({'video_urls': video_urls})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@podcast_bp.route('/abstract-summary', methods=['POST'])
def abstract_summary():
    data = request.get_json()
    podcast_url = data.get('podcast_url')
    if not podcast_url:
        return jsonify({'error': 'podcast_url is required'}), 400
    
    try:
        summary = generate_abstract_summary(podcast_url)
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
