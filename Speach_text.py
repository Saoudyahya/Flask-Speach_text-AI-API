import os
from flask import Flask, request, jsonify
from datetime import datetime
from faster_whisper import WhisperModel
from flask_cors import CORS
import io

# Specify the directory for the model
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'whisper_models')
os.makedirs(MODEL_DIR, exist_ok=True)

app = Flask(__name__)

# Configure allowed extensions and CORS
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'm4a', 'flac'}
CORS(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Increase the timeout if needed
from werkzeug.serving import WSGIRequestHandler
WSGIRequestHandler.timeout = 120

# Load the Faster-Whisper model
model = WhisperModel("tiny", device="cpu", download_root=MODEL_DIR)

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def format_timestamp(seconds):
    """Convert seconds to MM:SS format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No file part',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 400
    
    file = request.files['file']
    
    # If no file is selected, the browser submits an empty file without a filename
    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'No selected file',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 400
    
    # Check if file is allowed
    if file and allowed_file(file.filename):
        try:
            # Read file into memory
            audio_bytes = file.read()
            
            # Print processing message
            print(f"\nProcessing audio file: {file.filename}")
            print("-" * 50)
            
            # Transcribe the audio file directly from memory
            segments, info = model.transcribe(io.BytesIO(audio_bytes))
            
            # Extract and print the transcribed text
            transcribed_text = ""
            print("\nTranscription:")
            print("=" * 50)
            transcription_segments = []
            for segment in segments:
                transcribed_text += f"{segment.text} "
                # Print each segment with timestamp
                print(f"[{segment.start:.2f}s - {segment.end:.2f}s]: {segment.text}")
                
                # Prepare segments for JSON response
                transcription_segments.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text
                })
            
            print("=" * 50)
            print(f"Total duration: {info.duration:.2f} seconds")
            print("-" * 50 + "\n")
            
            # Format the response
            response_data = {
                'filename': file.filename,
                'duration': info.duration,
                'transcription': transcribed_text.strip(),
                'segments': transcription_segments
            }
            
            return jsonify({
                'status': 'success',
                'data': response_data,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            # Print error message
            print(f"\nError during transcription: {str(e)}")
            
            return jsonify({
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }), 500
    
    print("Error: File type not allowed")
    return jsonify({
        'status': 'error',
        'message': 'File type not allowed',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }), 400

@app.route('/transcribe2', methods=['POST'])
def transcribe_audios():
    # For now, returning a static response
    response_data = "Your transcribed text or other data here"
    
    return jsonify({
        'status': 'success',
        'data': response_data,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)