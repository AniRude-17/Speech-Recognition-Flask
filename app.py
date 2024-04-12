import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydub import AudioSegment
import speech_recognition as sr

app = Flask(__name__)
CORS(app)
recognizer = sr.Recognizer()


UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def convert_audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Speech recognition could not understand the audio"
    except sr.RequestError as e:
        return "Error with speech recognition service; {0}".format(e)



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        audio_data = AudioSegment.from_file(file_path, format="ogg")  # Change format to 'ogg'
        audio_data = audio_data.set_frame_rate(8000)  
        audio_data = audio_data.set_channels(1) 
        text="sample audio :)"
        with audio_data.export('./output.wav', format="wav", parameters=["-ar", "8000", "-ac", "1", "-ab", "8k"]) as wav_file:  # Specify parameters for the export
            with sr.AudioFile(wav_file) as source:  
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                print(text)    
        
        os.remove(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename, 'text': text}), 200


@app.route('/')
def hello_world():
    return 'The Knowledge Browser !!'

if __name__ == '__main__':
    app.run()
