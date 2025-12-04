# Instagram File Size Optimization

## Problem

Instagram Reels have a **100MB file size limit**. Full-length videos were exceeding this limit, causing upload failures.

## Solution

Implemented **dynamic bitrate calculation** that automatically adjusts video bitrate based on video duration to ensure files stay under 100MB.

---

## How It Works

### Dynamic Bitrate Calculation

The system now calculates the optimal bitrate for each Instagram video based on its duration:

1. **Formula**: `bitrate = (target_size_mb * 8) / duration - audio_bitrate`
2. **Target Size**: 95MB (leaves 5MB margin)
3. **Bitrate Range**:
   - Minimum: 800k (for very long videos)
   - Maximum: 8000k (for short videos)
   - Dynamic: Calculated based on duration

### Example Calculations

**Short video (30 seconds):**

- Bitrate: ~8000k (8 Mbps)
- File size: ~30MB ✅

**Medium video (60 seconds):**

- Bitrate: ~6000k (6 Mbps)
- File size: ~45MB ✅

**Long video (120 seconds / 2 minutes):**

- Bitrate: ~3000k (3 Mbps)
- File size: ~80MB ✅

**Very long video (300 seconds / 5 minutes):**

- Bitrate: ~2000k (2 Mbps)
- File size: ~95MB ✅

**Extremely long video (600 seconds / 10 minutes):**

- Bitrate: ~1000k (1 Mbps)
- File size: ~90MB ✅

---

## Automatic Re-encoding

If a video still exceeds 100MB after the initial encoding, the system will:

1. **Detect** the file size issue
2. **Re-calculate** bitrate with a 90MB target (more aggressive)
3. **Re-encode** the video automatically
4. **Verify** the new file size

This ensures videos fit under the limit even for edge cases.

---

## What Changed

### `process.py`

- Added `calculate_instagram_bitrate()` function
- Updated `export_video()` to use dynamic bitrate for Instagram
- Added automatic re-encoding if file is still too large
- Added file size verification and reporting

### `uploaders/instagram_uploader.py`

- Improved error messages for file size issues
- Added suggestions for handling oversized videos

---

## Usage

No changes needed! The system automatically handles file size optimization:

```bash
python process.py --input storage/inputs/your-video.mp4 --upload
```

The export process will:

1. Calculate optimal bitrate based on video duration
2. Encode with that bitrate
3. Check file size
4. Re-encode if needed (with lower bitrate)
5. Report the final file size

---

## Output Example

```
Exporting instagram video to storage/outputs/instagram/2025-12-02/video.mp4...
  Video duration: 180.5s
  Calculated bitrate: 4000k (estimated size: 94.5MB)
  Actual file size: 95.2MB
  [OK] File size under 100MB limit
[OK] instagram video exported successfully!
```

If re-encoding is needed:

```
  Actual file size: 105.3MB
  [WARNING] File size (105.3MB) exceeds 100MB limit!
  Re-encoding with lower bitrate to fit under 100MB...
  New bitrate: 3500k
  New file size: 89.1MB
  [OK] File size now under 100MB limit
```

---

## Quality Considerations

### Bitrate vs Quality

- **Higher bitrate** = Better quality, larger file
- **Lower bitrate** = Smaller file, slightly lower quality

The system balances:

- **Short videos**: High bitrate (up to 8 Mbps) for excellent quality
- **Long videos**: Lower bitrate (1-3 Mbps) to fit under 100MB

### Quality Levels

- **8000k (8 Mbps)**: Excellent quality (short videos)
- **4000k (4 Mbps)**: Very good quality (medium videos)
- **2000k (2 Mbps)**: Good quality (long videos)
- **1000k (1 Mbps)**: Acceptable quality (very long videos)
- **800k (0.8 Mbps)**: Minimum quality (extremely long videos)

For most videos, quality will be **very good to excellent**. Only very long videos (5+ minutes) will use lower bitrates.

---

## Troubleshooting

### Video Still Too Large After Re-encoding

If a video still exceeds 100MB after automatic re-encoding, it's likely **extremely long** (10+ minutes). Options:

1. **Split the video** into shorter segments
2. **Reduce video length** before processing
3. **Accept lower quality** (the system already uses minimum viable bitrate)

### Quality Concerns

If you notice quality issues:

- Check the bitrate used (shown in export output)
- For very long videos, lower bitrate is necessary to fit under 100MB
- Consider splitting long videos into multiple shorter segments

---

## Technical Details

### Formula Breakdown

```
file_size_mb = (video_bitrate_mbps + audio_bitrate_mbps) * duration_seconds / 8

Solving for video_bitrate:
video_bitrate_mbps = (target_size_mb * 8) / duration_seconds - audio_bitrate_mbps
```

Where:

- `target_size_mb` = 95MB (with 5MB margin)
- `audio_bitrate_mbps` = 0.192 Mbps (192k)
- `duration_seconds` = Video length in seconds

### Bitrate Clamping

- **Normal videos**: Clamped between 1000k and 8000k
- **Very long videos**: Can go below 1000k (minimum 800k) to fit under 100MB

---

## Summary

✅ **Automatic file size optimization** for Instagram videos
✅ **Dynamic bitrate calculation** based on video duration
✅ **Automatic re-encoding** if file is still too large
✅ **Quality maintained** for most video lengths
✅ **No manual intervention** required

Your Instagram videos will now automatically fit under the 100MB limit while maintaining the best possible quality for each video length!
