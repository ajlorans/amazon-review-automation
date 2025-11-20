# Fix: Instagram "Insufficient Developer Role" Error

## Problem

You're seeing: "Insufficient Developer Role: Insufficient developer role" when trying to add your Instagram account in Meta Developer Dashboard.

## Solution: Fix Your Developer Role

### Step 1: Check Your Role in the Facebook App

1. Go to **Meta for Developers**: https://developers.facebook.com/
2. Select your **App** (or create one if you haven't)
3. Go to **Settings** → **Roles** (or **App Roles**)
4. Check your role:
   - You need to be **Admin** or **Developer**
   - If you're not listed, you need to be added
   - If you're listed but as "Tester" or "Analyst", you need a higher role

### Step 2: Add Yourself as Admin/Developer

**If you created the app:**

- You should already be an Admin
- If not, check if someone else created it

**If someone else created the app:**

- Ask them to add you as an **Admin** or **Developer**
- They go to: App Settings → Roles → Add People
- Enter your email and select "Admin" or "Developer" role

### Step 3: Verify Instagram Account Type

Your Instagram account must be:

- ✅ **Instagram Business Account** OR
- ✅ **Instagram Creator Account**

**NOT a Personal Account!**

To check/convert:

1. Open Instagram app
2. Go to **Settings** → **Account**
3. Look for **"Switch to Professional Account"** or **"Account Type"**
4. If it says "Personal Account", convert it to Business or Creator

### Step 4: Link Instagram to Facebook Page

For Instagram Graph API, you need:

1. A **Facebook Page** (not just a profile)
2. Your Instagram account linked to that Facebook Page

**To link:**

1. Go to your Facebook Page: https://www.facebook.com/pages/manage/
2. Go to **Settings** → **Instagram**
3. Connect your Instagram Business/Creator account
4. Make sure it's properly linked

### Step 5: Add Instagram Product to Your App

1. In Meta Developer Dashboard, go to your **App**
2. Click **"Add Product"** or go to **Products**
3. Find **"Instagram"** and click **"Set Up"**
4. Select **"Instagram Graph API"** (not Basic Display)
5. Complete the setup

### Step 6: Get Access Token

Once you have the right role:

**Option A: Graph API Explorer (Easier)**

1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your **App** from the dropdown
3. Click **"Generate Access Token"**
4. Select permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
5. Generate token
6. Click **"i"** icon next to token → **"Open in Access Token Tool"**
7. Click **"Extend Access Token"** to get a long-lived token (60 days)

**Option B: Through App Settings**

1. Go to your App → **Tools** → **Graph API Explorer**
2. Follow the same steps as Option A

### Step 7: Get Instagram Account ID

1. Go to: https://business.facebook.com/settings
2. Click **"Instagram Accounts"** in left sidebar
3. Find your account
4. Copy the **Instagram Account ID** (numeric, like: 17841405309211844)

### Step 8: Update .env File

Add to your `.env` file:

```env
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token_here
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id_here
```

## Common Issues & Solutions

### "I can't see Roles in my app"

- Make sure you're the app owner or have been added as Admin
- Try creating a new app if you don't have access

### "My Instagram account is Personal"

- Convert to Business or Creator account in Instagram settings
- This is required for API access

### "I don't have a Facebook Page"

- Create one at: https://www.facebook.com/pages/create
- Link your Instagram account to it
- Required for Instagram Graph API

### "Token expires quickly"

- Short-lived tokens expire in 1-2 hours
- Use "Extend Access Token" to get 60-day token
- For production, set up token refresh

### "Still getting insufficient role error"

- Make sure you're logged into Meta Developer Dashboard with the same account that owns the app
- Try logging out and back in
- Clear browser cache

## Quick Checklist

- [ ] I'm an Admin or Developer in the Facebook App
- [ ] My Instagram account is Business or Creator (not Personal)
- [ ] I have a Facebook Page
- [ ] My Instagram is linked to my Facebook Page
- [ ] Instagram Graph API product is added to my app
- [ ] I've generated a long-lived access token
- [ ] I have my Instagram Account ID
- [ ] I've added both to my .env file

## Alternative: Instagram Basic Display API

If you can't get Graph API working, you can try Instagram Basic Display API:

- Simpler setup
- Fewer permissions needed
- But more limited functionality (may not support video uploads)

For video uploads, you really need **Instagram Graph API** with proper permissions.

---

## Need More Help?

If you're still stuck:

1. Check Meta's official docs: https://developers.facebook.com/docs/instagram-api/
2. Make sure your app is in Development mode (easier for testing)
3. Verify all permissions are granted during token generation
