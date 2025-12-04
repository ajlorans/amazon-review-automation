# Testing TikTok Uploads

## Quick Test

### Step 1: Make sure TikTok is enabled

Check your `.env` file and make sure TikTok is included in `UPLOAD_PLATFORMS`:

```env
UPLOAD_PLATFORMS=youtube,instagram,tiktok
```

Or use `all` to enable all platforms:

```env
UPLOAD_PLATFORMS=all
```

### Step 2: Test with a single video

**Option A: Test with a video from your inputs folder**

```bash
python process.py --input your-video.mp4 --upload
```

**Option B: Test with a full path**

```bash
python process.py --input "C:/path/to/your/video.mp4" --upload
```

**Option C: Test TikTok only (process but don't upload to other platforms)**

First, temporarily set in `.env`:

```env
UPLOAD_PLATFORMS=tiktok
```

Then run:

```bash
python process.py --input your-video.mp4 --upload
```

### Step 3: What to expect

When the upload starts, you'll see:

```
Uploading to TIKTOK...
  [OK] Authenticated with TikTok API
  Initializing TikTok upload...
  Uploading video file...
  Finalizing upload...
  [OK] Video uploaded successfully!
  Video ID: [some-id]
  Status: private
```

## Important Notes

### Privacy Status

By default, videos are uploaded as **"private"** (drafts) so you can review them before publishing. This is controlled by `UPLOAD_PRIVACY_STATUS` in your `.env`:

- `UPLOAD_PRIVACY_STATUS=private` - Uploads as draft (SELF_ONLY)
- `UPLOAD_PRIVACY_STATUS=public` - Uploads as public (PUBLIC_TO_EVERYONE)

### Where to find your video

After upload:

1. **Open the TikTok app** on your phone
2. Go to your **profile**
3. Check **"Drafts"** (if uploaded as private) or your **feed** (if uploaded as public)

### Video Format

TikTok videos will be:

- **Format**: Vertical 9:16 (1080x1920)
- **Duration**: Limited to 60 seconds (for TikTok requirements)
- **File size**: Should be under TikTok's limits

## Troubleshooting

### "Error: TIKTOK_ACCESS_TOKEN not set in .env"

- Make sure you ran `python auth_tiktok.py` successfully
- Check that `TIKTOK_ACCESS_TOKEN` is in your `.env` file

### "Error: Invalid access token"

- Your token may have expired
- Run `python auth_tiktok.py` again to get a new token

### "Error initializing upload" or "Error uploading file"

- Check your TikTok app settings - make sure "Content Publishing API" is enabled
- Verify your app is approved/submitted (if required)
- Check the error message for specific details

### Video doesn't appear in TikTok app

- Check your **Drafts** folder (if uploaded as private)
- Wait a few minutes - TikTok may need time to process
- Check the upload status using the Video ID from the output

## Test Without Uploading

If you want to test the video processing (format conversion, etc.) without uploading:

```bash
python process.py --input your-video.mp4 --no-upload
```

This will:

- Process the video
- Convert to vertical format for TikTok
- Save to `storage/outputs/tiktok/`
- **NOT** upload to TikTok

Then check the output video to make sure it looks good before uploading.

## Full Test Workflow

1. **Test processing first:**

   ```bash
   python process.py --input test-video.mp4 --no-upload
   ```

2. **Check the output video:**

   - Go to `storage/outputs/tiktok/`
   - Open the video and verify it looks good

3. **Test upload:**

   ```bash
   python process.py --input test-video.mp4 --upload
   ```

4. **Check TikTok app:**
   - Open TikTok app
   - Check Drafts (if private) or feed (if public)
   - Review the video and publish if ready

## Success Indicators

✅ **Processing successful:**

- Video saved to `storage/outputs/tiktok/[date]/`
- Metadata file created

✅ **Upload successful:**

- See "[OK] Video uploaded successfully!" message
- Get a Video ID
- Video appears in TikTok app (Drafts or feed)
