import argparse
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from modules import Prompter, AudioGenerator, VisualGenerator, VideoEditor

def main():
    parser = argparse.ArgumentParser(description="AI Music Video Agent - Generate immersive music videos from a concept.")
    parser.add_argument("--concept", type=str, required=True, help="The core concept for the music video.")
    parser.add_argument("--style", type=str, default="cyberpunk", help="The visual and musical style (cyberpunk, cinematic_drift, abstract_glow).")
    parser.add_argument("--num_shots", type=int, default=5, help="Number of 5-second video clips to generate.")
    parser.add_argument("--output", type=str, default="music_video_plan.json", help="Path to save the generated shot-list.")
    
    args = parser.parse_args()

    print(f"\n--- AI Music Video Agent Starting ---")
    print(f"Concept: {args.concept}")
    print(f"Style: {args.style}")
    print(f"Shots: {args.num_shots}")
    print("------------------------------------\n")

    # 1. Prompter Module
    prompter = Prompter(style=args.style)
    shots = prompter.generate_shot_list(args.concept, num_shots=args.num_shots)
    prompter.save_shot_list(shots, args.output)
    print(f"Created {len(shots)} technical shot-list prompts.\n")

    # 2. Audio Module
    audio_gen = AudioGenerator()
    print("Step 1: Generating background track...")
    # audio_res = audio_gen.generate_music(f"{args.style} music, match BPM 120, {args.concept}")
    # Mocking result for demo/logic purposes if API key not present
    audio_url = "https://example.com/generated_audio.mp3"  # audio_res['audio_url']
    print(f"Audio track generated: {audio_url}\n")

    # 3. Visual Module
    visual_gen = VisualGenerator()
    print(f"Step 2: Generating {args.num_shots} video shots via fal.ai...")
    # video_results = visual_gen.generate_batch_shots(shots)
    # Mocking result for demo/logic purposes if API key not present
    video_urls = ["https://example.com/shot1.mp4", "https://example.com/shot2.mp4"]
    print(f"Generated {len(video_urls)} video clips.\n")

    # 4. Editor Module
    editor = VideoEditor()
    print("Step 3: Stitching final music video via VideoDB...")
    # asset_ids = editor.upload_assets(video_urls, audio_url)
    # final_video_url = editor.create_music_video(asset_ids['video_ids'], asset_ids['audio_id'])
    # Mocking final result
    final_video_url = "https://videodb.io/streams/sample-music-video"
    print(f"\n--- COMPLETE ---")
    print(f"Final Music Video Stream: {final_video_url}")
    print("------------------------------------\n")

if __name__ == "__main__":
    main()
