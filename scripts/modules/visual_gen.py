import os
import fal_client
from typing import List, Dict

class VisualGenerator:
    """
    Generates video clips using fal.ai video models.
    """
    
    DEFAULT_MODEL = "fal-ai/wan-t2v"

    def __init__(self, api_key: str = None):
        if api_key:
            fal_client.api_key = api_key
        elif not os.environ.get("FAL_KEY"):
            print("Warning: FAL_KEY environment variable not set.")

    def generate_video_shot(self, shot_data: Dict) -> Dict:
        """
        Submits a single shot generation to fal.ai.
        """
        print(f"Generating video for shot {shot_data.get('shot_id')}...")
        prompt = shot_data.get("prompt")
        
        try:
            result = fal_client.subscribe(
                self.DEFAULT_MODEL,
                arguments={
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                    "resolution": "720p",
                    "num_inference_steps": 30
                },
                with_logs=True
            )
            return {
                "shot_id": shot_data.get("shot_id"),
                "video_url": result.get("video", {}).get("url"),
                "duration": 5
            }
        except Exception as e:
            print(f"Error generating video for shot {shot_data.get('shot_id')}: {e}")
            return None

    def generate_batch_shots(self, shot_list: List[Dict]) -> List[Dict]:
        """
        Generates clips for all shots in the shot list.
        """
        results = []
        for shot in shot_list:
            res = self.generate_video_shot(shot)
            if res:
                results.append(res)
        return results

if __name__ == "__main__":
    # Example usage (requires FAL_KEY)
    vis_gen = VisualGenerator()
    # shots = [{"shot_id": 1, "prompt": "A stylish woman walks down a Tokyo street..."}]
    # videos = vis_gen.generate_batch_shots(shots)
    # print(videos)
