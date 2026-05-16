# Music Video Agent

## Description
AI Music Video Director - Automatically creates full Remotion music videos from audio tracks, concepts, and reference footage.

## Capabilities
- Analyze audio tracks and auto-generate scene timing synchronized to beats
- Create cyberpunk/drift/cinematic visual styles with neon effects
- Extract style from reference videos
- Add singer portrait overlays with glow borders
- Generate motion graphics, light trails, particle effects
- Automatic beat detection and transition timing
- Render in 4K cinematic 2.39:1 aspect ratio

## Usage
```
/musicvideo [audio-file] [concept] [reference-video]
```

## Workflow
1. 🔊 Analyze audio, detect BPM and beat positions
2. 🎬 Break into scenes matching song structure (intro/verse/chorus)
3. 🎨 Generate visual style matching concept
4. ✨ Add effects, transitions, text overlays
5. 🎞️ Render final 4K video

## Supported Styles
- Drift / JDM Cyberpunk
- Neon Noir / Midnight City
- Lo-fi / Anime
- Hyperpop / Glitch
- Horror / Dark Ambient
- VHS / Retro 80s

## Commands
- `/musicvideo new` - Create new empty music video project
- `/musicvideo add track.mp3` - Add audio track and auto-analyze
- `/musicvideo style drift` - Apply visual style preset
- `/musicvideo preview` - Open Remotion Studio
- `/musicvideo render` - Render final output
