from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import subprocess
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Allowed audio formats and their corresponding FFmpeg commands
SUPPORTED_FORMATS = {
    'mp3': {
        'extension': 'mp3',
        'ffmpeg_command': ['-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', '-f', 'mp3']
    },
    'm4a': {
        'extension': 'm4a',
        'ffmpeg_command': ['-vn', '-c:a', 'aac', '-b:a', '192k', '-f', 'mp4']
    },
    'aac': {  # Directly output to AAC format
        'extension': 'aac',
        'ffmpeg_command': ['-vn', '-c:a', 'aac', '-b:a', '192k', '-f', 'adts']
    },
    'wav': {
        'extension': 'wav',
        'ffmpeg_command': ['-vn', '-c:a', 'pcm_s16le', '-f', 'wav']
    },
    'ogg': {
        'extension': 'ogg',
        'ffmpeg_command': ['-vn', '-c:a', 'libvorbis', '-b:a', '192k', '-f', 'ogg']
    },
    'flac': {
        'extension': 'flac',
        'ffmpeg_command': ['-vn', '-c:a', 'flac', '-compression_level', '5', '-f', 'flac']
    }
}

# Ensure the output directory exists
OUTPUT_DIR = os.path.join('static', 'audio_output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert_video', methods=['POST'])
def convert_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No file provided.'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No selected file.'}), 400

    audio_format = request.form.get('audio_format', 'mp3').lower()
    if audio_format not in SUPPORTED_FORMATS:
        return jsonify({'error': 'Unsupported audio format.'}), 400

    # Secure the filename to prevent directory traversal attacks
    filename = secure_filename(video_file.filename)
    temp_video_path = os.path.join(OUTPUT_DIR, filename)
    video_file.save(temp_video_path)

    # Define output audio file path
    audio_extension = SUPPORTED_FORMATS[audio_format]['extension']
    audio_file_name = f"{os.path.splitext(filename)[0]}.{audio_extension}"
    audio_file_path = os.path.join(OUTPUT_DIR, audio_file_name)

    try:
        # Build FFmpeg command
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output files without asking
            '-i', temp_video_path  # Input file
        ] + SUPPORTED_FORMATS[audio_format]['ffmpeg_command'] + [
            audio_file_path  # Output file
        ]

        logging.debug(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}")

        # Execute FFmpeg command
        result = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Log FFmpeg output for debugging
        logging.debug(f"FFmpeg stdout: {result.stdout.decode('utf-8')}")
        logging.debug(f"FFmpeg stderr: {result.stderr.decode('utf-8')}")

        if result.returncode != 0:
            error_message = result.stderr.decode('utf-8')
            logging.error(f"FFmpeg error: {error_message}")
            return jsonify({'error': 'Conversion failed. Please check the file and try again.'}), 500

        # Successful conversion
        audio_url = f"/download/{audio_file_name}"
        return jsonify({'audio_url': audio_url}), 200

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred during conversion.'}), 500

    finally:
        # Remove the temporary video file after conversion
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
            logging.debug(f"Removed temporary file: {temp_video_path}")

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
