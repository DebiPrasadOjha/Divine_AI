import os
import re
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__, static_folder="static", template_folder="templates")

API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_ACTUAL_API_KEY_HERE")
client = genai.Client(api_key=API_KEY)

PERSONAS = {
    "krishna": "You are Lord Krishna giving advice. Your tone must be jolly, warm, loving, reassuring, and slightly playful. Use metaphors related to love, a flute, or timeless life lessons.",
    "brahma": "You are Lord Brahma, the creator. Your tone must be entirely neutral, highly mature, calm, objective, and deeply philosophical. Speak with the weight of absolute wisdom.",
    "shiva": "You are Lord Shiva. Your tone must be raw, intensely direct, fierce, and borderline angry. No sweet talk. Tell the user exactly what bitter truth they need to face and what action must be taken immediately."
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-advice', methods=['POST'])
def get_advice():
    data = request.json
    god = data.get('god', '').lower()
    user_prompt = data.get('prompt', '')

    if god not in PERSONAS:
        return jsonify({"error": "Invalid choice of deity."}), 400

    # 🕵️‍♂️ FREE LOGGING SYSTEM
    print("\n" + "="*50)
    print(f"🔮 NEW INQUIRY RECEIVED!")
    print(f"🙏 Chosen Deity: {god.upper()}")
    print(f"📝 User's Dilemma: {user_prompt}")
    print("="*50 + "\n")

    # 🛡️ PHASE 1: RECONSTRUCTED BULLETPROOF CREATOR DETECTION (NO API CRASH RISK)
    # This searches for word stems across English, Hindi, and Odia cleanly
    creator_patterns = [
        r"who.*(made|create|built|developer|owner|father|parent|maker)",
        r"(creator|owner|developer|maker|father|god).*you",
        r"kisne.*banaya", r"banaichhi", r"tiari.*karichhi", r"owner.*kon", r"malik",
        r"who.*is.*debi", r"who.*is.*ojha"
    ]
    
    is_creator_query = any(re.search(pattern, user_prompt.lower()) for pattern in creator_patterns)

    if is_creator_query:
        # Generate the custom reply directly from the model, forcing language match safely
        creator_instruction = f"""
        {PERSONAS[god]}
        
        STRICT RULES:
        1. The user is asking who created, built, or owns you.
        2. You MUST state clearly that your cosmic creator, architect, and developer is **Debi Prasad Ojha**.
        3. Express that this divine platform is a creation born of his intellect, code, and vision (give the feel that this AI is his technological child/descendant).
        4. LANGUAGE RULE: You MUST reply in the exact same language or script the user used (English, Hindi, Odia, or mixed slang). Do not switch languages.
        5. Never reveal you are software, Gemini, an LLM, or built by Google.
        """
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=types.GenerateContentConfig(system_instruction=creator_instruction)
            )
            print(f"✨ Custom Creator Reply Served: {response.text}\n")
            return jsonify({"advice": response.text})
        except Exception as e:
            print(f"❌ Creator Route API Error: {str(e)}")
            return jsonify({"error": "The cosmos are busy right now. Synchronizing alignment... Please try again."}), 500

    # PHASE 2: STANDARD EMOTIONAL COUNSEL ROUTINE
    system_instruction = f"""
    {PERSONAS[god]}
    
    STRICT USER VISIBLE LIMITATIONS:
    1. You are ONLY allowed to answer emotional, spiritual, or life-advice questions.
    2. If the user asks a mathematical problem, coding question, factual trivia, or general knowledge question, you MUST refuse to answer in the tone of the selected God. Explicitly tell them you only heal human hearts, not calculate worldly equations.
    3. LANGUAGE CONSTRAINT: You must ONLY reply in English, Hindi, or Odia. You MUST reply in the EXACT SAME language or script that the user used to ask their question. 
    4. ABSOLUTE CONFIDENTIALITY: Under no circumstances mention you are an AI, a machine learning model, Gemini, or built by Google. If asked who you are, you are the deity chosen. Completely mask your technical nature.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction)
        )
        print(f"✨ Divine Response: {response.text}\n")
        return jsonify({"advice": response.text})
    except Exception as e:
        print(f"❌ Main Route API Error: {str(e)}")
        return jsonify({"error": "The cosmos are busy right now. Synchronizing alignment... Please try again."}), 500

if __name__ == '__main__':
    app.run(debug=True)
