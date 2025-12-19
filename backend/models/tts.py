import requests
import os
from dotenv import load_dotenv

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY").strip()
model = "eleven_multilingual_v2"


def text_to_speech(text, voice_id="EXAVITQu4vr4xnSDxMaL"): 
    """Generates speech using ElevenLabs and returns audio bytes."""
    if not ELEVENLABS_API_KEY:
        print("ElevenLabs API key not set.")
        return None 

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": model, 
        "voice_settings": {
            "stability": 0.75,      
            "similarity_boost": 0.75 
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True) # Use stream=True for potentially large audio
        response.raise_for_status() 
        return response.content 
        # ---

    except requests.exceptions.RequestException as e:
        try:
             error_details = response.json()
             print("Error details:", error_details)
        except:
             print("Response content:", response.text)
        return None 
    
   
    
# audio = text_to_speech("aapka naam kya hai")

# if audio:
#     output_path = "farmer_response.mp3"
#     with open(output_path, "wb") as f:
#         f.write(audio)
#     print("✅ Speech saved to:", output_path)