# TikTok App Requirements for Video Upload

## The Issue

You're seeing:

- ✅ Token shows `video.upload` in authorized scopes
- ❌ But actual upload API calls fail with "scope_not_authorized"

This is a common issue with TikTok's API.

## Possible Causes

### 1. App Status: Sandbox vs Production

**TikTok apps can be in two modes:**

- **Sandbox Mode** (Development):

  - Limited API access
  - May not support all scopes even if granted
  - Usually for testing with your own account only

- **Production Mode** (Approved):
  - Full API access
  - All scopes work as expected
  - Requires app review and approval

**Check your app status:**

1. Go to https://developers.tiktok.com/
2. Open your app
3. Check the app status (Sandbox, In Review, Approved, etc.)

### 2. Content Publishing API Not Fully Enabled

Even if you enabled "Content Publishing API" in your app settings, TikTok might require:

- App to be submitted for review
- Additional permissions/approvals
- App to be out of Sandbox mode

### 3. Token Scope vs API Access

TikTok may show `video.upload` in the scope list, but the actual API endpoint might require:

- App approval
- Additional permissions
- Specific app configuration

## Solutions

### Solution 1: Check App Status

1. Go to https://developers.tiktok.com/
2. Open your app
3. Check:
   - Is it in "Sandbox" mode?
   - Is it "In Review"?
   - Is it "Approved"?

**If in Sandbox:**

- You may need to submit the app for review
- Or wait for TikTok to enable full access
- Some APIs don't work in Sandbox mode

### Solution 2: Verify App Configuration

1. In your TikTok app settings, check:

   - ✅ "Content Publishing API" is enabled
   - ✅ App is not in draft mode
   - ✅ All required fields are filled out

2. Check "Products" or "APIs" section:
   - Make sure "Content Publishing" is enabled
   - Check if there are any warnings or requirements

### Solution 3: Re-check Token

Run the improved check script:

```bash
python check_tiktok_token.py
```

This will show:

- The actual error message from TikTok
- More details about what's failing
- Suggestions based on the error

### Solution 4: Try Different Privacy Level

Sometimes TikTok's API is picky about privacy levels. Try modifying the upload to use:

- `PUBLIC_TO_EVERYONE` instead of `SELF_ONLY`
- Or check if your app allows draft uploads

### Solution 5: Contact TikTok Support

If none of the above works:

1. Check TikTok Developer Forums
2. Contact TikTok Developer Support
3. Check if there are known issues with Content Publishing API

## Testing Steps

1. **Check app status:**

   - Go to https://developers.tiktok.com/
   - Check if app is Sandbox or Approved

2. **Run detailed check:**

   ```bash
   python check_tiktok_token.py
   ```

   - Look at the full error message
   - Check the error code

3. **Check app configuration:**

   - Content Publishing API enabled?
   - App submitted for review?
   - All required fields filled?

4. **Try re-authorizing:**
   ```bash
   python auth_tiktok.py
   ```
   - Make sure to grant ALL permissions
   - Check all permission boxes

## Common Error Messages

### "scope_not_authorized"

- Token doesn't have the scope (even if listed)
- App may not be approved
- API may not be fully enabled

### "insufficient_permissions"

- App needs to be approved
- Additional permissions required

### "app_not_approved"

- App is in Sandbox or pending review
- Need to submit for review

## Next Steps

1. Run `python check_tiktok_token.py` to see the full error
2. Check your app status at https://developers.tiktok.com/
3. If app is in Sandbox, consider submitting for review
4. Check TikTok Developer documentation for latest requirements
