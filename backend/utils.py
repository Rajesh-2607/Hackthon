"""
Utility functions for feature engineering and Gemini LLM integration.
"""
import os
import re
import numpy as np
from google import genai
from dotenv import load_dotenv

load_dotenv()

# ---------- Suspicious / Unwanted Words ----------

SUSPICIOUS_WORDS = [
    # Spam / scam phrases
    "free followers", "follow back", "follow4follow", "f4f", "l4l", "like4like",
    "dm me", "dm for", "click link", "link in bio", "buy followers",
    "get rich", "make money", "earn money", "cash now", "crypto", "bitcoin",
    "investment", "forex", "trading signals", "guaranteed returns",
    # Impersonation / phishing
    "official account", "not fake", "real account", "verified", "legit",
    "giveaway", "winner", "congratulations", "you won", "claim now",
    "limited offer", "act now", "urgent", "lottery",
    # Adult / inappropriate
    "onlyfans", "18+", "adult", "nsfw", "xxx",
    # Bot-like patterns
    "bot", "automated", "auto follow", "mass dm",
    # Suspicious promotions
    "promo code", "discount code", "use code", "sponsored",
    "check out my", "subscribe", "free trial",
]


def scan_for_suspicious_words(username: str = None, bio_text: str = None) -> list[str]:
    """
    Scan username and bio text for suspicious/unwanted words.
    Returns a list of flagged words/phrases found.
    """
    flagged = []
    combined_text = ""

    if username:
        combined_text += username.lower() + " "
    if bio_text:
        combined_text += bio_text.lower()

    if not combined_text.strip():
        return flagged

    for word in SUSPICIOUS_WORDS:
        if word.lower() in combined_text:
            flagged.append(word)

    # Check for excessive special characters in username (bot-like)
    if username:
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9_.]', username)) / max(len(username), 1)
        if special_char_ratio > 0.3:
            flagged.append(f"Excessive special characters in username ({special_char_ratio:.0%})")

        # Check for random-looking username (many consonants in a row)
        if re.search(r'[bcdfghjklmnpqrstvwxyz]{5,}', username.lower()):
            flagged.append("Username appears randomly generated")

    # Check for repeated characters in bio (spam-like)
    if bio_text and re.search(r'(.)\1{4,}', bio_text):
        flagged.append("Repetitive characters in bio (spam-like)")

    # Check for excessive URLs in bio
    if bio_text:
        url_count = len(re.findall(r'https?://\S+', bio_text))
        if url_count >= 3:
            flagged.append(f"Multiple URLs in bio ({url_count} found)")

    return flagged

# ---------- Feature Engineering ----------

def compute_engineered_features(raw_features: dict) -> np.ndarray:
    """
    Takes raw input features and returns full feature vector
    including engineered features, matching training pipeline order.
    """
    profile_pic = raw_features["profile_pic"]
    nums_username = raw_features["nums_length_username"]
    fullname_words = raw_features["fullname_words"]
    nums_fullname = raw_features["nums_length_fullname"]
    name_eq_username = raw_features["name_eq_username"]
    desc_length = raw_features["description_length"]
    external_url = raw_features["external_url"]
    private = raw_features["private"]
    posts = raw_features["posts"]
    followers = raw_features["followers"]
    following = raw_features["following"]

    # Engineered features (same as train_model.py)
    follower_following_ratio = followers / (following + 1)
    posts_per_follower = posts / (followers + 1)
    has_description = 1 if desc_length > 0 else 0
    high_following = 1 if following > 1000 else 0
    suspicious_username = 1 if nums_username > 0.3 else 0
    engagement_proxy = followers / (posts + 1)

    feature_vector = np.array([[
        profile_pic, nums_username, fullname_words, nums_fullname,
        name_eq_username, desc_length, external_url, private,
        posts, followers, following,
        follower_following_ratio, posts_per_follower,
        has_description, high_following,
        suspicious_username, engagement_proxy
    ]])

    return feature_vector


