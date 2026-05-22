# Promo Video Scripts — Recording Instructions

This directory contains 60-second promo/demo video scripts for three products. Use this guide to record professional-quality screen recordings with voiceover.

---

## Recommended Tools

| Tool | Platform | Best For | Cost |
|------|----------|----------|------|
| **OBS Studio** | Windows / macOS / Linux | Screen recording + webcam + audio | Free |
| **ScreenFlow** | macOS | Polished screencasts with editing | $149 (one-time) |
| **DaVinci Resolve** | Windows / macOS / Linux | Full video editing + color grading | Free (Studio $295) |
| **Final Cut Pro** | macOS | Professional editing | $299 (one-time) |
| **Audacity** | Windows / macOS / Linux | Voiceover recording + audio cleanup | Free |

**Recommended workflow:** Record screen capture in OBS Studio, record voiceover in Audacity, edit and composite in DaVinci Resolve or ScreenFlow.

---

## Video Settings

| Setting | Value |
|---------|-------|
| **Resolution** | 1920 x 1080 (1080p) |
| **Frame Rate** | 30 fps (smooth for screencasts) |
| **Bitrate** | 15-20 Mbps (CBR or VBR) |
| **Codec** | H.264 (widest compatibility) or H.265 (smaller files) |
| **Format** | MP4 (.mp4) |

### OBS Studio Quick Setup
1. Set canvas resolution: 1920x1080
2. Add "Display Capture" or "Window Capture" source
3. Set output: Settings → Output → Recording → Advanced → H.264, 20 Mbps
4. Record a test clip — confirm smooth 30fps before recording final takes

---

## Audio Tips

### Recording
- **Microphone:** Use a USB condenser mic (Blue Yeti, Rode NT-USB) or a lavalier
- **Environment:** Record in a quiet room with soft furnishings (reduces echo)
- **Distance:** 6-12 inches from mic, off-axis to avoid plosives
- **Levels:** Aim for -12dB to -6dB peak in Audacity/OBS
- **Pop filter:** Essential — prevents harsh "p" and "b" sounds

### Voiceover Style
- **Pace:** Conversational but slightly faster than natural speech (60s is tight)
- **Energy:** Enthusiastic but not salesy. Sound like a helpful expert
- **Pauses:** Brief pauses between scenes (0.5-1s) for breath and editing
- **Practice:** Read each script aloud 2-3 times before recording

### Post-Processing (Audacity)
1. Noise Reduction: Select noise floor → Effect → Noise Reduction → Apply
2. Compressor: Effect → Compressor (Ratio 3:1, Threshold -18dB)
3. Equalizer: Mild high-pass filter (80Hz) to remove rumble
4. Normalize: Effect → Normalize (-1dB peak)
5. Export as WAV or 320kbps MP3

---

## Screen Recording Tips

### Pre-Recording Checklist
- [ ] Close unnecessary apps and notifications
- [ ] Set browser zoom to 100% (not 125% or 150%)
- [ ] Use a clean desktop wallpaper
- [ ] Disable macOS Dock magnification / Windows taskbar auto-hide
- [ ] Increase cursor size (macOS: System Prefs → Accessibility → Display → Cursor Size; Windows: Settings → Ease of Access → Cursor size)
- [ ] Set text editor / IDE to a clean theme (light theme often reads better for demos)

### During Recording
- **Slow down:** Move cursor deliberately. Fast movements look chaotic on video
- **Zoom on key areas:** Before clicking something important, pause 0.5s
- **No typing in real-time:** Pre-type text, then show the result. Or add typing sounds in post
- **Smooth scrolls:** Use middle-click auto-scroll instead of jerky wheel scrolling
- **Stay in bounds:** Keep all action within a 16:9 frame (don't go off-screen)

---

## Editing Timeline Structure

Each 60s script is structured as 5 scenes. Build your timeline like this:

| Scene | Duration | Visual | Audio |
|-------|----------|--------|-------|
| 1 — Hook | 0:00-0:10 | Engaging opener, logo reveal | Hook line + music start |
| 2 — Problem | 0:10-0:20 | Pain point demonstration | Problem statement |
| 3 — Solution | 0:20-0:40 | Product walkthrough | Solution narrative |
| 4 — Features | 0:40-0:55 | Feature montage | Feature highlights |
| 5 — CTA | 0:55-1:00 | Logo + URL + download buttons | Final call to action |

### Music
- Background music: low volume (-20dB to -25dB relative to voice)
- Royalty-free sources: Epidemic Sound, Artlist, Uppbeat (free tier), Pixabay Music
- Genre: Upbeat electronic for tools, thoughtful ambient for knowledge products
- Fade in at start, fade out at end, dip slightly during voiceover (-3dB)

---

## Export Settings (Final Delivery)

| Use Case | Format | Resolution | Bitrate |
|----------|--------|------------|---------|
| Website / Landing Page | MP4 (H.264) | 1080p | 15 Mbps |
| Social Media (Twitter/X) | MP4 (H.264) | 1080p, square 1:1 | 10 Mbps |
| Social Media (LinkedIn) | MP4 (H.264) | 1080p, 16:9 | 15 Mbps |
| YouTube | MP4 (H.264) | 1080p | 20 Mbps |

---

## File Structure

```
promo-video-scripts/
├── README.md                        ← This file
├── agentforge-index-script.md       → Product 1: AgentForge Index
├── github-downloader-script.md      → Product 2: GitHub Downloader
└── chatgpt-export-script.md         → Product 3: ChatGPT Export System
```
