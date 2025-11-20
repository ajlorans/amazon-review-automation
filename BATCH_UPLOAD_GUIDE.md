# Batch Upload Guide

## Quick Command

To process and upload **all videos** in your `storage/inputs/` folder:

```bash
python process.py --batch --upload
```

This will:

1. ✅ Process all videos in `storage/inputs/`
2. ✅ Convert them to vertical format (1080x1920)
3. ✅ Add CTA overlay
4. ✅ Export to YouTube, Instagram, and TikTok folders
5. ✅ Upload to all platforms (if enabled)
6. ✅ Archive processed videos to `storage/archive/`

## Command Options

### Basic Batch Processing (No Upload)

```bash
python process.py --batch
```

- Processes all videos
- Does NOT upload (just creates the formatted videos)

### Batch Processing with Upload

```bash
python process.py --batch --upload
```

- Processes all videos
- Uploads to YouTube, Instagram, and TikTok

### Batch from Custom Folder

```bash
python process.py --batch --input-folder "C:/path/to/your/videos" --upload
```

- Processes videos from a specific folder
- Uploads to all platforms

### Batch Without Archiving

```bash
python process.py --batch --upload --no-archive
```

- Processes and uploads all videos
- Keeps original videos in `storage/inputs/` (doesn't move to archive)

## What Happens During Batch Processing

1. **Scans** `storage/inputs/` for video files (.mp4, .mov, .avi, .mkv, .m4v)
2. **Processes each video**:
   - Converts to vertical 9:16 format
   - Adds CTA overlay
   - Exports to platform-specific folders
   - Generates metadata
3. **Uploads** (if `--upload` flag is used):
   - YouTube Shorts (as private/draft)
   - Instagram Reels (as draft)
   - TikTok Videos (as draft)
4. **Archives** processed videos (unless `--no-archive` is used)
5. **Shows summary** at the end

## Example Output

```
============================================================
BATCH PROCESSING: Found 3 video(s)
============================================================

[1/3] Processing: video1.mp4
============================================================
Processing: video1.mp4
============================================================
...
[OK] Processing complete!

[2/3] Processing: video2.mp4
...
[OK] Processing complete!

[3/3] Processing: video3.mp4
...
[OK] Processing complete!

============================================================
BATCH PROCESSING SUMMARY
============================================================
Total videos: 3
Successful: 3
Failed: 0
============================================================
```

## Before Running Batch Upload

Make sure you have:

1. ✅ **Videos in `storage/inputs/` folder**

   - Place all your videos there
   - Supported formats: .mp4, .mov, .avi, .mkv, .m4v

2. ✅ **API credentials set up** (if uploading):

   - YouTube: Token in `storage/tokens/youtube_token.json`
   - Instagram: `INSTAGRAM_ACCESS_TOKEN` in .env
   - TikTok: `TIKTOK_ACCESS_TOKEN` in .env

3. ✅ **Upload enabled** (if using `--upload`):
   - Or set `AUTO_UPLOAD_ENABLED=true` in .env

## Tips

### Process Without Upload First

Test the processing first:

```bash
python process.py --batch
```

Check the output videos in `storage/outputs/` to make sure they look good, then upload:

```bash
python process.py --batch --upload
```

### Skip Archiving During Testing

```bash
python process.py --batch --upload --no-archive
```

This keeps originals in `storage/inputs/` so you can re-process if needed.

### Process Specific Videos Only

If you only want to process certain videos:

1. Move only those videos to `storage/inputs/`
2. Run batch processing
3. Move them back or archive them

## Troubleshooting

### "No video files found"

- Make sure videos are in `storage/inputs/` folder
- Check file extensions (.mp4, .mov, etc.)
- Make sure files aren't corrupted

### "Upload failed"

- Check your API credentials
- Verify tokens haven't expired
- Check internet connection
- Review error messages in the output

### "Processing failed"

- Check video file isn't corrupted
- Make sure you have enough disk space
- Check FFmpeg is installed correctly

## Quick Reference

| Command                                           | What It Does                     |
| ------------------------------------------------- | -------------------------------- |
| `python process.py --batch`                       | Process all videos (no upload)   |
| `python process.py --batch --upload`              | Process and upload all videos    |
| `python process.py --batch --upload --no-archive` | Process, upload, keep originals  |
| `python process.py --input video.mp4 --upload`    | Process single video with upload |
