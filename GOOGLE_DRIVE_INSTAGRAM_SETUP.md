# Google Drive Setup for Instagram Uploads

## What's Been Implemented

Since Instagram requires a publicly accessible video URL, I've set up automatic Google Drive upload:

1. ✅ **Uploads video from `storage/inputs/` to Google Drive**
2. ✅ **Makes it publicly accessible**
3. ✅ **Gets the public URL**
4. ✅ **Uses that URL for Instagram upload**
5. ✅ **Uses your existing YouTube credentials** (same Google account)

## Setup

### Step 1: Add to .env File

Add this line to your `.env` file:

```env
INSTAGRAM_USE_GOOGLE_DRIVE=true
GOOGLE_DRIVE_CLIENT_SECRETS_FILE=storage/credentials/youtube_client_secrets.json
```

**Note:** You can use the same `youtube_client_secrets.json` file since it's the same Google account!

### Step 2: First-Time Google Drive Authentication

When you run the upload for the first time:

1. A browser window will open
2. Sign in with your **Google account** (same one you use for YouTube)
3. Grant permissions to access Google Drive
4. The token will be saved automatically to `storage/tokens/drive_token.json`

### Step 3: Test It

```bash
python process.py --input storage/inputs/amazon-review-labtop.mp4 --upload
```

Or batch upload:

```bash
python process.py --batch --upload
```

## How It Works

1. **Video from inputs folder** → Uploaded to Google Drive
2. **Made publicly accessible** → Gets public URL
3. **Public URL** → Used for Instagram upload
4. **Video appears as draft** in Instagram app

## What Gets Created

- **Google Drive folder**: "Instagram Videos" (created automatically)
- **Drive token**: `storage/tokens/drive_token.json` (saved after first auth)
- **Videos stay in Drive**: They're kept there (you can delete manually if needed)

## Optional: Clean Up Drive Videos

If you want to automatically delete videos from Drive after Instagram upload, I can add that feature. For now, videos stay in Drive in case you need them.

## Troubleshooting

### "Error authenticating with Google Drive"

- Make sure `GOOGLE_DRIVE_CLIENT_SECRETS_FILE` is set in .env
- You can use the same file as YouTube: `storage/credentials/youtube_client_secrets.json`
- Run the upload again to trigger authentication

### "Failed to upload to Google Drive"

- Check your internet connection
- Make sure you granted Drive permissions
- Check video file size (Google Drive has limits)

### "Video URL not accessible"

- Make sure the video was made public in Drive
- Check the URL format
- Try accessing the URL in a browser to verify it works

## Configuration

In your `.env` file:

```env
# Instagram (required)
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_ACCOUNT_ID=your_account_id

# Google Drive for Instagram (required)
INSTAGRAM_USE_GOOGLE_DRIVE=true
GOOGLE_DRIVE_CLIENT_SECRETS_FILE=storage/credentials/youtube_client_secrets.json
```

## Summary

✅ **Videos upload from `storage/inputs/`** (not from Drive initially)
✅ **Automatically uploads to Google Drive** to get public URL
✅ **Uses that URL for Instagram**
✅ **Uses your existing YouTube credentials** (same Google account)
✅ **Everything automated** - you just run the batch command!
