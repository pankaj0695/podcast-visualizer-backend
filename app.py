from flask import Flask
from flask_cors import CORS
from routes.podcast_routes import podcast_bp

app = Flask(__name__)

# Enable CORS to allow all origins
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.register_blueprint(podcast_bp)

if __name__ == '__main__':
    app.run(debug=True)
