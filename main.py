from flask import Flask, request, jsonify, send_file
from gtts import gTTS
import google.generativeai as genai
import tempfile

app = Flask(__name__)

API_KEY = "AIzaSyDSYhQCYFe4Ldv-9TPVyvCYG3LKXUmC-A0"
genai.configure(api_key=API_KEY)

def get_gemini_model():
    return genai.GenerativeModel(model_name="gemini-1.5-flash")

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        query = data.get("query")

        if not query:
            return jsonify({"error": "Query is missing"}), 400

        model = get_gemini_model()
        response = model.generate_content(query)

        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        text = data.get("text")
        source_language = data.get("source_language")
        target_language = data.get("target_language")

        if not text or not target_language:
            return jsonify({"error": "Text and target_language are required"}), 400

        prompt = f"Translate the following text from {source_language or 'auto'} to {target_language}: {text}. Only give translated text as response"

        model = get_gemini_model()
        response = model.generate_content(prompt)

        return jsonify({"translated_text": response.text})

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get("text")
        language = data.get("language", "en")

        if not text:
            return jsonify({"error": "Text is required"}), 400

        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as temp_file:
            tts = gTTS(text=text, lang=language)
            tts.save(temp_file.name)

            response = send_file(temp_file.name, as_attachment=True, attachment_filename="output.mp3")
            return response

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

