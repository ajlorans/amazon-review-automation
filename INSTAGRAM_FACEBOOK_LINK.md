# Link Instagram Creator Account to Facebook Page

## Overview

Instagram Graph API requires a **Facebook Page** (not a personal profile). Since you have a basic Facebook account, you'll need to create a Page and link your Instagram Creator account to it.

## Step-by-Step Guide

### Step 1: Create a Facebook Page

1. **Go to Facebook Pages**: https://www.facebook.com/pages/create

   - Or go to: https://www.facebook.com → Click "Pages" in left sidebar → "Create New Page"

2. **Choose Page Type**:

   - Select **"Business or Brand"** (recommended)
   - Or **"Creator"** if you prefer

3. **Fill in Page Details**:

   - **Page Name**: Use your Instagram handle or brand name (e.g., "Your Instagram Name" or "Your Brand")
   - **Category**: Choose something relevant (e.g., "Content Creator", "Personal Blog", "Public Figure")
   - Click **"Create Page"**

4. **Optional Setup** (you can skip these for now):
   - Add profile picture
   - Add cover photo
   - Add description
   - You can do these later

### Step 2: Link Instagram to Your Facebook Page

**Method 1: From Facebook Page Settings (Recommended)**

1. **Go to your Facebook Page**:

   - Visit: https://www.facebook.com/pages/manage/
   - Or find your Page in the left sidebar of Facebook

2. **Open Page Settings**:

   - Click **"Settings"** in the left sidebar (or click the gear icon)

3. **Go to Instagram Section**:

   - In the left sidebar, click **"Instagram"**
   - If you don't see it, look for **"Linked Accounts"** or **"Instagram"** under Settings

4. **Connect Instagram**:
   - Click **"Connect Account"** or **"Link Instagram Account"**
   - You'll be prompted to log in to Instagram
   - Enter your Instagram username and password
   - Grant permissions to link the accounts
   - Click **"Confirm"**

**Method 2: From Instagram App**

1. **Open Instagram App** on your phone
2. **Go to Settings**:

   - Tap your profile picture (bottom right)
   - Tap the three lines (top right)
   - Tap **"Settings"**

3. **Go to Account**:

   - Tap **"Account"**
   - Tap **"Linked Accounts"** or **"Page"**

4. **Link Facebook Page**:
   - Tap **"Facebook"** or **"Page"**
   - If you see "Connect to Facebook", tap it
   - Select your **Facebook Page** (not your personal profile)
   - Confirm the connection

### Step 3: Verify the Connection

1. **Check on Facebook**:

   - Go to your Page → Settings → Instagram
   - You should see your Instagram account listed
   - It should show your Instagram username

2. **Check on Instagram**:
   - Go to Instagram Settings → Account → Linked Accounts
   - You should see your Facebook Page listed

### Step 4: Get Your Instagram Account ID

Once linked, get your Instagram Account ID:

1. **Go to Facebook Business Settings**:

   - Visit: https://business.facebook.com/settings
   - You may need to create a Business Account if you don't have one (it's free)

2. **Navigate to Instagram Accounts**:

   - In the left sidebar, click **"Instagram Accounts"**
   - You should see your Instagram account listed

3. **Copy the Account ID**:

   - Click on your Instagram account
   - The **Instagram Account ID** is a long number (like: 17841405309211844)
   - Copy this number

4. **Alternative: Get ID via API**:
   - If you can't find it in Business Settings, you can get it via Graph API Explorer after you have an access token

## Troubleshooting

### "I don't see Instagram option in Page Settings"

**Solution**:

- Make sure you're on the **Page** (not your personal profile)
- The URL should be: `facebook.com/YourPageName` or `facebook.com/pages/manage/`
- Try refreshing the page
- Make sure you're an Admin of the Page

### "I can't link my Instagram account"

**Possible causes**:

1. **Instagram account is Personal** (not Creator/Business)

   - Solution: Convert to Creator or Business account in Instagram Settings

2. **Instagram already linked to another Page**

   - Solution: Unlink it from the other Page first, then link to your new Page

3. **Permissions issue**
   - Solution: Make sure you're logged into both Facebook and Instagram with the same account (or accounts that have access)

### "I don't have a Business Account"

**Solution**:

- Go to: https://business.facebook.com/
- Click "Create Account" or "Get Started"
- It's free and just requires your Facebook account
- You can use it to manage your Page and Instagram

### "I can't find my Instagram Account ID"

**Alternative Method - Get ID via Graph API**:

1. First, get an access token (see Step 5 in INSTAGRAM_SETUP_FIX.md)
2. Use Graph API Explorer: https://developers.facebook.com/tools/explorer/
3. Make a GET request to: `me/accounts`
4. Find your Page in the response
5. Then make a GET request to: `{page_id}?fields=instagram_business_account`
6. The `id` field in the response is your Instagram Account ID

Or use this in your browser (replace ACCESS_TOKEN):

```
https://graph.facebook.com/v18.0/me/accounts?access_token=ACCESS_TOKEN
```

Then for each page:

```
https://graph.facebook.com/v18.0/{page_id}?fields=instagram_business_account&access_token=ACCESS_TOKEN
```

## Quick Checklist

- [ ] Created a Facebook Page
- [ ] Linked Instagram Creator account to the Facebook Page
- [ ] Verified connection in both Facebook and Instagram
- [ ] Got my Instagram Account ID
- [ ] Added Instagram Account ID to .env file

## Next Steps

After linking:

1. Go back to Meta Developer Dashboard
2. Try adding your Instagram account again
3. Generate your access token
4. Add both token and Account ID to your `.env` file

## Important Notes

- **You can use a simple Page name** - it doesn't have to be fancy, just needs to exist
- **The Page can be unpublished** - you don't need to make it public
- **You can have multiple Pages** - create one specifically for this purpose if needed
- **The link is reversible** - you can unlink and relink anytime
