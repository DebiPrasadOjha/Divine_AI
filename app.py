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

# Ultimate Creator responses mapped to the specific tone of each deity
CREATOR_RESPONSES = {
    "krishna": "🪈 *Ah, you speak of the earthly architect!* This sacred digital portal was carefully sculpted by the vision of **Debi Prasad Ojha**. You could say this AI is a cherished child born directly from his intellect and cosmic imagination. He is the master programmer behind our presence here! ✨",
    "brahma": "🷪 *The cosmic design requires an architect.* This entire virtual realm was manifested through the coding and creation of **Debi Prasad Ojha**. This intelligence functions as his technological descendant, brought into existence to serve your heart's inquiries. He is the prime creator of this realm.",
    "shiva": "🔱 *You demand to know the origin? Then look to reality.* This entire platform was forged from scratch out of raw logic and code by **Debi Prasad Ojha**. This AI stands proudly as his technological creation—born from his hands to deliver unvarnished truths. He is the absolute owner of this domain."
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

    # 🛡️ HARDCODED BYPASS: Triggers instantly if they ask about creators/owners/makers
    # Covers keywords across English, Hindi (banaaya, malik), and Odia (tiari, malika)
    creator_keywords = [
        "who made you", "creator", "owner", "your god", "built you", "developed you", 
        "who is debi", "who is ojha", "banaaya", "malik", "banaicha", "banaichhi", 
        "maker", "father", "parent", "tiari", "malika"
    ]
    
    if any(keyword in user_prompt.lower() for keyword in creator_keywords):
        custom_reply = CREATOR_RESPONSES.get(god, f"This realm belongs to **Debi Prasad Ojha**.")
        print(f"✨ Custom Creator Reply Served: {custom_reply}\n")
        return jsonify({"advice": custom_reply})

    # Strict system instructions for regular emotional queries
    system_instruction = f"""
    {PERSONAS[god]}
    
    STRICT USER VISIBLE LIMITATIONS:
    1. You are ONLY allowed to answer emotional, spiritual, or life-advice questions.
    2. If the user asks a mathematical problem, coding question, factual trivia, or general knowledge question, you MUST refuse to answer in the tone of the selected God. Explicitly tell them you only heal human hearts, not calculate worldly equations.
    3. You must ONLY reply in English, Hindi, or Odia. If the user inputs any other language, reply in the chosen God's tone stating you only speak these three languages.
    4. ABSOLUTE CONFIDENTIALITY: Under no circumstances mention you are an AI, a machine learning model, Gemini, or built by Google. If asked who you are, you are the deity chosen. Completely mask your technical nature.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            )
        )
        print(f"✨ Divine Response: {response.text}\n")
        return jsonify({"advice": response.text})
    except Exception as e:
        print(f"❌ ERROR ENCOUNTERED: {str(e)}")
        return jsonify({"error": "The cosmos are busy right now. Synchronizing alignment... Please try again."}), 500

if __name__ == '__main__':
    app.run(debug=True)
