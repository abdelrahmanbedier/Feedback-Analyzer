import os
import google.generativeai as genai
import json
import pycountry

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def get_language_code(language_name: str) -> str:
    """Converts a language name to a two-letter ISO code or 'un' for unknown."""
    if not language_name or language_name.lower() in ['unknown', 'undetermined']:
        return 'un'
    try:
        return pycountry.languages.lookup(language_name).alpha_2
    except (LookupError, AttributeError):
        return 'un'

def analyze_feedback(text: str):
    """Sends feedback to Gemini for analysis."""
    # --- NEW, SMARTER PROMPT ---
    prompt = f"""
    Analyze the following customer feedback text. Provide the analysis in a strict JSON format with four keys:
    1. 'is_translatable': a boolean (true or false) indicating if the text is meaningful and translatable.
    2. 'language': the detected language (e.g., "French"). If is_translatable is false, this should be "unknown".
    3. 'translated_text': the English translation. If is_translatable is false, this should be "Cannot be translated".
    4. 'sentiment': either "positive", "negative", or "neutral". If is_translatable is false, this should be "unknown".

    Text: "{text}"
    """
    try:
        response = model.generate_content(prompt)
        json_response_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        analysis_result = json.loads(json_response_text)

        # --- NEW, MORE RELIABLE CHECK ---
        if not analysis_result.get("is_translatable", False):
            # If Gemini says it's not translatable, we mark it for review
            analysis_result["language"] = "review"
            analysis_result["translated_text"] = "Cannot be translated"
            analysis_result["sentiment"] = "unknown"
        else:
            # If it is translatable, process the language as normal
            lang_name = analysis_result.get("language", "unknown")
            analysis_result["language"] = get_language_code(lang_name)

        return analysis_result
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        # Errors from the API should also be marked for review
        return {
            "language": "review",
            "translated_text": "Cannot be translated",
            "sentiment": "unknown"
        }