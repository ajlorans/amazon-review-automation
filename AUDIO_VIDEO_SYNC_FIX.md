# Audio-Video Sync Fix

## Problem
Some YouTube and Instagram videos had audio-video sync issues where:
- Audio played correctly
- Video was delayed/lagging behind audio
- Issue was consistent (not getting worse over time)
- Only affected some videos, not all

## Root Cause
Phone videos often record in **Variable Frame Rate (VFR)**, where the frame rate changes during recording. When these videos are converted to Constant Frame Rate (CFR) at export time, it can cause:
- Frames being duplicated or dropped inconsistently
- Audio timing not matching video timing
- Sync drift between audio and video tracks

Additionally, the code was **forcing all videos to 30fps** during export, which:
- Caused unnecessary frame rate conversion
- Could introduce sync issues if the original was a different frame rate
- Didn't preserve the original video's natural frame rate

## Solution
Implemented proper VFR → CFR conversion and frame rate preservation:

### 1. Early VFR Detection and Conversion
- **Detects** Variable Frame Rate videos during normalization
- **Converts** VFR to CFR (Constant Frame Rate) **before** other processing
- **Preserves** the original frame rate (or rounds to nearest common FPS)
- **Maintains** audio sync during conversion using `change_duration=False`

### 2. Preserve Original Frame Rate
- **No longer forces 30fps** - uses the source video's actual frame rate
- **Rounds to common FPS** (23.976, 24, 25, 29.97, 30, 60) if close
- **Prevents unnecessary conversion** that could cause sync issues

### 3. Explicit Audio Sync
- **Checks** audio and video duration match
- **Adjusts** audio duration if needed to match video
- **Uses FFmpeg sync parameters** (`-async 1`, `-vsync cfr`) during encoding
- **Sets proper audio sample rate** (44.1kHz) for consistency

### 4. Dynamic Keyframe Intervals
- **Keyframe interval** now matches the actual frame rate
- **1 keyframe per second** (e.g., 30fps = 30 frame keyframe interval)
- **Prevents sync issues** during playback

---

## Technical Changes

### `normalize_video()` Function
**Before:**
- Only noted the FPS, didn't convert it
- No VFR detection or conversion
- No audio sync checking

**After:**
- Detects and converts VFR to CFR early
- Preserves original frame rate (or rounds to common FPS)
- Explicitly checks and fixes audio-video duration mismatch
- Uses `set_fps()` with `change_duration=False` to preserve sync

### `export_video()` Function
**Before:**
- Forced all videos to 30fps: `fps=30`
- Fixed keyframe interval: `-g 30`
- No audio sync parameters

**After:**
- Uses actual clip FPS: `fps=output_fps`
- Dynamic keyframe interval based on actual FPS
- Audio sync parameters: `-async 1`, `-vsync cfr`
- Proper audio settings: `audio_nbytes=4`, `audio_fps=44100`

---

## How It Works

### Step 1: Load and Normalize
```
Original video (VFR, 29.97fps variable)
    ↓
Detect VFR → Convert to CFR (29.97fps constant)
    ↓
Check audio duration matches video
    ↓
Normalized clip (CFR, synced audio)
```

### Step 2: Process and Export
```
Normalized clip (29.97fps)
    ↓
Apply transformations (resize, vertical conversion, etc.)
    ↓
Export with original FPS (29.97fps)
    ↓
Use FFmpeg sync parameters
    ↓
Final video (CFR, perfect sync)
```

---

## Frame Rate Handling

### Common Phone Video Frame Rates
- **29.97 fps**: Most common (NTSC standard)
- **30 fps**: Some phones/cameras
- **25 fps**: PAL standard (less common in US)
- **60 fps**: High frame rate recordings

### What the Code Does
1. **Detects** the original frame rate
2. **Rounds** to nearest common FPS if within 0.5fps
   - 29.95fps → 29.97fps
   - 30.1fps → 30fps
   - 24.2fps → 24fps
3. **Converts VFR to CFR** at that frame rate
4. **Uses that FPS** for encoding (no forced conversion)

---

## Benefits

✅ **Fixes sync issues** - VFR converted to CFR early prevents drift
✅ **Preserves original quality** - No unnecessary frame rate conversion
✅ **Maintains audio sync** - Explicit sync checking and FFmpeg parameters
✅ **Works for all videos** - Handles 24fps, 25fps, 29.97fps, 30fps, 60fps
✅ **Prevents future issues** - Early conversion prevents sync problems in processing

---

## Testing

To verify the fix works:

1. **Check the output** during processing:
   ```
   Original FPS: 29.97
   Converting VFR to CFR: 29.97 → 29.97 fps
   [OK] Frame rate normalized (audio sync preserved)
   ```

2. **Verify in exported video**:
   - Audio and video should be perfectly in sync
   - No delay between audio and video
   - Smooth playback

3. **If issues persist**:
   - Check the original video's frame rate (shown in Step 1)
   - Verify audio duration matches video duration (shown in normalization)
   - Look for any warnings about audio/video mismatch

---

## Summary

The fix addresses the root cause of audio-video sync issues:
- **VFR videos** are converted to CFR early in the pipeline
- **Original frame rate** is preserved (no forced 30fps conversion)
- **Audio sync** is explicitly maintained throughout processing
- **FFmpeg parameters** ensure sync during encoding

This should resolve sync issues for all videos, especially those from phones that record in Variable Frame Rate.

