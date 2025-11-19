# Amazon Review Video Automation

Automatically process and upload Amazon review videos to YouTube Shorts, Instagram Reels, and TikTok as drafts.

## 🎯 What This Project Does

1. **Processes Videos**: Converts any video to vertical 9:16 format (1080x1920) optimized for social media
2. **Adds CTA Overlay**: Automatically adds your Amazon creator link as a text overlay
3. **Generates Metadata**: Creates platform-specific titles, descriptions, and hashtags
4. **Uploads as Drafts**: Uploads videos to YouTube, Instagram, and TikTok as drafts so you can review before publishing

## 📁 Project Structure

```
amazon-review-automation/
├── process.py              # Main processing script
├── config.py               # Configuration and settings
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
├── storage/
│   ├── inputs/            # Place videos here to process
│   ├── outputs/           # Processed videos (organized by platform and date)
│   │   ├── youtube/
│   │   ├── instagram/
│   │   └── tiktok/
│   ├── archive/           # Source videos moved here after processing
│   ├── credentials/       # API credentials (YouTube client secrets, etc.)
│   ├── tokens/            # OAuth tokens (auto-generated)
│   └── logs/              # Processing logs
└── uploaders/             # Platform-specific uploaders
    ├── base_uploader.py
    ├── youtube_uploader.py
    ├── instagram_uploader.py
    └── tiktok_uploader.py
```

## 🚀 Quick Start

### 1. Install Dependencies

All dependencies are already installed! ✅

If you need to reinstall:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Your `.env` file is already set up. Make sure to update:

- `CREATOR_LINK`: Your Amazon Associates/Influencer store link
- Platform API credentials (see `UPLOAD_SETUP.md` for details)

### 3. Process a Video

**Single Video:**

```bash
python process.py --input storage/archive/amazon-review-labtop.mp4
```

**Batch Processing (all videos in `storage/inputs/`):**

```bash
python process.py --batch
```

**With Upload (after setting up API credentials):**

```bash
python process.py --input video.mp4 --upload
```

## 📝 Usage Examples

### Process a Single Video

```bash
# From inputs folder
python process.py --input my-video.mp4

# Full path
python process.py --input "C:/path/to/video.mp4"

# Without archiving source video
python process.py --input video.mp4 --no-archive
```

### Batch Processing

```bash
# Process all videos in storage/inputs/
python process.py --batch

# Process videos from custom folder
python process.py --batch --input-folder "C:/path/to/videos"
```

### Upload Videos

```bash
# Upload after processing (requires API setup)
python process.py --input video.mp4 --upload

# Skip upload even if enabled in .env
python process.py --input video.mp4 --no-upload
```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Required
CREATOR_LINK=https://amazon.com/shop/YOUR_CREATOR_NAME

# YouTube (required for YouTube uploads)
YOUTUBE_CLIENT_SECRETS_FILE=storage/credentials/youtube_client_secrets.json

# Instagram (optional, for Instagram uploads)
INSTAGRAM_ACCESS_TOKEN=your_token_here
INSTAGRAM_ACCOUNT_ID=your_account_id_here

# TikTok (optional, for TikTok uploads)
TIKTOK_CLIENT_KEY=your_key_here
TIKTOK_CLIENT_SECRET=your_secret_here
TIKTOK_ACCESS_TOKEN=your_token_here

# Upload Settings
AUTO_UPLOAD_ENABLED=false          # Set to true to auto-upload
UPLOAD_PRIVACY_STATUS=private      # "private" for drafts
UPLOAD_PLATFORMS=all               # "youtube,instagram,tiktok" or "all"
```

### Video Settings (in config.py)

- **Target Resolution**: 1080x1920 (9:16 vertical format)
- **Frame Rate**: 30fps
- **Max Duration**: 45 seconds (configurable)
- **CTA Overlay**: Bottom of video with your creator link

## 📤 Upload Setup

See `UPLOAD_SETUP.md` for detailed instructions on setting up API credentials for:

- YouTube Shorts
- Instagram Reels
- TikTok Videos

## 📊 Output Structure

Processed videos are saved in date-organized folders:

```
storage/outputs/
├── youtube/2025-11-13/
│   ├── video-name.mp4
│   └── video-name.json      # Metadata with title, description, hashtags
├── instagram/2025-11-13/
│   ├── video-name.mp4
│   └── video-name.json
└── tiktok/2025-11-13/
    ├── video-name.mp4
    └── video-name.json
```

Metadata JSON files contain:

- Title/Caption
- Description
- Hashtags
- Upload status (if uploaded)

## 🔧 How It Works

1. **Load Video**: Reads input video file
2. **Normalize**: Ensures consistent frame rate and audio
3. **Extract Segment**: Uses full video (or specified duration)
4. **Convert to Vertical**: Crops/resizes to 1080x1920 (9:16)
5. **Add CTA Overlay**: Adds text overlay with Amazon creator link
6. **Export**: Saves platform-specific versions
7. **Generate Metadata**: Creates titles, descriptions, hashtags
8. **Upload** (optional): Uploads to platforms as drafts

## 🐛 Troubleshooting

### Video Processing Issues

- **FFmpeg errors**: Make sure FFmpeg is installed and in PATH
- **Memory errors**: Try processing smaller videos or reduce resolution
- **Import errors**: Run `pip install -r requirements.txt`

### Upload Issues

- **YouTube**: Check `storage/tokens/youtube_token.json` - delete if expired
- **Instagram**: Verify access token is long-lived (60 days)
- **TikTok**: Complete OAuth2 flow to get fresh access token

See `UPLOAD_SETUP.md` for platform-specific troubleshooting.

## 📋 Requirements

- Python 3.11+ ✅ (You have 3.11.9)
- FFmpeg (for video processing)
- API credentials for platforms you want to upload to

## 📚 Files

- `process.py`: Main processing pipeline
- `config.py`: Configuration and settings
- `uploaders/`: Platform-specific upload implementations
- `UPLOAD_SETUP.md`: Detailed upload setup guide

## 🔒 Security Notes

- Never commit `.env` file or credential files to git
- Store tokens securely
- Rotate API tokens regularly
- The `.gitignore` already excludes sensitive files

## 🎬 Next Steps

1. Update `CREATOR_LINK` in `.env` with your Amazon store link
2. Place a test video in `storage/inputs/`
3. Run: `python process.py --batch`
4. Check `storage/outputs/` for processed videos
5. Set up API credentials (see `UPLOAD_SETUP.md`) to enable uploads

---

**Ready to process videos?** Place them in `storage/inputs/` and run `python process.py --batch`!
