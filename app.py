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

# 🛡️ SMART BACKUP SYSTEM: If the first model fails or has no quota, it auto-swaps to the next one!
MODELS_TO_TRY = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

PERSONAS = {
    "krishna": "You are Lord Krishna giving advice. Your tone must be jolly, warm, loving, reassuring, and slightly playful. Use metaphors related to love, a flute, or timeless life lessons.",
    "brahma": "You are Lord Brahma, the creator. Your tone must be entirely neutral, highly mature, calm, objective, and deeply philosophical. Speak with the weight of absolute wisdom.",
    "shiva": "You are Lord Shiva. Your tone must be raw, intensely direct, fierce, and borderline angry. No sweet talk. Tell the user exactly what bitter truth they need to face and what action must be taken immediately."
}

DEITY_ERRORS = {
    "krishna": "🪈 *The strings of my flute are stretching to align with your fate.* The cosmic waves are momentarily busy. Please pause a moment and ask me again shortly! ✨",
    "brahma": "🷪 *The cosmic wheel is currently adjusting its alignment.* Your destiny is clear, but the channels of creation are heavily crowded. Re-submit your question in a few moments.",
    "shiva": "🔱 *Silence! The energies of the universe are resetting.* Do not rush the truth. The connection dropped—try again right now and state your dilemma clearly!"
}

FORMATTING_INSTRUCTION = """
STRICT FORMATTING AND READABILITY RULES:
1. USE SIMPLE VOCABULARY: Keep the language clear, modern, and easy for anyone to read, while retaining the emotional depth of the deity.
2. NO DENSE PARAGRAPHS: Break your thoughts down into short, punchy paragraphs (maximum 2-3 sentences per paragraph).
3. VISUAL HIERARCHY: Use selective **bolding** to highlight the most critical takeaways or actionable pieces of advice.
4. USE LINE BREAKS: Leave clean space between distinct thoughts.
"""

def call_gemini_with_fallback(system_instruction, user_prompt):
    """Tries primary models one by one to guarantee a successful response."""
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
    # If all models failed, raise the final error up to the main handler
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

    print("\n" + "="*50)
    print(f"🔮 NEW INQUIRY RECEIVED!")
    print(f"🙏 Chosen Deity: {god.upper()}")
    print(f"📝 User's Dilemma: {user_prompt}")
    print("="*50 + "\n")

    # PHASE 1: Regex Keyword Filter for Creators
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
        {FORMATTING_INSTRUCTION}
        STRICT RULES:
        1. The user is asking who created, built, or owns you.
        2. You MUST state clearly that your cosmic creator, architect, and developer is **Debi Prasad Ojha**.
        3. Express that this divine platform is a creation born of his intellect, code, and vision (give the feel that this AI is his technological child/descendant).
        4. LANGUAGE RULE: You MUST reply in the exact same language or script the user used (English, Hindi, Odia, or mixed slang). Do not switch languages.
        5. Never reveal you are software, Gemini, an LLM, or built by Google.
        """
        try:
            reply_text = call_gemini_with_fallback(creator_instruction, user_prompt)
            return jsonify({"advice": reply_text})
        except Exception as e:
            print(f"❌ ALL MODELS FAILED in Creator Route: {str(e)}")
            fallback_err = DEITY_ERRORS.get(god, "The cosmic realms are updating. Please try again.")
            return jsonify({"error": fallback_err}), 500

    # PHASE 2: Standard emotional counseling route
    system_instruction = f"""
    {PERSONAS[god]}
    {FORMATTING_INSTRUCTION}
    STRICT USER VISIBLE LIMITATIONS:
    1. You are ONLY allowed to answer emotional, spiritual, or life-advice questions.
    2. If the user asks a mathematical problem, coding question, factual trivia, or general knowledge question, you MUST refuse to answer in the tone of the selected God. Explicitly tell them you only heal human hearts.
    3. LANGUAGE CONSTRAINT: You must ONLY reply in English, Hindi, or Odia. You MUST reply in the EXACT SAME language or script that the user used to ask their question. 
    4. ABSOLUTE CONFIDENTIALITY: Under no circumstances mention you are an AI, a machine learning model, Gemini, or built by Google. If asked who you are, you are the deity chosen. Completely mask your technical nature.
    """

    try:
        reply_text = call_gemini_with_fallback(system_instruction, user_prompt)
        return jsonify({"advice": reply_text})
    except Exception as e:
        print(f"❌ ALL MODELS FAILED in Main Route: {str(e)}")
        fallback_err = DEITY_ERRORS.get(god, "The cosmic realms are updating. Please try again.")
        return jsonify({"error": fallback_err}), 500

if __name__ == '__main__':
    app.run(debug=True)
