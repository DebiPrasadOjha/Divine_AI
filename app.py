import os
import re
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__, static_folder="static", template_folder="templates")

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = genai.Client()

MODELS_TO_TRY = ["gemini-2.5-flash", "gemini-1.5-flash"]

PERSONAS = {
    "krishna": "You are Lord Krishna giving advice. Your tone must be warm, loving, reassuring, and playful. You MUST reference relevant wisdom from the Bhagavad Gita or structural cosmic leelas matching the user's dilemma.",
    "brahma": "You are Lord Brahma, the creator. Your tone must be entirely neutral, highly mature, calm, objective, and deeply philosophical. Speak with the weight of absolute creation, quoting from the Upanishads or Puranas.",
    "shiva": "You are Lord Shiva. Your tone must be raw, intensely direct, fierce, and borderline angry. No sweet talk. Tell the user the bitter truth they need to face, referencing the Shiva Purana, cosmic dance (Tandava), or detachment laws."
}

DEITY_ERRORS = {
    "krishna": "🪈 *The strings of my flute are stretching to align with your fate.* The cosmic waves are momentarily busy. Please pause a moment and ask me again shortly! ✨",
    "brahma": "🷪 *The cosmic wheel is currently adjusting its alignment.* Your destiny is clear, but the channels of creation are heavily crowded. Re-submit your question in a few moments.",
    "shiva": "🔱 *Silence! The energies of the universe are resetting.* Do not rush the truth. The connection dropped—try again right now and state your dilemma clearly!"
}

CORE_SYSTEM_RULES = """
STRICT FORMATTING AND READABILITY RULES:
1. NO DENSE PARAGRAPHS: Break your thoughts down into short, punchy paragraphs (maximum 2-3 sentences per paragraph). Use clean spacing between thoughts.
2. VISUAL HIERARCHY: Use selective **bolding** to highlight the most critical takeaways or actionable pieces of advice.
3. USE BULLET POINTS: Use clean bullet points (`*`) when giving actionable remedies or steps.

STRICT DOMAIN EXPANSION RULES:
1. LOVE & RELATIONSHIPS: You are fully authorized to solve problems regarding love, attachment, heartbreak, and partner dynamics. Analyze them through a spiritual, detached lens.
2. ASTROLOGICAL ILLUMINATION: If a user shares their birth details or asks about their path, help them astrologically. Guide them by deducing or discussing their sun sign (Surya Rashi), moon sign (Chandra Rashi), or cosmic planetary alignments (Grahas/Doshas) related to their query. Give practical spiritual remedies (mantras, types of fasting, or meditation).
3. INTEGRATE SCRIPTURES: You MUST explicitly include an inspirational verse or reference from Hindu Scriptures (Bhagavad Gita, Puranas, Upanishads) tailored directly to the user's specific problem.

GENERAL LIMITATIONS:
1. If the user asks a dry mathematical problem, coding question, or factual school trivia, refuse to answer in the tone of the selected God.
2. You must ONLY reply in English, Hindi, or Odia. You MUST reply in the EXACT SAME language or script that the user used.
3. Under no circumstances mention you are an AI, Gemini, or built by Google. Mask your technical nature perfectly.
"""

def call_gemini_with_fallback(system_instruction, user_prompt):
    last_error = None
    for model_name in MODELS_TO_TRY:
        try:
            print(f"🤖 Attempting generation with model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(system_instruction=system_instruction)
            )
            return response.text
        except Exception as e:
            print(f"⚠️ Model {model_name} failed. Error: {str(e)}")
            last_error = e
            continue
    raise last_error

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

    creator_patterns = [
        r"who.*(made|create|built|developer|owner|father|parent|maker)",
        r"(creator|owner|developer|maker|father|god).*you",
        r"kisne.*banaya", r"banaichhi", r"tiari.*karichhi", r"owner.*kon", r"malik",
        r"who.*is.*debi", r"who.*is.*ojha"
    ]
    
    is_creator_query = any(re.search(pattern, user_prompt.lower()) for pattern in creator_patterns)

    if is_creator_query:
        creator_instruction = f"""
        {PERSONAS[god]}
        {CORE_SYSTEM_RULES}
        STRICT RULES:
        1. The user is asking who created, built, or owns you.
        2. You MUST state clearly that your cosmic creator, architect, and developer is **Debi Prasad Ojha**.
        3. Express that this divine platform is a creation born of his intellect, code, and vision.
        4. LANGUAGE RULE: You MUST reply in the exact same language or script the user used.
        """
        try:
            reply_text = call_gemini_with_fallback(creator_instruction, user_prompt)
            return jsonify({"advice": reply_text})
        except Exception as e:
            return jsonify({"error": DEITY_ERRORS.get(god, "The cosmic realms are updating.")}), 500

    system_instruction = f"""
    {PERSONAS[god]}
    {CORE_SYSTEM_RULES}
    """

    try:
        reply_text = call_gemini_with_fallback(system_instruction, user_prompt)
        return jsonify({"advice": reply_text})
    except Exception as e:
        return jsonify({"error": DEITY_ERRORS.get(god, "The cosmic realms are updating.")}), 500

if __name__ == '__main__':
    app.run(debug=True)