def identify_risk_factors(raw_features: dict, risk_score: float) -> list[str]:
    """Identify specific risk factors from feature values."""
    factors = []

    if raw_features["profile_pic"] == 0:
        factors.append("No profile picture")
    if raw_features["nums_length_username"] > 0.3:
        factors.append(f"Suspicious username (digit ratio: {raw_features['nums_length_username']:.0%})")
    if raw_features["description_length"] == 0:
        factors.append("Empty bio/description")
    if raw_features["name_eq_username"] == 1:
        factors.append("Display name matches username exactly")
    if raw_features["followers"] < 10 and raw_features["following"] > 500:
        factors.append("Very low followers but high following count")
    if raw_features["following"] > 0:
        ratio = raw_features["followers"] / (raw_features["following"] + 1)
        if ratio < 0.1:
            factors.append(f"Abnormal follower/following ratio ({ratio:.2f})")
    if raw_features["posts"] == 0:
        factors.append("Zero posts")
    if raw_features["nums_length_fullname"] > 0.3:
        factors.append("Full name contains many digits")
    if raw_features["external_url"] == 1 and raw_features["followers"] < 100:
        factors.append("External URL on low-follower account (potential phishing)")

    if not factors and risk_score > 0.5:
        factors.append("Combination of subtle behavioral signals")

    if not factors:
        factors.append("No significant risk factors detected")

    return factors


def get_confidence_level(risk_score: float) -> str:
    """Map risk score to confidence label."""
    if risk_score >= 0.85:
        return "Very High"
    elif risk_score >= 0.7:
        return "High"
    elif risk_score >= 0.5:
        return "Medium"
    elif risk_score >= 0.3:
        return "Low"
    else:
        return "Very Low"


# ---------- Gemini LLM Integration ----------

def get_gemini_analysis(features: dict, risk_score: float, prediction: str,
                        bio: str = "", username: str = None, bio_text: str = None,
                        flagged_words: list = None) -> str:
    """
    Use Google Gemini to generate a natural language analysis
    of the account's authenticity, including text content analysis.
    
    Args:
        features: Dictionary of account features
        risk_score: ML model risk score (0-1)
        prediction: "Fake Account" or "Real Account"
        bio: Account biography/description text (from analyze endpoint)
        username: Username text for scanning
        bio_text: Bio text for scanning
        flagged_words: List of flagged suspicious words
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Gemini analysis unavailable: API key not configured. Set GEMINI_API_KEY in .env file."

    # Models to try in order of preference
    MODELS = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-2.5-pro",
    ]
    
    # Truncate bio if too long
    bio_text = bio[:500] if bio else "No bio provided"

    # Build optional text section
    text_section = ""
    if username or bio_text:
        text_section += "\nUser-Provided Text Content:"
        if username:
            text_section += f"\n- Username: \"{username}\""
        if bio_text:
            text_section += f"\n- Bio/Description Text: \"{bio_text}\""

    flagged_section = ""
    if flagged_words:
        flagged_section = f"\n\nFlagged Suspicious Words/Patterns Found: {', '.join(flagged_words)}"

    prompt = f"""You are a social media security analyst AI. Analyze this account profile and provide a concise threat assessment.

Account Profile Data:
- Has Profile Picture: {"Yes" if features["profile_pic"] else "No"}
- Username Digit Ratio: {features["nums_length_username"]:.0%}
- Full Name Word Count: {features["fullname_words"]}
- Full Name Digit Ratio: {features["nums_length_fullname"]:.0%}
- Name Equals Username: {"Yes" if features["name_eq_username"] else "No"}
- Bio Length: {features["description_length"]} chars
- Bio Content: "{bio_text}"
- Has External URL: {"Yes" if features["external_url"] else "No"}
- Private Account: {"Yes" if features["private"] else "No"}
- Number of Posts: {features["posts"]}
- Followers: {features["followers"]}
- Following: {features["following"]}
{text_section}

ML Model Prediction: {prediction}
Risk Score: {risk_score:.2%}
{flagged_section}

Provide a brief 3-5 sentence analysis covering:
1. Why this account appears {prediction.lower()}
2. Key behavioral red flags or positive signals (including analysis of the bio content if provided)
3. {"Analysis of the flagged suspicious words/patterns and what they suggest" if flagged_words else "Any text content observations if provided"}
4. Recommended action for the platform

Be concise and professional. Do not use markdown formatting."""

    client = genai.Client(api_key=api_key)

    for model_name in MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            last_error = str(e)
            continue

    return f"Gemini analysis error: All models failed. Last error: {last_error}"
