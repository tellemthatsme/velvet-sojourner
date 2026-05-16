import json
from typing import List, Dict

class Prompter:
    """
    Generates technical shot-lists for AI video models based on user concepts.
    Inspired by 'awesome-ai-video-prompts' methodologies.
    """
    
    STYLE_TEMPLATES = {
        "cyberpunk": {
            "vibe": "neon-lit, futuristic, rainy city, high contrast, cinematic lighting",
            "technical": "8k resolution, photorealistic, Ray-tracing, volumetric fog, Unreal Engine 5 render style",
            "camera": "low angle, tracking shot, dynamic motion blur"
        },
        "cinematic_drift": {
            "vibe": "high-speed racing, smoke, tire marks, sunset, gritty",
            "technical": "anamorphic lens, shutter speed 1/48, highly detailed textures, masterwork physics simulation",
            "camera": "drone follow shot, close-up on wheels, wide pan of the track"
        },
        "abstract_glow": {
            "vibe": "ethereal, fluid motion, glowing particles, dreamscape",
            "technical": "soft focus, bokeh, 120fps slow motion, bioluminescent colors",
            "camera": "static, slow zoom, macro lens"
        }
    }

    def __init__(self, style: str = "cyberpunk"):
        self.style = style if style in self.STYLE_TEMPLATES else "cyberpunk"
        self.template = self.STYLE_TEMPLATES[self.style]

    def generate_shot_list(self, concept: str, num_shots: int = 5) -> List[Dict]:
        """
        Generates a list of shot descriptions and technical prompts.
        """
        shots = []
        for i in range(num_shots):
            shot_prompt = (
                f"Shot {i+1}: {concept}. {self.template['vibe']}. "
                f"{self.template['technical']}. Camera: {self.template['camera']}. "
                f"Temporal consistency, high-fidelity motion."
            )
            shots.append({
                "shot_id": i + 1,
                "description": f"Generating shot {i+1} for {concept} in {self.style} style.",
                "prompt": shot_prompt,
                "duration_sec": 5  # Standard clip length
            })
        return shots

    def save_shot_list(self, shots: List[Dict], filepath: str):
        with open(filepath, 'w') as f:
            json.dump(shots, f, indent=4)
        print(f"Shot list saved to {filepath}")

if __name__ == "__main__":
    prompter = Prompter(style="cinematic_drift")
    shots = prompter.generate_shot_list("A neon blue Nissan GT-R drifting through a rainy Tokyo intersection")
    print(json.dumps(shots, indent=4))
