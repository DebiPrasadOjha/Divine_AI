import os
import sys
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Safely handle configuration
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("CRITICAL LOG ERROR: GEMINI_API_KEY environment variable is missing completely!", file=sys.stderr, flush=True)

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
        data = request.get_json()
        if not data:
            print("LOG WARNING: Received empty request payload.", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 400

        selected_god = data.get('god', '').lower()
        user_prompt = data.get('prompt', '').strip()

        if not selected_god or not user_prompt:
            print("LOG WARNING: Missing god selection or prompt input fields.", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 400

        if selected_god not in DEITY_PROMPTS:
            print(f"LOG WARNING: Invalid deity selection attempted: {selected_god}", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 400

        if not os.environ.get("GEMINI_API_KEY"):
            print("CRITICAL LOG ERROR: Request dropped. GEMINI_API_KEY environment variable is not set on Render dashboard.", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 500

        # Run AI Generation
        system_instruction = DEITY_PROMPTS[selected_god]
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(user_prompt)
        
        if response and response.text:
            return jsonify({"advice": response.text})
        else:
            print("LOG ERROR: Gemini engine generated an empty response string.", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 500

    except Exception as e:
        # Technical errors are printed straight to terminal logs, completely out of sight from users
        print(f"CRITICAL BACKEND EXCEPTION ENCOUNTERED: {str(e)}", file=sys.stderr, flush=True)
        return jsonify({"status": "failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
