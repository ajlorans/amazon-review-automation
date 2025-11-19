# TikTok Setup Guide

## Step 1: Get Your Client Key and Secret

1. Go to **https://developers.tiktok.com/**
2. Log in with your TikTok account
3. Click on your app (or create a new one if you haven't)
4. Go to **"Basic Information"** or **"Keys"** section
5. You'll see:
   - **Client Key** (also called App ID)
   - **Client Secret**
6. Copy both values

## Step 2: Configure Redirect URI

1. In your TikTok app settings, find **"Platform"** or **"OAuth"** section
2. Add a redirect URI. For local testing, use:
   - `http://localhost:8080`
3. Save the settings

**Important:** The redirect URI must match exactly what you use in the script!

## Step 3: Run the Authentication Script

Run the helper script:
```bash
python auth_tiktok.py
```

The script will:
1. Ask for your Client Key and Secret (or read from .env)
2. Ask for your Redirect URI
3. Open a browser window for authorization
4. Guide you through getting the authorization code
5. Exchange the code for an access token
6. Save everything to your .env file

## Step 4: Manual Process (if script doesn't work)

If you prefer to do it manually:

### 1. Get Authorization Code

Open this URL in your browser (replace YOUR_CLIENT_KEY and YOUR_REDIRECT_URI):
```
https://www.tiktok.com/v2/auth/authorize/?client_key=YOUR_CLIENT_KEY&scope=video.upload&response_type=code&redirect_uri=YOUR_REDIRECT_URI
```

After authorizing, you'll be redirected to:
```
YOUR_REDIRECT_URI?code=AUTHORIZATION_CODE&state=...
```

Copy the `code` value from the URL.

### 2. Exchange Code for Token

Use this command (replace values):
```bash
curl -X POST "https://open.tiktokapis.com/v2/oauth/token/" \
  -H "Content-Type: application/json" \
  -d '{
    "client_key": "YOUR_CLIENT_KEY",
    "client_secret": "YOUR_CLIENT_SECRET",
    "code": "AUTHORIZATION_CODE",
    "grant_type": "authorization_code",
    "redirect_uri": "YOUR_REDIRECT_URI"
  }'
```

Or use the Python script - it's much easier!

## Step 5: Update .env File

Your .env file should have:
```env
TIKTOK_CLIENT_KEY=your_client_key_here
TIKTOK_CLIENT_SECRET=your_client_secret_here
TIKTOK_ACCESS_TOKEN=your_access_token_here
```

The script will do this automatically, or you can add it manually.

## Troubleshooting

### "Invalid redirect_uri"
- Make sure the redirect URI in your TikTok app settings matches exactly
- Check for trailing slashes, http vs https, etc.

### "Authorization code expired"
- Authorization codes expire very quickly (usually within minutes)
- Run the script again to get a fresh code

### "Invalid client_key or client_secret"
- Double-check you copied the values correctly
- Make sure there are no extra spaces

### "Access denied" or "Insufficient permissions"
- Make sure your app has "Content Publishing" capability enabled
- Check that you granted all required permissions during authorization

## Testing

After setup, test your authentication:
```bash
python process.py --input storage/inputs/amazon-review-labtop.mp4 --upload
```

Or test just TikTok:
```python
from uploaders.tiktok_uploader import TikTokUploader
uploader = TikTokUploader()
uploader.authenticate()  # Should print "[OK] Authenticated with TikTok API"
```

## Token Refresh

Access tokens expire. When they do, you'll need to:
1. Run `python auth_tiktok.py` again
2. Get a new authorization code
3. Exchange it for a new access token

Some tokens come with refresh tokens - the script will handle those if available.

