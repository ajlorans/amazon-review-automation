# Upload Automation Setup Guide

This guide will help you set up automatic video uploads to YouTube Shorts, Instagram Reels, and TikTok.

## Overview

The upload system automatically uploads processed videos to your social media accounts as **drafts**, so you can review them before publishing.

## Prerequisites

1. **YouTube**: Google account with YouTube channel
2. **Instagram**: Instagram Business or Creator account
3. **TikTok**: TikTok account with Content Publishing API access

---

## YouTube Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **YouTube Data API v3**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"

### Step 2: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: **Desktop app**
4. Name it (e.g., "Video Uploader")
5. Click "Create"
6. Download the JSON file
7. Save it as `storage/credentials/youtube_client_secrets.json`

### Step 3: Configure .env

```env
YOUTUBE_CLIENT_SECRETS_FILE=storage/credentials/youtube_client_secrets.json
```

### Step 4: First-Time Authentication

When you run the uploader for the first time:

1. A browser window will open
2. Sign in with your Google account
3. Grant permissions to access YouTube
4. The token will be saved automatically

---

## Instagram Setup

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add **Instagram Graph API** product
4. Set up Instagram Basic Display or Instagram Graph API

### Step 2: Get Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Add permissions: `instagram_basic`, `instagram_content_publish`, `pages_show_list`
4. Generate a **long-lived access token** (valid for 60 days)
5. For production, set up token refresh

### Step 3: Get Instagram Account ID

1. Go to [Facebook Business Settings](https://business.facebook.com/settings)
2. Navigate to "Instagram Accounts"
3. Find your account ID (numeric)

### Step 4: Configure .env

```env
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id
```

**Note**: Instagram Reels upload requires the video to be uploaded to a publicly accessible URL first. The current implementation is a placeholder - you may need to upload videos to a cloud storage service (S3, Google Cloud Storage) first.

---

## TikTok Setup

### Step 1: Create TikTok App

1. Go to [TikTok Developers](https://developers.tiktok.com/)
2. Create a new app
3. Add **Content Publishing** capability
4. Note your **Client Key** and **Client Secret**

### Step 2: Complete OAuth2 Flow

1. Use the authorization URL from your app settings
2. Authorize the app with your TikTok account
3. Get the authorization code
4. Exchange it for an access token

**Quick OAuth2 Flow** (you may need to implement this):

```
1. Redirect user to: https://www.tiktok.com/v2/auth/authorize/
   ?client_key=YOUR_CLIENT_KEY
   &scope=video.upload
   &response_type=code
   &redirect_uri=YOUR_REDIRECT_URI

2. User authorizes, gets redirected with code

3. Exchange code for token:
   POST https://open.tiktokapis.com/v2/oauth/token/
   {
     "client_key": "YOUR_CLIENT_KEY",
     "client_secret": "YOUR_CLIENT_SECRET",
     "code": "AUTHORIZATION_CODE",
     "grant_type": "authorization_code",
     "redirect_uri": "YOUR_REDIRECT_URI"
   }
```

### Step 3: Configure .env

```env
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
TIKTOK_ACCESS_TOKEN=your_access_token
```

---

## Usage

### Enable Uploads

1. Set in `.env`:

   ```env
   AUTO_UPLOAD_ENABLED=true
   UPLOAD_PRIVACY_STATUS=private  # For drafts
   ```

2. Or use CLI flag:
   ```bash
   python process.py --input video.mp4 --upload
   ```

### Upload Status

Upload results are saved in the metadata JSON files:

```json
{
  "title": "...",
  "description": "...",
  "upload": {
    "video_id": "...",
    "status": "private",
    "url": "...",
    "platform": "youtube"
  }
}
```

### Platform-Specific Notes

- **YouTube**: Videos uploaded as "private" appear in YouTube Studio as drafts
- **Instagram**: Requires video to be uploaded to a public URL first (implementation needed)
- **TikTok**: Videos uploaded as "SELF_ONLY" are drafts in TikTok Studio

---

## Troubleshooting

### YouTube

- **"Invalid credentials"**: Re-download client secrets JSON
- **"Token expired"**: Delete `storage/tokens/youtube_token.json` and re-authenticate

### Instagram

- **"Invalid access token"**: Generate a new long-lived token
- **"Permission denied"**: Ensure you have Instagram Business/Creator account

### TikTok

- **"Invalid access token"**: Complete OAuth2 flow again
- **"Upload failed"**: Check video file size (TikTok has limits)

---

## Security Notes

- **Never commit** `.env` file or credential files to git
- Store tokens securely
- Rotate tokens regularly
- Use environment variables in production

---

## Next Steps

1. Set up API credentials for each platform
2. Test with a single video: `python process.py --input test.mp4 --upload`
3. Once working, enable for batch processing: `python process.py --batch --upload`
