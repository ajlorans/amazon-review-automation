# TikTok App Setup - What You Actually Need

## Quick Answer

**For personal use/testing, you can use minimal information and submit in "Development" or "Sandbox" mode.**

TikTok allows apps in development mode for testing, which has fewer requirements than production apps.

## Required vs Optional Fields

### ✅ **REQUIRED** (Must Fill Out):

- **App name** - Already filled: "Amazon-review-tiktok" ✓
- **Category** - Select any relevant category (e.g., "Content Management" or "Social Media Tools")
- **Description** - Brief description of what your app does
- **Terms of Service URL** - Can use a placeholder for testing
- **Privacy Policy URL** - Can use a placeholder for testing
- **Platforms** - Select at least one (probably "Web" or "Desktop")
- **App review explanation** - Explain how you'll use the Content Publishing API

### ❌ **OPTIONAL** (Can Skip or Use Placeholder):

- **App icon** - Can upload a simple icon or skip if allowed
- Detailed screenshots
- Video demos

## Recommended Approach for Personal Use

### Option 1: Minimal Setup (Recommended)

Fill out the form with minimal but valid information:

1. **App name**: `Amazon-review-tiktok` (you already have this)

2. **Category**: Select "Content Management" or "Social Media Tools"

3. **Description** (example):

   ```
   A desktop application that helps content creators automatically process and upload Amazon product review videos to TikTok. The app formats videos for TikTok and uploads them as drafts for review before publishing.
   ```

4. **Terms of Service URL**:

   - For testing, you can use a placeholder like:
   - `https://example.com/terms` (if you don't have one)
   - Or create a simple GitHub Pages site with basic terms
   - Or use a free service like: https://www.termsfeed.com/

5. **Privacy Policy URL**:

   - Similar to Terms of Service
   - Use a placeholder or create a simple one
   - Free generator: https://www.privacypolicygenerator.info/

6. **Platforms**:

   - Select **"Desktop"** (since you're running it on your computer)
   - Or **"Web"** if you prefer

7. **App review explanation** (example):

   ```
   This application uses the Content Publishing API to upload video content to TikTok.
   The app processes Amazon product review videos, formats them for TikTok (9:16 vertical format),
   and uploads them as drafts (privacy level: SELF_ONLY) so the creator can review before publishing.
   The app only accesses the user's own TikTok account and only uploads content that the user explicitly chooses to upload.
   ```

8. **App icon**:
   - Upload a simple icon (can be a basic image)
   - Or skip if the form allows it

### Option 2: Use Development/Sandbox Mode

1. Look for a **"Development"** or **"Sandbox"** mode option in your TikTok app settings
2. Development mode typically has fewer requirements
3. You can test the API without full app review
4. Once working, you can submit for review later if needed

## Important Notes

### For Personal Use:

- TikTok may allow apps in "Development" or "Testing" mode with minimal info
- You don't need a fully polished app for personal use
- The app review process is mainly for apps that will be used by others

### Terms of Service & Privacy Policy:

If you don't have URLs yet, you can:

1. **Quick Solution**: Create simple pages on GitHub Pages

   - Create a GitHub repo
   - Add basic terms.html and privacy.html files
   - Enable GitHub Pages
   - Use those URLs

2. **Free Generators**:

   - Terms: https://www.termsfeed.com/terms-generator/
   - Privacy: https://www.privacypolicygenerator.info/

3. **Placeholder** (for testing only):
   - Some developers use placeholder URLs during development
   - You'll need real ones for production/submission

## Submission Status

### Draft vs Submitted:

- **Draft**: You can save as draft and test if TikTok allows it
- **Submitted for Review**: Required for production use, but may work in development mode first

### Development Mode:

- Check if there's a "Development" or "Sandbox" toggle in your app settings
- Development mode usually allows API access without full review
- Perfect for personal use and testing

## Step-by-Step: What to Do Now

1. **Fill out the minimum required fields** with the information above
2. **Look for "Development Mode" or "Sandbox" option** - use that if available
3. **Save as draft** if you can't submit yet
4. **Try to get your Client Key and Secret** - sometimes you can get these even in draft mode
5. **Test the API** - if it works, you're good! If not, you may need to submit for review

## If You Get Stuck

If TikTok requires full submission before you can use the API:

1. Fill out all required fields (use the examples above)
2. Submit for review
3. TikTok will review your app (can take a few days to weeks)
4. Once approved, you can use the API

For personal use, TikTok is usually more lenient, so try the minimal approach first!

---

## Quick Checklist

- [ ] App name: "Amazon-review-tiktok" ✓
- [ ] Select a category
- [ ] Write a brief description
- [ ] Get/create Terms of Service URL (or placeholder)
- [ ] Get/create Privacy Policy URL (or placeholder)
- [ ] Select platform (Desktop or Web)
- [ ] Write app review explanation
- [ ] Upload app icon (or skip if allowed)
- [ ] Look for Development/Sandbox mode
- [ ] Save or submit
