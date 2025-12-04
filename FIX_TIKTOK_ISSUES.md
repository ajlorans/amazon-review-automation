# Fixing TikTok Issues

## Issue 1: Platform Filtering Not Working

### Problem

When you set `UPLOAD_PLATFORMS=tiktok` in `.env`, it still processes/uploads to all platforms.

### Solution

**Make sure your `.env` file uses the correct variable name (uppercase):**

```env
UPLOAD_PLATFORMS=tiktok
```

**NOT:**

```env
upload_platforms=tiktok  ❌ (wrong - lowercase won't work)
```

### How to Test

1. **Set in `.env`:**

   ```env
   UPLOAD_PLATFORMS=tiktok
   ```

2. **Run with upload:**

   ```bash
   python process.py --input your-video.mp4 --upload
   ```

3. **You should see:**
   ```
   Processing videos for platforms: tiktok
   ...
   Step 7: Uploading videos to platforms...
   Configured platforms: tiktok
   Uploading to TIKTOK...
   ```

### Other Platform Options

```env
# Only TikTok
UPLOAD_PLATFORMS=tiktok

# Only YouTube
UPLOAD_PLATFORMS=youtube

# Only Instagram
UPLOAD_PLATFORMS=instagram

# Multiple platforms (comma-separated, no spaces)
UPLOAD_PLATFORMS=youtube,instagram

# All platforms
UPLOAD_PLATFORMS=all
```

---

## Issue 2: Scope Not Authorized Error

### Problem

```
Error initializing upload: 401
Response: {"error":{"code":"scope_not_authorized",...}}
```

This means your TikTok token doesn't have the `video.upload` scope.

### Solution

**Step 1: Check your current token**

```bash
python check_tiktok_token.py
```

This will tell you if your token has the correct scopes.

**Step 2: Re-authorize with ALL permissions**

```bash
python auth_tiktok.py
```

**IMPORTANT:** When the browser opens:

- ✅ **GRANT ALL PERMISSIONS**
- ✅ **Check ALL permission boxes**
- ✅ **Especially make sure "video.upload" or "Upload videos" is checked**
- ❌ **Don't skip any permissions**

**Step 3: Verify the new token**

After re-authorizing, run:

```bash
python check_tiktok_token.py
```

You should see:

```
[OK] Token is valid
[OK] video.upload scope is authorized!
  You can upload videos to TikTok
```

**Step 4: Test upload again**

```bash
python process.py --input your-video.mp4 --upload
```

---

## Quick Checklist

- [ ] `.env` file has `UPLOAD_PLATFORMS=tiktok` (uppercase, not lowercase)
- [ ] Ran `python check_tiktok_token.py` and it shows `[OK] video.upload scope is authorized!`
- [ ] If scope check failed, ran `python auth_tiktok.py` and granted ALL permissions
- [ ] Tested upload with `python process.py --input video.mp4 --upload`

---

## Still Having Issues?

### Check .env File Format

Make sure your `.env` file looks like this:

```env
# TikTok Configuration
TIKTOK_CLIENT_KEY=your_client_key_here
TIKTOK_CLIENT_SECRET=your_client_secret_here
TIKTOK_ACCESS_TOKEN=your_access_token_here

# Upload Settings
UPLOAD_PLATFORMS=tiktok
AUTO_UPLOAD_ENABLED=false
```

**Common mistakes:**

- ❌ `upload_platforms=tiktok` (lowercase - won't work)
- ❌ `UPLOAD_PLATFORMS = tiktok` (spaces around = - might cause issues)
- ❌ `UPLOAD_PLATFORMS="tiktok"` (quotes - not needed)

**Correct:**

- ✅ `UPLOAD_PLATFORMS=tiktok` (uppercase, no spaces, no quotes)

### Debug Output

The updated code now shows which platforms are configured. When you run the script, look for:

```
Processing videos for platforms: tiktok
...
Configured platforms: tiktok
```

If you see all three platforms listed, check your `.env` file format.
