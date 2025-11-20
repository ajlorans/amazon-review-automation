# AWS S3 Setup for Instagram Uploads

## Why AWS S3?

- ✅ **More reliable** than Google Drive for Instagram API
- ✅ **Free tier**: 5GB storage, 20,000 requests/month (first 12 months)
- ✅ **Direct download URLs** that Instagram can access
- ✅ **Automatic cleanup** after upload (optional)

## Step 1: Create AWS Account (Free)

1. Go to: https://aws.amazon.com/
2. Click **"Create an AWS Account"**
3. Follow the signup process (requires credit card, but free tier won't charge you)
4. Free tier includes:
   - 5GB S3 storage
   - 20,000 GET requests
   - 2,000 PUT requests
   - First 12 months free

## Step 2: Create S3 Bucket

1. Go to: https://s3.console.aws.amazon.com/
2. Click **"Create bucket"**
3. **Bucket name**: Choose a unique name (e.g., `your-name-instagram-videos`)
   - Must be globally unique
   - Use lowercase, numbers, hyphens only
4. **Region**: Choose closest to you (e.g., `us-east-1`)
5. **Object Ownership**: Select **"ACLs disabled (recommended)"** (default)
   - This is fine - we'll use bucket policy instead of ACLs
6. **Block Public Access**: **UNCHECK** this (we need public access for Instagram)
   - Uncheck "Block all public access"
   - Acknowledge the warning
7. **Bucket Versioning**: Leave disabled (default)
8. Click **"Create bucket"**

## Step 3: Configure Bucket for Public Access

1. Click on your bucket name
2. Go to **"Permissions"** tab
3. Scroll to **"Bucket policy"**
4. Click **"Edit"** and add this policy (replace `YOUR_BUCKET_NAME`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    }
  ]
}
```

5. Click **"Save changes"**

## Step 4: Create IAM User for API Access

1. Go to: https://console.aws.amazon.com/iam/
2. Click **"Users"** → **"Create user"**
3. **User name**: `instagram-uploader` (or any name)
4. **Access type**: Select **"Programmatic access"**
5. Click **"Next: Permissions"**
6. Click **"Attach existing policies directly"**
7. Search for and select: **"AmazonS3FullAccess"** (or create a more restricted policy)
8. Click **"Next"** → **"Create user"**
9. **IMPORTANT**: Copy these values (you won't see them again):
   - **Access Key ID**
   - **Secret Access Key**
   - Click **"Download .csv"** to save them

## Step 5: Add to .env File

Add these to your `.env` file:

```env
# AWS S3 for Instagram uploads
AWS_ACCESS_KEY_ID=your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_REGION=us-east-2
AWS_S3_BUCKET_NAME=your-bucket-name-here

# Note: The code will auto-detect the bucket's actual region,
# but it's good to set AWS_REGION to match your bucket's region

# Instagram storage preference (s3, google_drive, or direct)
INSTAGRAM_STORAGE_TYPE=s3

# Cleanup S3 files after Instagram upload (true/false)
INSTAGRAM_CLEANUP_S3=true
```

## Step 6: Install boto3

```bash
pip install boto3
```

## Step 7: Test It

```bash
python process.py --input storage/inputs/amazon-review-labtop.mp4 --upload
```

## How It Works

1. **Video from inputs folder** → Uploaded to AWS S3
2. **Made publicly accessible** → Gets public URL
3. **Public URL** → Used for Instagram upload
4. **After successful upload** → S3 file is automatically deleted (if cleanup enabled)

## Cost Estimate

**Free Tier (First 12 Months):**

- 5GB storage: FREE
- 20,000 GET requests: FREE
- 2,000 PUT requests: FREE

**After Free Tier:**

- Storage: ~$0.023 per GB/month
- Requests: ~$0.0004 per 1,000 requests
- **Very cheap** - probably <$1/month for typical use

## Cleanup

Files are automatically deleted from S3 after successful Instagram upload (if `INSTAGRAM_CLEANUP_S3=true`).

To keep files in S3, set:

```env
INSTAGRAM_CLEANUP_S3=false
```

## Troubleshooting

### "Bucket not found"

- Check bucket name in .env matches exactly
- Make sure bucket exists in the correct region

### "Access denied"

- Check IAM user has S3 permissions
- Verify bucket policy allows public read
- Check Block Public Access is disabled

### "Invalid credentials"

- Verify Access Key ID and Secret Access Key are correct
- Make sure there are no extra spaces in .env

## Security Notes

- **Never commit** `.env` file with AWS credentials
- IAM user should have minimal permissions (S3 only)
- Consider using IAM roles instead of access keys for better security

## Quick Checklist

- [ ] Created AWS account
- [ ] Created S3 bucket (public access enabled)
- [ ] Added bucket policy for public read
- [ ] Created IAM user with S3 access
- [ ] Copied Access Key ID and Secret Access Key
- [ ] Added credentials to .env file
- [ ] Installed boto3: `pip install boto3`
- [ ] Tested upload
