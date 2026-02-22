"""
Text-to-Speech Service
"""
import os
import tempfile
import base64
from gtts import gTTS
from typing import Optional

def generate_speech(text: str, language: str = 'en', slow: bool = False) -> Optional[str]:
    """
    Generate speech from text and return the audio as base64 string
    
    Args:
        text: Text to convert to speech
        language: Language code (default: 'en')
        slow: Whether to speak slowly (default: False)
        
    Returns:
        Base64 encoded MP3 audio or None if there was an error
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file_path = temp_file.name
        
        # Generate speech
        tts = gTTS(text=text, lang=language, slow=slow)
        tts.save(temp_file_path)
        
        # Read the file and encode to base64
        with open(temp_file_path, 'rb') as f:
            audio_data = f.read()
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Return base64 encoded audio
        return base64.b64encode(audio_data).decode('utf-8')
        
    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        return None