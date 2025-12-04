# TikTok Sandbox Mode - How to Make It Work

## Good News! ✅

**TikTok Sandbox mode DOES support video uploads**, but with specific requirements:

## Requirements for Sandbox Mode

### 1. Privacy Level Must Be `SELF_ONLY`

In Sandbox mode, you can **only** upload videos with `privacy_level: "SELF_ONLY"`. This means:

- Videos are visible only to you (drafts)
- Videos appear in your Drafts folder
- You can review and publish them manually from the TikTok app

**Public uploads (`PUBLIC_TO_EVERYONE`) do NOT work in Sandbox mode.**

### 2. TikTok Account Must Be Private

**Important:** Your TikTok account must be set to **Private** in the TikTok app for Sandbox uploads to work.

**To check/set your account to private:**

1. Open TikTok app on your phone
2. Go to your Profile
3. Tap the three lines (☰) in the top right
4. Go to **Settings and privacy**
5. Go to **Privacy**
6. Turn on **Private account**

### 3. Daily Limit

Sandbox mode has a limit of approximately **15 posts per day** per creator account.

## Current Code Status

The code already uses `SELF_ONLY` for private uploads (when `UPLOAD_PRIVACY_STATUS=private` in `.env`), so it should work in Sandbox mode.

**Make sure your `.env` has:**

```env
UPLOAD_PRIVACY_STATUS=private
```

This will use `SELF_ONLY` which is required for Sandbox.

## Troubleshooting

### Still Getting "scope_not_authorized" Error?

Even in Sandbox mode, you might get this error if:

1. **Your TikTok account is not set to Private**

   - Fix: Set your account to Private in TikTok app (see steps above)

2. **The token doesn't have the correct scope**

   - Fix: Re-run `python auth_tiktok.py` and grant ALL permissions

3. **App configuration issue**
   - Make sure "Content Publishing API" is enabled in your app
   - Check that all required app fields are filled out

### Test Steps

1. **Set your TikTok account to Private:**

   - TikTok app → Profile → Settings → Privacy → Private account ON

2. **Verify your .env settings:**

   ```env
   UPLOAD_PRIVACY_STATUS=private
   TIKTOK_ACCESS_TOKEN=your_token_here
   ```

3. **Test the upload:**

   ```bash
   python process.py --input your-video.mp4 --upload
   ```

4. **Check your TikTok app:**
   - Go to Profile
   - Check **Drafts** folder
   - Video should appear there (not published)

## What to Expect

When upload succeeds in Sandbox mode:

- ✅ Video uploads successfully
- ✅ Appears in your **Drafts** folder in TikTok app
- ✅ You can review and publish manually
- ✅ Only visible to you (SELF_ONLY)

## Moving to Production Mode

To upload public videos or remove Sandbox limitations:

1. **Submit your app for review:**

   - Go to https://developers.tiktok.com/
   - Open your app
   - Submit for review
   - Fill out all required information
   - Wait for approval (can take days to weeks)

2. **After approval:**
   - You can use `PUBLIC_TO_EVERYONE` privacy level
   - No daily limit restrictions
   - Full API access

## Quick Checklist

- [ ] TikTok account is set to **Private** in TikTok app
- [ ] `.env` has `UPLOAD_PRIVACY_STATUS=private`
- [ ] Token has `video.upload` scope (check with `python check_tiktok_token.py`)
- [ ] Content Publishing API is enabled in your TikTok app
- [ ] Try uploading: `python process.py --input video.mp4 --upload`
- [ ] Check TikTok app → Profile → Drafts for uploaded video

## If It Still Doesn't Work

1. **Check the full error:**

   ```bash
   python check_tiktok_token.py
   ```

   Look at the complete error message

2. **Verify account is private:**

   - This is often the issue - TikTok requires private account for Sandbox

3. **Re-authorize:**

   ```bash
   python auth_tiktok.py
   ```

   Make sure to grant ALL permissions

4. **Check app status:**
   - Make sure app is not in "Draft" status
   - All required fields should be filled out
