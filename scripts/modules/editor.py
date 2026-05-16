import os
from typing import List, Dict
from videodb import connect
from videodb.editor import Timeline, Track, Clip, VideoAsset, AudioAsset

class VideoEditor:
    """
    Stitches video clips and audio together using the VideoDB SDK.
    """
    
    def __init__(self, api_key: str = None):
        api_key = api_key or os.environ.get("VIDEO_DB_API_KEY")
        if not api_key:
            print("Warning: VIDEO_DB_API_KEY environment variable not set.")
            self.conn = None
        else:
            self.conn = connect(api_key=api_key)
            self.coll = self.conn.get_collection()

    def upload_assets(self, video_urls: List[str], audio_url: str) -> Dict:
        """
        Uploads remote URLs to VideoDB and returns their asset IDs.
        """
        if not self.conn:
            return None
            
        print("Uploading assets to VideoDB...")
        video_ids = []
        for url in video_urls:
            video = self.coll.upload(url=url)
            video_ids.append(video.id)
            
        audio = self.coll.upload(url=audio_url)
        return {
            "video_ids": video_ids,
            "audio_id": audio.id
        }

    def create_music_video(self, video_ids: List[str], audio_id: str, duration_per_clip: int = 5) -> str:
        """
        Stitches clips and overlays audio.
        """
        if not self.conn:
            return "Error: VideoDB connection not established."

        print("Creating timeline and stitching clips...")
        timeline = Timeline(self.conn)
        
        # Video Track
        video_track = Track()
        for v_id in video_ids:
            video_asset = VideoAsset(id=v_id)
            video_track.add_clip(Clip(asset=video_asset, duration=duration_per_clip))
        
        # Audio Track
        audio_track = Track()
        audio_asset = AudioAsset(id=audio_id)
        total_duration = len(video_ids) * duration_per_clip
        audio_track.add_clip(Clip(asset=audio_asset, duration=total_duration))
        
        timeline.add_track(video_track)
        timeline.add_track(audio_track)
        
        # Generate final stream link
        stream_url = timeline.generate_stream()
        print(f"Music video generated: {stream_url}")
        return stream_url

if __name__ == "__main__":
    # Example usage (requires VIDEO_DB_API_KEY)
    editor = VideoEditor()
    # stream = editor.create_music_video(["vid1", "vid2"], "aud1")
    # print(stream)
