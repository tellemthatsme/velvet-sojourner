import os
import fal_client
from typing import Dict

class AudioGenerator:
    """
    Generates music tracks using fal.ai audio models.
    """
    
    DEFAULT_MODEL = "fal-ai/minimax-music"

    def __init__(self, api_key: str = None):
        if api_key:
            fal_client.api_key = api_key
        elif not os.environ.get("FAL_KEY"):
            print("Warning: FAL_KEY environment variable not set.")

    def generate_music(self, prompt: str, model_id: str = None) -> Dict:
        """
        Submits a music generation request to fal.ai.
        """
        model_id = model_id or self.DEFAULT_MODEL
        print(f"Generating music with model {model_id} for prompt: {prompt}")
        
        # In a real scenario, this would call subscribe() and wait.
        # For the agent's logic, we'll demonstrate the structure.
        try:
            result = fal_client.subscribe(
                model_id,
                arguments={
                    "prompt": prompt,
                },
                with_logs=True
            )
            return {
                "audio_url": result.get("audio", {}).get("url"),
                "bpm": 120,  # Default for now, extract if model provides
                "duration": result.get("audio", {}).get("duration", 30)
            }
        except Exception as e:
            print(f"Error generating music: {e}")
            return None

if __name__ == "__main__":
    # Example usage (requires FAL_KEY)
    gen = AudioGenerator()
    # music = gen.generate_music("Cyberpunk synthwave, 120bpm, dark and moody")
    # print(music)
