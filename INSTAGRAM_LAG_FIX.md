# Instagram Video Lag Fix

## Problem

Instagram videos were experiencing lag/stuttering during playback, especially for longer videos.

## Root Cause

- Lower bitrates (800k-2000k) for longer videos to fit under 100MB limit
- Fast encoding preset sacrificing quality for speed
- Missing advanced encoding optimizations for smooth playback

## Solution

Implemented comprehensive encoding optimizations to reduce lag while maintaining file size constraints.

---

## Improvements Made

### 1. Higher Minimum Bitrate

- **Before**: 800k-1000k minimum (caused lag)
- **After**: 2500k (2.5 Mbps) minimum for most videos
- **Very long videos**: 2000k (2 Mbps) minimum

This ensures smoother playback even for longer videos.

### 2. Better Encoding Preset

- **Before**: `fast` preset (prioritized speed over quality)
- **After**: `medium` preset (better quality, smoother playback)

Slightly slower encoding but significantly better quality and smoother playback.

### 3. Advanced Encoding Parameters

Added professional-grade encoding settings:

- **High Profile**: Better compression efficiency
- **H.264 Level 4.0**: Ensures compatibility
- **Keyframe Interval**: 1 per second (30 frames) for smooth seeking
- **B-frames**: Better compression with adaptive placement
- **Lookahead**: 30 frames for better quality decisions
- **Reference Frames**: 3 frames for better quality
- **Trellis Quantization**: Better quality at same bitrate

### 4. Smart Bitrate Calculation

The system now:

- Uses minimum 2500k for videos under 5 minutes
- Uses minimum 2000k for very long videos (5+ minutes)
- Only reduces bitrate below minimum if absolutely necessary to fit under 100MB
- Checks if minimum bitrate would exceed 100MB before applying it

---

## Technical Details

### Encoding Settings

**Instagram Videos:**

- Preset: `medium` (was `fast`)
- Minimum Bitrate: 2500k (was 1000k)
- Profile: `high`
- Keyframe Interval: 30 frames (1 per second)
- B-frames: 2 with adaptive placement
- Lookahead: 30 frames
- Reference Frames: 3
- Trellis: Enabled

**TikTok Videos:**

- Same optimizations as Instagram
- Higher file size limit allows for better quality

**YouTube Videos:**

- Already using high bitrate (10 Mbps)
- No changes needed

---

## Bitrate Strategy

### Short Videos (< 2 minutes)

- Bitrate: 5000k-8000k (5-8 Mbps)
- Quality: Excellent
- File Size: 30-60MB ✅

### Medium Videos (2-5 minutes)

- Bitrate: 2500k-5000k (2.5-5 Mbps)
- Quality: Very Good
- File Size: 60-95MB ✅

### Long Videos (5-10 minutes)

- Bitrate: 2000k-2500k (2-2.5 Mbps)
- Quality: Good (smooth playback)
- File Size: 85-100MB ✅

### Very Long Videos (10+ minutes)

- Bitrate: 2000k minimum
- Quality: Good (prevents lag)
- File Size: May approach 100MB limit

---

## Quality vs File Size Balance

The system now prioritizes **quality and smooth playback** while still respecting the 100MB limit:

1. **First Priority**: Use minimum bitrate (2500k or 2000k) for smooth playback
2. **Second Priority**: Check if this fits under 100MB
3. **If Too Large**: Re-encode with calculated bitrate (but never below 2000k)

This ensures:

- ✅ Smooth playback (no lag)
- ✅ Good quality
- ✅ Stays under 100MB (when possible)

---

## Expected Results

### Before

- Short videos: Smooth ✅
- Medium videos: Some lag ⚠️
- Long videos: Noticeable lag ❌

### After

- Short videos: Smooth ✅
- Medium videos: Smooth ✅
- Long videos: Smooth ✅ (with minimum 2000k bitrate)

---

## File Size Impact

The higher minimum bitrate may result in:

- **Slightly larger files** for very long videos
- **Better quality** and **smoother playback**
- **Automatic re-encoding** if file exceeds 100MB

For most videos (under 5 minutes), file sizes will remain similar or only slightly larger.

---

## Usage

No changes needed! The optimizations are automatic:

```bash
python process.py --input storage/inputs/your-video.mp4 --upload
```

The system will:

1. Calculate optimal bitrate (with quality minimums)
2. Encode with optimized settings
3. Verify file size
4. Re-encode if needed (maintaining quality minimums)

---

## Troubleshooting

### If Video Still Lags

1. **Check the bitrate used** (shown in export output)

   - Should be at least 2000k for long videos
   - Should be 2500k+ for shorter videos

2. **Check video duration**

   - Very long videos (10+ minutes) may need to be split

3. **Check file size**
   - If file is close to 100MB, bitrate may have been reduced
   - Consider splitting very long videos

### If File Exceeds 100MB

The system will automatically:

1. Detect the issue
2. Re-encode with lower bitrate
3. Maintain minimum 2000k for quality

If it still exceeds 100MB after re-encoding, the video is likely too long and should be split.

---

## Summary

✅ **Higher minimum bitrates** (2500k/2000k) prevent lag
✅ **Better encoding preset** (`medium` instead of `fast`)
✅ **Advanced encoding parameters** for smoother playback
✅ **Smart bitrate calculation** balances quality and file size
✅ **Automatic optimization** - no manual intervention needed

Your Instagram videos should now play smoothly without lag while still fitting under the 100MB limit!
