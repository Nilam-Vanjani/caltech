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

class API:
    def _init_(
        self,
        endpoint="https://api.ocr.space/parse/image",
        api_key="K89122345988957",  
        language="eng",
        **kwargs,
    ):
        self.endpoint = endpoint
        self.payload = {
            "isOverlayRequired": True,
            "apikey": api_key,
            "language": language,
            "OCREngine": 2,
            **kwargs,
        }

    def _parse(self, raw):
        if type(raw) == str:
            raise Exception(raw)
        if raw["IsErroredOnProcessing"]:
            raise Exception(raw["ErrorMessage"][0])
        return raw["ParsedResults"][0]["ParsedText"]

    def ocr_base64(self, base64image):
        data = self.payload
        data["base64Image"] = base64image
        r = requests.post(
            self.endpoint,
            data=data,
        )
        return self._parse(r.json())


@app.route("/extract_text", methods=["POST"])
def extract_text():
    try:
        data = request.get_json()
        image_data = data.get("image")
        if not image_data:
            return jsonify({"error": "No Base64 image data provided"}), 400

        ocr_api = API(api_key="K89122345988957")  

        extracted_text = ocr_api.ocr_base64(image_data)

        if not extracted_text:
            return jsonify({"error": "Could not extract text from the image"}), 400

        return jsonify({"extracted_text": extracted_text})

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

