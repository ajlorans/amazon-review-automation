# Fix: "Insufficient Developer Role" Error

## The Problem

Even after linking Instagram to your Facebook Page, you're still getting "Insufficient Developer Role" when trying to add your Instagram account in the Developer App.

**This means:** The issue is with your **role in the Facebook App**, not the Instagram linking.

## Solution: Check and Fix Your App Role

### Step 1: Verify You're the App Owner/Admin

1. **Go to Meta for Developers**: https://developers.facebook.com/
2. **Select your App** from the list
3. **Go to Settings** → **Roles** (or **App Roles**)
4. **Check your role**:
   - Look for your name/email in the list
   - You need to be **"Admin"** or **"Developer"**
   - If you're listed as "Tester" or "Analyst", that's the problem!

### Step 2: If You're Not Listed or Wrong Role

**Option A: You Created the App**

- You should automatically be Admin
- If not, there might be an issue with the app creation
- **Solution**: Create a new app (see Step 3)

**Option B: Someone Else Created the App**

- Ask them to add you as Admin/Developer
- They go to: App Settings → Roles → Add People
- Enter your email and select **"Admin"** role
- You'll get an email invitation

**Option C: You Can't Access Roles**

- The app might be in a weird state
- **Solution**: Create a new app (see Step 3)

### Step 3: Create a New App (Recommended if Current App Doesn't Work)

If you can't fix the role issue, create a fresh app:

1. **Go to**: https://developers.facebook.com/apps/
2. **Click "Create App"**
3. **Choose App Type**:
   - Select **"Business"** (recommended for Instagram API)
   - Click **"Next"**
4. **Fill in App Details**:
   - **App Name**: e.g., "Amazon Review Video Uploader"
   - **App Contact Email**: Your email
   - **Business Account**: Select or create one
   - Click **"Create App"**
5. **Add Instagram Product**:
   - You'll see a dashboard
   - Find **"Instagram"** in the products list
   - Click **"Set Up"** or **"Get Started"**
   - Select **"Instagram Graph API"**
6. **You're Now Admin!**
   - As the creator, you're automatically Admin
   - Go to Settings → Roles to verify

### Step 4: Add Instagram Account (After Fixing Role)

Once you have Admin/Developer role:

1. **Go to your App Dashboard**
2. **Find "Instagram" product** (should be added)
3. **Click on "Instagram"** in the left sidebar
4. **Go to "Basic Display" or "Graph API"** section
5. **Try adding your Instagram account again**

**Alternative Method - Use Graph API Explorer:**

1. **Go to**: https://developers.facebook.com/tools/explorer/
2. **Select your App** from the dropdown (top left)
3. **Click "Generate Access Token"**
4. **Select Permissions**:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts` (if available)
5. **Generate Token**
6. **Extend Token**:
   - Click the **"i"** icon next to the token
   - Click **"Open in Access Token Tool"**
   - Click **"Extend Access Token"** to get 60-day token
7. **Copy the token** - this is your `INSTAGRAM_ACCESS_TOKEN`

### Step 5: Get Instagram Account ID

1. **Go to**: https://business.facebook.com/settings
2. **Click "Instagram Accounts"** in left sidebar
3. **Find your account** and click on it
4. **Copy the Account ID** (long number)

### Step 6: Update .env File

Add to your `.env`:

```env
INSTAGRAM_ACCESS_TOKEN=your_long_lived_token_here
INSTAGRAM_ACCOUNT_ID=your_account_id_here
```

## Quick Diagnostic Checklist

Run through these to find the issue:

- [ ] I can see "Roles" in my App Settings
- [ ] My email/name is listed in Roles
- [ ] My role is "Admin" or "Developer" (not Tester/Analyst)
- [ ] I created the app myself (or was added as Admin)
- [ ] My Instagram is linked to a Facebook Page
- [ ] Instagram Graph API product is added to my app

## Most Common Issues

### "I don't see Roles option"

- You might not have access to the app
- Try creating a new app

### "I'm listed as Tester"

- You need Admin or Developer role
- Ask the app owner to change your role
- Or create your own app

### "I created the app but still get the error"

- Try logging out and back into Meta for Developers
- Clear browser cache
- Make sure you're selecting the right app
- Try creating a new app

### "I can't add Instagram product"

- Make sure you selected "Business" type when creating app
- Some app types don't support Instagram API
- Create a new Business app if needed

## Why This Happens

The "Insufficient Developer Role" error means:

- Meta's API requires Admin/Developer role to manage Instagram accounts
- Testers and Analysts have read-only access
- This is a security feature to prevent unauthorized access

## Recommended Solution

**If you're still stuck, create a new app:**

1. It's quick (5 minutes)
2. You'll automatically be Admin
3. Fresh start with no permission issues
4. You can delete the old app later if needed

## After Fixing

Once you have the right role:

1. You should be able to add your Instagram account
2. Generate your access token
3. Get your Account ID
4. Add both to `.env` file
5. Test with: `python process.py --input video.mp4 --upload`
