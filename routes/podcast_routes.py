from flask import Blueprint, request, jsonify
from controllers.podcast_controller import process_podcast

podcast_bp = Blueprint('podcast', __name__)

@podcast_bp.route('/audio-podcast-key-moments', methods=['POST'])
def audio_podcast_key_moments():
    data = request.get_json()
    audio_url = data.get('audio_url')
    if not audio_url:
        return jsonify({'error': 'audio_url is required'}), 400
    video_urls = process_podcast(audio_url)
    return jsonify({'video_urls': video_urls})
