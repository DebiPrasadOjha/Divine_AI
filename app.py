import os
import sys
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Reverting back to environment variables to pass GitHub's secret scanner security checks
API_KEY = os.environ.get("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("LOG ERROR: GEMINI_API_KEY environment variable is not set yet.", file=sys.stderr, flush=True)

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
        # Final fallback safety check to avoid silent 500 exceptions on the frontend UI
        if not os.environ.get("GEMINI_API_KEY"):
            print("LOG ERROR: API request dropped because GEMINI_API_KEY is completely missing from Render.", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 500

        data = request.get_json()
        if not data:
            return jsonify({"status": "failed"}), 400

        selected_god = data.get('god', '').lower()
        user_prompt = data.get('prompt', '').strip()

        if not selected_god or not user_prompt:
            return jsonify({"status": "failed"}), 400

        if selected_god not in DEITY_PROMPTS:
            return jsonify({"status": "failed"}), 400

        # Execute content generation
        system_instruction = DEITY_PROMPTS[selected_god]
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(user_prompt)
        
        if response and response.text:
            return jsonify({"advice": response.text})
        else:
            print("LOG ERROR: Gemini engine returned an empty response.", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 500

    except Exception as e:
        print(f"LOG EXCEPTION: {str(e)}", file=sys.stderr, flush=True)
        return jsonify({"status": "failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
