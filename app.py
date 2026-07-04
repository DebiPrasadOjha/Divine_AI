import os
import sys
import traceback
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Fetch the API key safely from Render Settings
API_KEY = os.environ.get("GEMINI_API_KEY")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        print("--- RENDER LOG ERROR: CONFIGURATION FAILED ---", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
else:
    print("--- RENDER LOG ERROR: GEMINI_API_KEY IS MISSING IN ENVIRONMENT ---", file=sys.stderr, flush=True)

DEITY_PROMPTS = {
    "krishna": "You are Lord Krishna. Provide warm, playful, deeply reassuring, and comforting advice. Use gentle wisdom.",
    "brahma": "You are Lord Brahma. Provide highly objective, stable, detached, and mature cosmic wisdom.",
    "shiva": "You are Lord Shiva. Provide raw, intensely blunt, aggressive, and direct reality checks without sugarcoating."
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-advice', methods=['POST'])
def get_advice():
    try:
        # Check variable before parsing payload
        if not os.environ.get("GEMINI_API_KEY"):
            print("--- RENDER LOG ERROR: REQUEST DECLINED, NO KEY FOUND ---", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 500

        data = request.get_json()
        if not data:
            print("--- RENDER LOG ERROR: PAYLOAD IS EMPTY OR MALFORMED ---", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 400

        selected_god = data.get('god', '').lower()
        user_prompt = data.get('prompt', '').strip()

        if not selected_god or not user_prompt:
            print(f"--- RENDER LOG ERROR: MISSING DATA. GOD: {selected_god}, PROMPT: {bool(user_prompt)} ---", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 400

        if selected_god not in DEITY_PROMPTS:
            print(f"--- RENDER LOG ERROR: INVALID GOD ATTEMPTED: {selected_god} ---", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 400

        # Run Generation Process
        system_instruction = DEITY_PROMPTS[selected_god]
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(user_prompt)
        
        if response and response.text:
            return jsonify({"advice": response.text})
        else:
            print("--- RENDER LOG ERROR: GEMINI SENT AN EMPTY RESPONSE STRING ---", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 500

    except Exception as e:
        # Pushes the complete full raw traceback stack to your Render logs terminal view
        print("--- RENDER LOG ERROR: CRITICAL RUNTIME CRASH ---", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return jsonify({"status": "failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
