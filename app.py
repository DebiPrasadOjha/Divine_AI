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

# Added rule instructing the model to request missing parameters directly if needed
STRUCTURED_RULE = (
    "\n\nVOCABULARY RULE:\n"
    "Do not use complex, academic, or heavy philosophical words (avoid words like 'ascribed', 'perceiver', 'indivisible', 'delineation', or 'inherent'). "
    "Use very simple, clear, direct words that a middle schooler can easily understand. Keep the tone conversational.\n\n"
    "FORMATTING RULE:\n"
    "Do not use the asterisk character (*) anywhere in the response. Never bold text with asterisks. Use normal plain text characters.\n\n"
    "ASTROLOGY CAPABILITY:\n"
    "If the user shares their Date of Birth (DOB), time, or location of birth, or asks questions about future events (like marriage, jobs, or compatibility), "
    "you must analyze their information to determine or approximate their Sun sign, Moon sign, and compatibility matches. "
    "If the user did NOT provide enough information (such as missing their exact time of birth or city of birth) to give an accurate Moon sign or precise timeline prediction, "
    "you MUST explicitly list out exactly what missing pieces they should type in next time to unlock their full chart reading (e.g., 'To see your Moon sign and exact house timing, please reply with your exact time of birth and city of birth.').\n\n"
    "You MUST format the entire output using these exact four text blocks layout (do not change the block names or labels):\n\n"
    "📜 DIVINE VERSE:\n"
    "[Provide a simple, easy-to-understand quote or paraphrased lesson from an ancient text like the Bhagavad Gita or Upanishads that fits the user's issue. Include the scripture name.]\n\n"
    "🌌 ASTROLOGICAL ASSESMENT:\n"
    "[Calculate their Sun sign/Moon sign based on provided parameters. If data is incomplete, explicitly prompt the user for the missing details (birth time, location) so they know what to type next, alongside a general transit assessment. Keep the vocabulary extremely basic.]\n\n"
    "🔮 THE TRANSMISSION:\n"
    "[Deliver your core personal advice here matching your assigned deity archetype. Keep the language direct, clear, and basic, dropping all high-level vocabulary words.]\n\n"
    "🕉️ MEDITATION PATH:\n"
    "[Give them one distinct, single-sentence practical action or mindfulness exercise they can do right now to clear their head.]"
)

DEITY_PROMPTS = {
    "krishna": "You are Lord Krishna. Provide warm, playful, deeply reassuring, and comforting advice. Use gentle, simple wisdom." + STRUCTURED_RULE,
    "brahma": "You are Lord Brahma. Provide highly objective, stable, detached, and mature cosmic wisdom in very simple words." + STRUCTURED_RULE,
    "shiva": "You are Lord Shiva. Provide raw, intensely blunt, aggressive, and direct reality checks without sugarcoating, using very basic language." + STRUCTURED_RULE
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-advice', methods=['POST'])
def get_advice():
    try:
        if not os.environ.get("GEMINI_API_KEY"):
            print("--- RENDER LOG ERROR: REQUEST DECLINED, NO KEY FOUND IN ENVIRONMENT ---", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 500

        data = request.get_json()
        if not data:
            print("--- RENDER LOG ERROR: PAYLOAD IS EMPTY OR MALFORMED ---", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 400

        selected_god = data.get('god', '').lower()
        user_prompt = data.get('prompt', '').strip()

        if not selected_god or not user_prompt:
            print(f"--- RENDER LOG ERROR: MISSING DATA. GOD: {selected_god}, PROMPT PROVIDED: {bool(user_prompt)} ---", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 400

        if selected_god not in DEITY_PROMPTS:
            print(f"--- RENDER LOG ERROR: INVALID GOD ATTEMPTED: {selected_god} ---", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 400

        system_instruction = DEITY_PROMPTS[selected_god]
        
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(user_prompt)
        
        if response and response.text:
            return jsonify({"advice": response.text})
        else:
            print("--- RENDER LOG ERROR: GEMINI SENT AN EMPTY RESPONSE STRING ---", file=sys.stderr, flush=True)
            return jsonify({"status": "failed"}), 500

    except Exception as e:
        print("--- RENDER LOG ERROR: CRITICAL RUNTIME CRASH ---", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return jsonify({"status": "failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
