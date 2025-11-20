# Instagram S3 Upload Error - Troubleshooting

## The Error

You're seeing: `[ERROR] Video processing failed: ERROR` after:

- ✅ Video uploaded to Google Drive (backup)
- ✅ Video uploaded to S3 successfully
- ✅ Container created in Instagram
- ❌ But Instagram returns ERROR when processing

## Quick Checks

### 0. Check Region Mismatch (Common Issue!)

**Problem**: URL shows wrong region (e.g., `us-east-1` but bucket is in `us-east-2`).

**Solution**:

1. Check your bucket's actual region in S3 console
2. Update `.env` file: `AWS_REGION=us-east-2` (use your bucket's region)
3. **The code now auto-detects the bucket region**, but having it correct in .env helps

**Note**: The code will automatically detect and use the correct region, but if you see region mismatch errors, update your `.env` file.

### 1. Check S3 Bucket Policy

**Problem**: S3 bucket might not be publicly accessible.

**Solution**:

1. Go to: https://s3.console.aws.amazon.com/
2. Click your bucket: `rolands-reviews-instagram-videos`
3. Go to **"Permissions"** tab
4. Check **"Bucket policy"** - should have this:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::rolands-reviews-instagram-videos/*"
    }
  ]
}
```

5. Check **"Block public access"** - should be **UNCHECKED** (all 4 settings)

### 2. Test S3 URL Manually

**Problem**: URL might not be accessible.

**Solution**:

1. Copy the S3 URL from the console output (looks like: `https://rolands-reviews-instagram-videos.s3.us-east-1.amazonaws.com/...`)
2. Paste it in a **new incognito/private browser window**
3. It should **download the video directly** (not show an error page)
4. If it shows "Access Denied" or similar, the bucket policy is wrong

### 3. Check Video Requirements

**Instagram Reels Requirements**:

- ✅ **Format**: MP4
- ✅ **Duration**: 15-90 seconds
- ✅ **File Size**: Max 100MB
- ✅ **Resolution**: At least 720p (yours are 1080p)
- ✅ **Aspect Ratio**: 9:16 (vertical) - your videos are already converted

The code now validates these automatically, but double-check your video meets these.

### 4. Check Instagram App

**Sometimes the video appears anyway!**

1. Open Instagram app
2. Go to your profile
3. Check for **drafts** or **scheduled posts**
4. The video might be there even if API reports error

### 5. Check Container Status in Instagram API

You can check the container status manually:

```bash
# Replace CONTAINER_ID with the ID from the error message
curl "https://graph.instagram.com/CONTAINER_ID?access_token=YOUR_ACCESS_TOKEN&fields=status_code,status,error"
```

## Common Issues & Solutions

### Issue: "Access Denied" when testing S3 URL

**Solution**:

- Verify bucket policy is correct (see #1 above)
- Make sure "Block all public access" is unchecked
- Wait a few minutes after changing bucket policy (AWS can be slow)

### Issue: Video too large or wrong duration

**Solution**:

- Check video file size: should be < 100MB
- Check video duration: should be 15-90 seconds
- Re-process the video if needed

### Issue: Instagram can't access S3 URL

**Possible causes**:

1. **Bucket policy not set correctly** - Most common issue
2. **Region mismatch** - Make sure URL region matches bucket region
3. **CORS issues** - Usually not needed for public buckets, but can add CORS policy if needed

**Solution**: Add CORS policy to bucket:

1. Go to bucket → **"Permissions"** tab
2. Scroll to **"Cross-origin resource sharing (CORS)"**
3. Click **"Edit"** and add:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

### Issue: Video format/codec not supported

**Solution**:

- Videos should be MP4 with H.264 codec
- Your processing script already converts to this format
- If issue persists, try re-processing the video

## Next Steps

1. **Run the upload again** - The improved error handling will now:

   - Test S3 URL accessibility automatically
   - Show more detailed error information
   - Provide specific troubleshooting steps

2. **Check the console output** - Look for:

   - `[OK] S3 URL is accessible` - Good sign
   - `[WARNING] S3 URL returned status XXX` - Problem with URL
   - File size and duration info

3. **If still failing**:
   - Check Instagram app for drafts (might be there anyway)
   - Verify bucket policy one more time
   - Try a different video to rule out video-specific issues
   - Check Instagram API status page for outages

## Still Not Working?

If none of the above works:

1. **Check Instagram API directly**:

   - Go to: https://developers.facebook.com/tools/explorer/
   - Use your access token
   - Query the container ID to see detailed error

2. **Try a smaller test video**:

   - Create a simple 20-second test video
   - Upload it to see if the issue is video-specific

3. **Contact support**:
   - Instagram Graph API: https://developers.facebook.com/support/
   - AWS S3: https://aws.amazon.com/support/

## What Changed

The code now:

- ✅ Tests S3 URL accessibility automatically
- ✅ Validates video file size and duration before upload
- ✅ Shows more detailed error information
- ✅ Provides specific troubleshooting steps based on error type

Run the upload again to see the improved error messages!
