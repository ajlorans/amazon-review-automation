# TikTok Quick Setup Guide

## What You Need in Your TikTok App Settings

### ✅ **Add These Products/APIs:**

1. **Content Publishing API** ✅ (REQUIRED)

   - This is what you need to upload videos
   - Go to your app → "Products" or "APIs" section
   - Enable "Content Publishing API" or "Video Upload API"

2. **Login Kit** ❌ (NOT NEEDED)
   - This is for user login/authentication
   - You don't need this for uploading videos
   - Skip this one

### Summary:

- ✅ **Content Publishing API** - YES, add this
- ❌ **Login Kit** - NO, you don't need this

---

## Where to Get Your Access Token

The access token is **NOT** in your app settings. You need to get it through the OAuth2 flow.

### Step-by-Step:

1. **Get Client Key and Secret** (from app settings):

   - Go to: https://developers.tiktok.com/
   - Open your app
   - Go to "Basic Information" or "Keys" section
   - Copy:
     - **Client Key** (also called App ID)
     - **Client Secret**

2. **Add Redirect URI** (in app settings):

   - Go to "Platform" or "OAuth" settings
   - Add redirect URI: `http://localhost:8080`
   - Save

3. **Run the Authentication Script** (to get access token):

   ```bash
   python auth_tiktok.py
   ```

   This script will:

   - Ask for your Client Key and Secret (or read from .env)
   - Open a browser for authorization
   - Guide you through getting the authorization code
   - Exchange the code for an access token
   - Save the token to your .env file

4. **The Access Token** will be saved to your `.env` file automatically:
   ```
   TIKTOK_ACCESS_TOKEN=your_token_here
   ```

---

## Complete Setup Checklist

### In TikTok Developer Portal (https://developers.tiktok.com/):

- [ ] Create/select your app
- [ ] Fill out app information (name, description, etc.)
- [ ] **Enable "Content Publishing API"** (in Products/APIs section)
- [ ] **Skip "Login Kit"** (not needed)
- [ ] Go to "Basic Information" → Copy **Client Key** and **Client Secret**
- [ ] Go to "Platform" or "OAuth" → Add redirect URI: `http://localhost:8080`

### In Your Project:

- [ ] Add to `.env` file:

  ```
  TIKTOK_CLIENT_KEY=your_client_key_here
  TIKTOK_CLIENT_SECRET=your_client_secret_here
  ```

- [ ] Run authentication script:

  ```bash
  python auth_tiktok.py
  ```

- [ ] The script will automatically add `TIKTOK_ACCESS_TOKEN` to your `.env` file

---

## Quick Reference

**What to Enable:**

- ✅ Content Publishing API

**What NOT to Enable:**

- ❌ Login Kit

**Where to Get:**

- **Client Key & Secret**: App settings → "Basic Information" or "Keys"
- **Access Token**: Run `python auth_tiktok.py` (OAuth2 flow)

**Redirect URI:**

- Use: `http://localhost:8080`
- Must match exactly in app settings and when running auth script

---

## Troubleshooting

**"Invalid redirect_uri" error:**

- Make sure the redirect URI in your app settings matches exactly: `http://localhost:8080`
- Check for trailing slashes, http vs https, etc.

**"Authorization code expired":**

- Authorization codes expire quickly (within minutes)
- Run `python auth_tiktok.py` again to get a fresh code

**"Insufficient permissions" or "Access denied":**

- Make sure you enabled "Content Publishing API" in your app settings
- Make sure you granted permissions during authorization

**Can't find "Content Publishing API" in app settings:**

- Look for "Products", "APIs", or "Capabilities" section
- It might be called "Video Upload API" or "Content Publishing"
- If you can't find it, your app might need to be submitted for review first
