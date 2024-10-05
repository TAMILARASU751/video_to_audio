from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from pydub import AudioSegment  # Ensure you have pydub installed for this to work
import ffmpeg  # Ensure you have ffmpeg installed

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert_video', methods=['POST'])
def convert_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    video_file = request.files['video']
    output_path = os.path.join('static', 'audio_output')

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Save the uploaded video file temporarily
    temp_video_path = os.path.join(output_path, video_file.filename)
    video_file.save(temp_video_path)

    audio_file_name = f"{os.path.splitext(video_file.filename)[0]}.mp3"  # Output file name
    audio_file_path = os.path.join(output_path, audio_file_name)

    try:
        # Use ffmpeg to convert the video to audio
        AudioSegment.from_file(temp_video_path).export(audio_file_path, format='mp3')

        return jsonify({'audio_url': f'/download/{audio_file_name}'}), 200
    except Exception as e:
        print(f"Error during conversion: {e}")  # Print the error for debugging
        return jsonify({'error': 'An error occurred during conversion.'}), 500
    finally:
        # Remove the temporary video file after conversion
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(os.path.join('static', 'audio_output'), filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
