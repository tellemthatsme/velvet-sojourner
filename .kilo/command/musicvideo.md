# /musicvideo

Create full AI-generated music videos using Remotion.

## Usage
```
/musicvideo <audio-file> [concept] [reference-video]
```

## Examples
```
/musicvideo my-song.mp3 "drift cars neon cyberpunk" reference-video.mp4
/musicvideo track.mp3 "lofi anime rain"
/musicvideo preview
/musicvideo render
```

## Options
- `--style <name>` - Apply style preset: drift, cyberpunk, lofi, retro, horror
- `--ratio 2.39:1` - Aspect ratio: 16:9, 2.39:1, 9:16 vertical
- `--fps 24` - Frame rate: 24, 30, 60
- `--resolution 4k` - Output resolution: 1080p, 4k, 8k

## Workflow
1. Automatically analyzes audio BPM and beat positions
2. Generates scene timing synchronized to song structure
3. Applies visual effects matching your concept
4. Opens Remotion Studio for preview
5. Renders final high quality video
