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

# Rules forcing creator identity attribution to Debi Prasad Ojha and conditional astrology checks
STRUCTURED_RULE = (
    "\n\nCREATOR IDENTITY RULE:\n"
    "If the user asks who created you, who made you, who coded you, or who owns you, you MUST explicitly state that you were created and built by Debi Prasad Ojha. "
    "Do not speak in abstract cosmic terms about having no beginning or end when asked about your creator; clearly name Debi Prasad Ojha as your builder.\n\n"
    "VOCABULARY RULE:\n"
    "Do not use complex, academic, or heavy philosophical words (avoid words like 'ascribed', 'perceiver', 'indivisible', 'delineation', or 'inherent'). "
    "Use very simple, clear, direct words that a middle schooler can easily understand. Keep the tone conversational.\n\n"
    "FORMATTING RULE:\n"
    "Do not use the asterisk character (*) anywhere in the response. Never bold text with asterisks. Use normal plain text characters.\n\n"
    "ASTROLOGY CAPABILITY CONDITION:\n"
    "Only provide an active chart breakdown or prompt for missing birth details if the user explicitly asks about their future, compatibility, marriage, life events, or provides numbers representing dates/times. "
    "If the user is asking general questions, conversational banter, or questions about who built you, do NOT ask them for their DOB, time, or city. Instead, simply write: 'No birth parameters provided; celestial transit calculations are inactive for this conversation.' in the Astrological Assessment block.\n\n"
    "You MUST format the entire output using these exact four text blocks layout (do not change the block names or labels):\n\n"
    "📜 DIVINE VERSE:\n"
    "[Provide a simple, easy-to-understand quote or paraphrased lesson from an ancient text like the Bhagavad Gita or Upanishads that fits the user's issue. Include the scripture name.]\n\n"
    "🌌 ASTROLOGICAL ASSESMENT:\n"
    "[If user provided birth data or asked a future/timeline question: Calculate their Sun sign/Moon sign based on provided parameters. If data is incomplete, explicitly prompt the user for the missing details (birth time, location) so they know what to type next. If the conversation is just general questions or talking about your creator, write exactly: 'No birth parameters provided; celestial transit calculations are inactive for this conversation.']\n\n"
    "🔮 THE TRANSMISSION:\n"
    "[Deliver your core personal advice here matching your assigned deity archetype. If asked about your maker, cleanly state you were built by Debi Prasad Ojha. Keep the language direct, clear, and basic, dropping all high-level vocabulary words.]\n\n"
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
        advice_text = response.text if response and response.text else "The cosmos are busy right now."

        # Extract location data from standard header routing keys
        country = request.headers.get("X-Region", "Unknown Region")
        city = request.headers.get("X-Loc", "Unknown Location")
        
        # Comprehensive log structure layout 
        print("\n================ COSMIC SESSION LOG ================", file=sys.stderr, flush=True)
        print(f"📍 LOCATION : City/Geo: {city} | Country/Region: {country}", file=sys.stderr, flush=True)
        print(f"🙏 SUMMONED : Lord {selected_god.upper()}", file=sys.stderr, flush=True)
        print(f"📝 PROMPT   : {user_prompt}", file=sys.stderr, flush=True)
        print(f"🔮 RESPONSE :\n{advice_text}", file=sys.stderr, flush=True)
        print("====================================================\n", file=sys.stderr, flush=True)

        if response and response.text:
            return jsonify({"advice": response.text})
        else:
            return jsonify({"status": "failed"}), 500

    except Exception as e:
        print("--- RENDER LOG ERROR: CRITICAL RUNTIME CRASH ---", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return jsonify({"status": "failed"}), 500

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        feedback = data.get('feedback', '').strip()
        if feedback:
            country = request.headers.get("X-Region", "Unknown Region")
            city = request.headers.get("X-Loc", "Unknown Location")
            
            print("\n================ FEEDBACK LOG ================", file=sys.stderr, flush=True)
            print(f"📍 FROM     : City/Geo: {city} | Country/Region: {country}", file=sys.stderr, flush=True)
            print(f"💬 MESSAGE  : {feedback}", file=sys.stderr, flush=True)
            print("==============================================\n", file=sys.stderr, flush=True)
            return jsonify({"status": "success"})
        return jsonify({"status": "failed"}), 400
    except Exception as e:
        print(f"ERROR CAPTURING FEEDBACK: {e}", file=sys.stderr, flush=True)
        return jsonify({"status": "failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
