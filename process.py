"""
Main CLI tool for processing Amazon review videos.

Usage:
    python process.py --input path/to/video.mp4

This script:
1. Normalizes the input video
2. Exports YouTube videos in original format (landscape, full length)
3. Converts Instagram videos to vertical 9:16 format (1080x1920, full length)
4. Converts TikTok videos to vertical 9:16 format (1080x1920, full length)
5. Adds CTA overlay with Amazon creator link (currently disabled)
6. Exports to platform-specific folders
7. Generates metadata files for each platform
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
import config

# Import uploaders (optional - only if upload is enabled)
try:
    from uploaders import YouTubeUploader, InstagramUploader, TikTokUploader
    UPLOADERS_AVAILABLE = True
except ImportError:
    UPLOADERS_AVAILABLE = False


def normalize_video(clip: VideoFileClip) -> VideoFileClip:
    """
    Normalize the input video and fix VFR (Variable Frame Rate) issues.
    
    Phone videos often have Variable Frame Rate, which causes audio-video sync issues.
    This function converts VFR to CFR (Constant Frame Rate) while preserving the original
    frame rate, ensuring audio stays in sync.
    
    Args:
        clip: Input video clip
        
    Returns:
        Normalized video clip with constant frame rate and synced audio
    """
    original_fps = clip.fps
    
    # Phone videos are often VFR (Variable Frame Rate)
    # Convert to CFR (Constant Frame Rate) to fix sync issues
    # Use set_fps with change_duration=False to preserve audio sync
    print(f"  Original FPS: {original_fps:.2f}")
    
    # Round to nearest common frame rate (23.976, 24, 25, 29.97, 30, 60)
    # This handles slight variations in phone recordings
    common_fps = [23.976, 24, 25, 29.97, 30, 60]
    target_fps = min(common_fps, key=lambda x: abs(x - original_fps))
    
    # If close to a common FPS, use that; otherwise use the original
    if abs(original_fps - target_fps) < 0.5:
        normalized_fps = target_fps
    else:
        # Use original FPS, rounded to 2 decimals
        normalized_fps = round(original_fps, 2)
    
    # Convert VFR to CFR while preserving audio sync
    # change_duration=False ensures audio timing stays correct
    if abs(clip.fps - normalized_fps) > 0.01:  # Only convert if significantly different
        print(f"  Converting VFR to CFR: {original_fps:.2f} → {normalized_fps:.2f} fps")
        clip = clip.set_fps(normalized_fps, change_duration=False)
        print(f"  [OK] Frame rate normalized (audio sync preserved)")
    else:
        print(f"  [OK] Frame rate is already constant ({normalized_fps:.2f} fps)")
    
    # Ensure audio is present and properly synced
    if clip.audio is None:
        print("  Warning: Input video has no audio track.")
    else:
        # Explicitly ensure audio is set to match video duration
        # This prevents audio drift during processing
        if abs(clip.audio.duration - clip.duration) > 0.1:
            print(f"  Warning: Audio duration ({clip.audio.duration:.2f}s) doesn't match video ({clip.duration:.2f}s)")
            print(f"  Adjusting audio to match video duration...")
            clip = clip.set_audio(clip.audio.set_duration(clip.duration))
    
    return clip


def extract_clip_segment(clip: VideoFileClip, start_time: float = None, 
                         duration: float = None) -> VideoFileClip:
    """
    Extract a segment from the video.
    
    For MVP, if no times are specified, use the whole video.
    If duration is specified, extract from start_time.
    
    Args:
        clip: Input video clip
        start_time: Start time in seconds (default: 0)
        duration: Duration in seconds (default: full video)
        
    Returns:
        Extracted video segment
    """
    if start_time is None:
        start_time = 0
    
    if duration is None:
        # Use whole video, but limit to max duration
        max_duration = min(clip.duration, config.DEFAULT_CLIP_DURATION_MAX)
        duration = max_duration
    
    # Ensure we don't exceed video length
    end_time = min(start_time + duration, clip.duration)
    duration = end_time - start_time
    
    # MoviePy 2.x uses slicing syntax instead of subclip()
    return clip[start_time:end_time]


def convert_to_vertical(clip: VideoFileClip) -> VideoFileClip:
    """
    Convert video to vertical 9:16 format (1080x1920).
    
    Strategy: Scale to fit (minimizes cropping and zoom)
    - Scales video to fit within target dimensions while maintaining aspect ratio
    - Adds letterboxing/pillarboxing if needed (black bars)
    - This prevents important content from being cropped out
    
    Args:
        clip: Input video clip
        
    Returns:
        Vertical video clip (1080x1920)
    """
    target_width = config.TARGET_WIDTH
    target_height = config.TARGET_HEIGHT
    target_aspect = target_width / target_height  # 9:16 = 0.5625
    
    current_width = clip.w
    current_height = clip.h
    current_aspect = current_width / current_height
    
    # Calculate scale factor to fit video within target dimensions
    # We want to scale so the video fits completely within the target frame
    scale_by_width = target_width / current_width
    scale_by_height = target_height / current_height
    
    # Use the smaller scale factor to ensure video fits completely
    scale_factor = min(scale_by_width, scale_by_height)
    
    # Calculate new dimensions after scaling
    new_width = int(current_width * scale_factor)
    new_height = int(current_height * scale_factor)
    
    # Resize video (this will fit within target dimensions)
    scaled_clip = clip.resized(new_size=(new_width, new_height))
    
    # Create a black background at target size
    background = ColorClip(size=(target_width, target_height), color=(0, 0, 0), duration=clip.duration)
    
    # Center the scaled video on the black background
    # Calculate position to center the video
    x_center = (target_width - new_width) // 2
    y_center = (target_height - new_height) // 2
    
    # Composite the scaled video on the background
    final_clip = CompositeVideoClip(
        [background, scaled_clip.with_position((x_center, y_center))],
        size=(target_width, target_height)
    )
    
    return final_clip


def add_cta_overlay(clip: VideoFileClip) -> CompositeVideoClip:
    """
    Add CTA text overlay to the video.
    
    Args:
        clip: Input video clip
        
    Returns:
        Video clip with CTA overlay
    """
    # Create text clip for CTA (MoviePy 2.x uses font_size instead of fontsize)
    txt_clip = TextClip(
        text=config.CTA_TEXT,
        font_size=config.CTA_FONT_SIZE,
        color=config.CTA_TEXT_COLOR,
        bg_color=config.CTA_BACKGROUND_COLOR,
        size=(clip.w, None),  # Full width
        method='caption'  # Auto-wrap text
    ).with_duration(clip.duration)  # MoviePy 2.x uses with_duration()
    
    # Position at bottom (MoviePy 2.x uses with_position())
    if config.CTA_POSITION == "bottom":
        txt_clip = txt_clip.with_position(('center', 'bottom'))
    elif config.CTA_POSITION == "top":
        txt_clip = txt_clip.with_position(('center', 'top'))
    else:
        txt_clip = txt_clip.with_position('center')
    
    # Set opacity (MoviePy 2.x uses with_opacity())
    txt_clip = txt_clip.with_opacity(config.CTA_OPACITY)
    
    # Composite text over video
    final_clip = CompositeVideoClip([clip, txt_clip])
    
    return final_clip


def calculate_instagram_bitrate(duration_seconds: float, target_size_mb: float = 95.0) -> str:
    """
    Calculate optimal bitrate for Instagram to stay under file size limit.
    
    Instagram Reels limit: 100MB
    Formula: file_size_mb = (video_bitrate_mbps * duration + audio_bitrate_mbps * duration) / 8
    
    Args:
        duration_seconds: Video duration in seconds
        target_size_mb: Target file size in MB (default 95MB to leave margin)
        
    Returns:
        Bitrate string in format "XXXXk" (e.g., "5000k")
    """
    # Audio bitrate is typically 192k = 0.192 Mbps
    audio_bitrate_mbps = 0.192
    
    # Calculate maximum video bitrate to stay under target size
    # file_size_mb = (video_bitrate_mbps * duration + audio_bitrate_mbps * duration) / 8
    # Solving for video_bitrate_mbps:
    # video_bitrate_mbps = (target_size_mb * 8 - audio_bitrate_mbps * duration) / duration
    # video_bitrate_mbps = (target_size_mb * 8) / duration - audio_bitrate_mbps
    
    if duration_seconds <= 0:
        duration_seconds = 1  # Prevent division by zero
    
    max_video_bitrate_mbps = (target_size_mb * 8) / duration_seconds - audio_bitrate_mbps
    
    # Convert to kbps and round down to nearest 100
    max_video_bitrate_kbps = int(max_video_bitrate_mbps * 1000)
    max_video_bitrate_kbps = (max_video_bitrate_kbps // 100) * 100  # Round down to nearest 100
    
    # Set minimum bitrate for quality to prevent lag
    # Higher minimum ensures smoother playback even for longer videos
    min_bitrate_kbps = 2500  # 2.5 Mbps minimum for smooth playback
    # Set maximum bitrate for quality (max 8 Mbps = 8000k for smooth playback)
    max_bitrate_kbps = 8000
    
    # For very long videos, we need to balance file size vs quality
    # Use a more aggressive target size if needed, but prioritize quality
    if max_video_bitrate_kbps < min_bitrate_kbps:
        # Video would be too long for minimum bitrate - need to balance
        # Check if using minimum bitrate would exceed 100MB
        min_bitrate_size_mb = (min_bitrate_kbps / 1000 + audio_bitrate_mbps) * duration_seconds / 8
        
        if min_bitrate_size_mb <= 100:
            # Can use minimum bitrate without exceeding 100MB
            optimal_bitrate_kbps = min_bitrate_kbps
        elif duration_seconds > 300:  # Over 5 minutes
            # Very long video - use lower target but maintain reasonable quality
            # Use 85MB target for very long videos
            max_video_bitrate_mbps = (85.0 * 8) / duration_seconds - audio_bitrate_mbps
            max_video_bitrate_kbps = int(max_video_bitrate_mbps * 1000)
            max_video_bitrate_kbps = (max_video_bitrate_kbps // 100) * 100
            # Maintain minimum of 2000k for quality (prevents lag)
            optimal_bitrate_kbps = max(2000, min(max_bitrate_kbps, max_video_bitrate_kbps))
        else:
            # Moderately long video (2-5 min) - use calculated bitrate
            # This ensures we stay under 100MB while maintaining quality
            optimal_bitrate_kbps = max(2000, max_video_bitrate_kbps)  # Minimum 2000k for quality
    else:
        # Normal video - clamp between min and max
        optimal_bitrate_kbps = min(max_bitrate_kbps, max(max_video_bitrate_kbps, min_bitrate_kbps))
    
    return f"{optimal_bitrate_kbps}k"


def export_video(clip: CompositeVideoClip, output_path: Path, platform: str):
    """
    Export video to specified path with optimized settings.
    
    Args:
        clip: Video clip to export
        output_path: Output file path
        platform: Platform name (for logging)
    """
    print(f"Exporting {platform} video to {output_path}...")
    
    # Platform-specific encoding settings
    if platform == "instagram":
        # Instagram: Dynamic bitrate to stay under 100MB limit
        # Calculate optimal bitrate based on video duration
        duration = clip.duration
        bitrate = calculate_instagram_bitrate(duration)
        estimated_size_mb = (float(bitrate[:-1]) / 1000 + 0.192) * duration / 8
        print(f"  Video duration: {duration:.1f}s")
        print(f"  Calculated bitrate: {bitrate} (estimated size: {estimated_size_mb:.1f}MB)")
        audio_bitrate = "192k"
        preset = "medium"  # Better quality encoding (slightly slower but smoother)
    elif platform == "tiktok":
        # TikTok: Similar to Instagram, but TikTok allows larger files
        # Still optimize to keep reasonable file sizes
        duration = clip.duration
        # TikTok allows up to 287MB, but we'll use similar optimization
        bitrate = calculate_instagram_bitrate(duration, target_size_mb=200.0)  # More lenient
        audio_bitrate = "192k"
        preset = "medium"  # Better quality encoding
    else:  # youtube
        # YouTube: Can use faster preset since it's landscape (less processing)
        # YouTube allows much larger files, so we can use higher bitrate
        bitrate = "10000k"  # 10 Mbps for landscape
        audio_bitrate = "192k"
        preset = "fast"
    
    # Use more threads for faster encoding (auto-detect or use more)
    import multiprocessing
    num_threads = min(multiprocessing.cpu_count(), 8)  # Use up to 8 threads
    
    # Build FFmpeg parameters
    ffmpeg_params = [
        '-movflags', '+faststart',  # Enable fast start for web playback
        '-pix_fmt', 'yuv420p',  # Ensure compatibility
        '-profile:v', 'high',  # Use high profile for better quality
        '-level', '4.0',  # H.264 level 4.0 for compatibility
        '-g', '30',  # Keyframe interval (1 keyframe per second at 30fps)
        '-bf', '2',  # B-frames for better compression
        '-b_strategy', '1',  # Adaptive B-frame placement
    ]
    
    # Add Instagram and TikTok-specific optimizations for smoother playback
    if platform in ["instagram", "tiktok"]:
        ffmpeg_params.extend([
            '-rc-lookahead', '30',  # Lookahead for better quality
            '-refs', '3',  # Reference frames for better quality
            '-trellis', '1',  # Trellis quantization for better quality
        ])
    
    # Use the clip's actual FPS instead of forcing 30fps
    # This preserves the original frame rate and prevents sync issues
    output_fps = clip.fps
    if output_fps is None or output_fps <= 0:
        output_fps = 30  # Fallback to 30fps if FPS is invalid
        print(f"  Warning: Invalid FPS, using 30fps as fallback")
    else:
        print(f"  Using source frame rate: {output_fps:.2f} fps")
    
    # Update keyframe interval to match frame rate (1 keyframe per second)
    # Remove the old '-g' parameter and add a new one based on actual FPS
    ffmpeg_params = [p for p in ffmpeg_params if p != '-g']
    keyframe_interval = int(output_fps)  # 1 keyframe per second
    ffmpeg_params.append('-g')
    ffmpeg_params.append(str(keyframe_interval))
    
    # Add audio sync parameters to prevent drift
    ffmpeg_params.extend([
        '-async', '1',  # Audio sync method
        '-vsync', 'cfr',  # Constant frame rate (ensures sync)
    ])
    
    clip.write_videofile(
        str(output_path),
        codec='libx264',
        audio_codec='aac',
        fps=output_fps,  # Use actual FPS instead of forcing 30
        preset=preset,
        bitrate=bitrate,
        audio_bitrate=audio_bitrate,
        threads=num_threads,
        ffmpeg_params=ffmpeg_params,
        audio_nbytes=4,  # 32-bit audio for better quality
        audio_fps=44100  # Standard audio sample rate
    )
    
    # Verify file size for Instagram and re-encode if needed
    if platform == "instagram":
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  Actual file size: {file_size_mb:.1f}MB")
        
        if file_size_mb > 100:
            print(f"  [WARNING] File size ({file_size_mb:.1f}MB) exceeds 100MB limit!")
            print(f"  Re-encoding with lower bitrate to fit under 100MB...")
            
            # Calculate new bitrate to get under 100MB
            # Use 90MB as target to leave margin
            new_bitrate = calculate_instagram_bitrate(clip.duration, target_size_mb=90.0)
            print(f"  New bitrate: {new_bitrate}")
            
            # Re-encode with lower bitrate (use same optimized settings)
            # Use the same FPS and sync settings as the original encode
            reencode_fps = clip.fps if clip.fps and clip.fps > 0 else 30
            keyframe_interval = int(reencode_fps)
            
            ffmpeg_params = [
                '-movflags', '+faststart',
                '-pix_fmt', 'yuv420p',
                '-profile:v', 'high',
                '-level', '4.0',
                '-g', str(keyframe_interval),
                '-bf', '2',
                '-b_strategy', '1',
                '-rc-lookahead', '30',
                '-refs', '3',
                '-trellis', '1',
                '-async', '1',  # Audio sync
                '-vsync', 'cfr',  # Constant frame rate
            ]
            
            clip.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=reencode_fps,  # Use actual FPS
                preset=preset,
                bitrate=new_bitrate,
                audio_bitrate=audio_bitrate,
                threads=num_threads,
                ffmpeg_params=ffmpeg_params,
                audio_nbytes=4,
                audio_fps=44100,
                overwrite=True  # Overwrite the existing file
            )
            
            # Check again
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"  New file size: {file_size_mb:.1f}MB")
            
            if file_size_mb > 100:
                print(f"  [ERROR] File still too large ({file_size_mb:.1f}MB) after re-encoding!")
                print(f"  [ERROR] Video may be too long. Consider splitting into shorter segments.")
            else:
                print(f"  [OK] File size now under 100MB limit")
        else:
            print(f"  [OK] File size under 100MB limit")
    
    print(f"[OK] {platform} video exported successfully!")


def extract_amazon_link(video_path: Path) -> str:
    """
    Extract Amazon product link from video filename or associated files.
    
    Supports multiple methods:
    1. Filename format: video-name_https-amazon-com-dp-12345.mp4
    2. Sidecar file: video-name.amazon or video-name.link
    3. JSON mapping file: storage/inputs/video_links.json
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Amazon product link, or empty string if not found
    """
    video_name = video_path.stem
    video_dir = video_path.parent
    
    # Method 1: Check filename for Amazon link
    # Format: video-name_https-amzn-to-3K7euOO.mp4 or video-name_https-amazon-com-dp-12345.mp4
    if '_https-' in video_name or '_http-' in video_name:
        # Extract the link part after the first underscore
        parts = video_name.split('_', 1)
        if len(parts) > 1:
            link_part = parts[1]
            amazon_link = link_part
            
            # Replace protocol pattern: https- -> https://
            if amazon_link.startswith('https-'):
                amazon_link = amazon_link.replace('https-', 'https://', 1)
            elif amazon_link.startswith('http-'):
                amazon_link = amazon_link.replace('http-', 'http://', 1)
            
            # Handle shortened Amazon links (amzn.to)
            # Pattern: https://amzn-to-3K7euOO -> https://amzn.to/3K7euOO
            if 'amzn-to-' in amazon_link:
                # Replace amzn-to- with amzn.to/
                amazon_link = amazon_link.replace('amzn-to-', 'amzn.to/')
            elif amazon_link.startswith('https://amzn-to') or amazon_link.startswith('http://amzn-to'):
                # Handle case where it's just amzn-to without the dash after
                amazon_link = amazon_link.replace('amzn-to', 'amzn.to', 1)
            
            # Handle full Amazon URLs
            # Replace domain pattern: amazon-com -> amazon.com
            amazon_link = amazon_link.replace('-com', '.com')
            amazon_link = amazon_link.replace('-co-uk', '.co.uk')
            amazon_link = amazon_link.replace('-ca', '.ca')
            amazon_link = amazon_link.replace('-de', '.de')
            
            # Replace path separators: dp-12345 -> dp/12345
            amazon_link = amazon_link.replace('-dp-', '/dp/')
            amazon_link = amazon_link.replace('-gp-product-', '/gp/product/')
            
            # Replace remaining hyphens with slashes for path segments
            # But be careful - only replace hyphens that are part of the path, not in the domain
            # Pattern: https://amzn.to/3K7euOO (already handled above)
            # Pattern: https://amazon.com/dp/B08XYZ-1234 -> https://amazon.com/dp/B08XYZ/1234 (wrong)
            # So we need to be smarter - only replace hyphens after the domain
            
            # For amzn.to links, the format is already correct after the above replacements
            # For full amazon.com links, we need to handle product IDs carefully
            
            # Validate it looks like an Amazon URL
            if ('amazon' in amazon_link.lower() or 'amzn.to' in amazon_link.lower()) and ('http://' in amazon_link or 'https://' in amazon_link):
                return amazon_link
    
    # Method 2: Check for sidecar files (.amazon or .link)
    for ext in ['.amazon', '.link', '.txt']:
        sidecar_file = video_dir / f"{video_name}{ext}"
        if sidecar_file.exists():
            try:
                with open(sidecar_file, 'r', encoding='utf-8') as f:
                    link = f.read().strip()
                    if link and 'amazon' in link.lower():
                        return link
            except Exception:
                pass
    
    # Method 3: Check JSON mapping file
    json_file = video_dir / "video_links.json"
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                links_map = json.load(f)
                # Try exact match first
                if video_name in links_map:
                    return links_map[video_name]
                # Try with extension
                if video_path.name in links_map:
                    return links_map[video_path.name]
        except Exception:
            pass
    
    # No link found
    return ""


def generate_metadata(video_name: str, platform: str, amazon_link: str = "") -> dict:
    """
    Generate metadata for a platform.
    
    Args:
        video_name: Name of the video (without extension)
        platform: Platform name ('youtube', 'instagram', 'tiktok')
        
    Returns:
        Dictionary with metadata
    """
    # Generate title from video name
    title = video_name.replace('_', ' ').replace('-', ' ').title()
    
    # Get platform-specific hashtags
    hashtags = config.DEFAULT_HASHTAGS.get(platform, [])
    
    # Generate platform-specific content
    if platform == "youtube":
        description = config.get_youtube_description(title, hashtags, amazon_link)
        metadata = {
            "title": title,
            "description": description,
            "hashtags": hashtags
        }
    elif platform == "instagram":
        caption = config.get_instagram_caption(title, hashtags, amazon_link)
        metadata = {
            "caption": caption,
            "hashtags": hashtags
        }
    elif platform == "tiktok":
        caption = config.get_tiktok_caption(title, hashtags, amazon_link)
        metadata = {
            "caption": caption,
            "hashtags": hashtags
        }
    else:
        metadata = {}
    
    return metadata


def save_metadata(metadata: dict, output_path: Path, platform: str):
    """
    Save metadata to JSON file.
    
    Args:
        metadata: Metadata dictionary
        output_path: Path where video was saved
        platform: Platform name
    """
    # Create metadata file path (same name as video, but .json)
    metadata_path = output_path.with_suffix('.json')
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] {platform} metadata saved to {metadata_path}")


def upload_videos(uploaded_videos: dict, video_name: str) -> dict:
    """
    Upload videos to social media platforms.
    
    Args:
        uploaded_videos: Dictionary with platform -> {path, metadata}
        video_name: Name of the video
        
    Returns:
        Dictionary with upload results per platform
    """
    results = {}
    
    # Initialize uploaders
    uploaders = {
        'youtube': YouTubeUploader() if 'youtube' in config.UPLOAD_PLATFORMS else None,
        'instagram': InstagramUploader() if 'instagram' in config.UPLOAD_PLATFORMS else None,
        'tiktok': TikTokUploader() if 'tiktok' in config.UPLOAD_PLATFORMS else None,
    }
    
    for platform in config.UPLOAD_PLATFORMS:
        if platform not in uploaded_videos:
            continue
        
        uploader = uploaders.get(platform)
        if not uploader:
            continue
        
        print(f"\nUploading to {platform.upper()}...")
        
        video_info = uploaded_videos[platform]
        video_path = video_info['path']
        metadata = video_info['metadata']
        
        # Extract title and description from metadata
        if platform == 'youtube':
            title = metadata.get('title', video_name)
            description = metadata.get('description', '')
            tags = metadata.get('hashtags', [])
        elif platform == 'instagram':
            title = video_name  # Instagram doesn't use titles
            description = metadata.get('caption', '')
            tags = metadata.get('hashtags', [])
        else:  # tiktok
            title = video_name
            description = metadata.get('caption', '')
            tags = metadata.get('hashtags', [])
        
        # Upload video
        result = uploader.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            privacy_status=config.UPLOAD_PRIVACY_STATUS
        )
        
        results[platform] = result
        
        if result:
            print(f"  [OK] {platform.upper()} upload successful!")
        else:
            print(f"  [FAILED] {platform.upper()} upload failed")
    
    return results


def log_processing(video_name: str, status: str, error: str = None):
    """
    Log processing status to a log file.
    
    Args:
        video_name: Name of the video file
        status: 'success' or 'failed'
        error: Error message if status is 'failed'
    """
    log_file = config.LOGS_FOLDER / f"processing_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {video_name}: {status}"
    if error:
        log_entry += f" - {error}"
    log_entry += "\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)


def archive_video(input_path: Path):
    """
    Move processed video to archive folder.
    
    Args:
        input_path: Path to the processed video file
    """
    try:
        archive_path = config.ARCHIVE_FOLDER / input_path.name
        # If file already exists in archive, add timestamp
        if archive_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = config.ARCHIVE_FOLDER / f"{input_path.stem}_{timestamp}{input_path.suffix}"
        
        shutil.move(str(input_path), str(archive_path))
        print(f"  Archived to: {archive_path.name}")
    except Exception as e:
        print(f"  Warning: Could not archive video: {e}")


def process_video(input_path: Path, archive: bool = True) -> bool:
    """
    Main processing pipeline.
    
    Args:
        input_path: Path to input video file
        archive: Whether to archive the video after successful processing
        
    Returns:
        True if processing succeeded, False otherwise
    """
    video_name = input_path.stem
    clip = None
    instagram_clip = None
    tiktok_clip = None
    final_clip = None
    
    try:
        print(f"\n{'='*60}")
        print(f"Processing: {input_path.name}")
        print(f"{'='*60}\n")
        
        # Step 1: Load video
        print("Step 1: Loading video...")
        clip = VideoFileClip(str(input_path))
        print(f"  Original: {clip.w}x{clip.h}, {clip.duration:.2f}s, {clip.fps}fps")
        
        # Step 2: Normalize
        print("\nStep 2: Normalizing video...")
        clip = normalize_video(clip)
        
        # Step 3: Prepare clips for different platforms
        print("\nStep 3: Preparing clips for platforms...")
        
        # YouTube: Keep original landscape format (full length, no duration limit)
        youtube_clip = clip
        print(f"  YouTube: {youtube_clip.w}x{youtube_clip.h}, {youtube_clip.duration:.2f}s (original format, full length)")
        
        # Instagram: Full length, convert to vertical format
        print("\nStep 4: Preparing Instagram clip...")
        print("  Converting to vertical format (1080x1920) - full length...")
        instagram_clip = convert_to_vertical(clip)
        print(f"  Instagram: {instagram_clip.w}x{instagram_clip.h}, {instagram_clip.duration:.2f}s (vertical, full length)")
        
        # TikTok: Full length, convert to vertical format
        print("\nStep 5: Preparing TikTok clip...")
        print("  Converting to vertical format (1080x1920) - full length...")
        tiktok_clip = convert_to_vertical(clip)
        print(f"  TikTok: {tiktok_clip.w}x{tiktok_clip.h}, {tiktok_clip.duration:.2f}s (vertical, full length)")
        
        # Step 6: Add CTA overlay (disabled - no overlay on videos)
        print("\nStep 6: Skipping CTA overlay...")
        
        # Step 7: Extract Amazon link (once, before processing platforms)
        print("\nStep 7: Extracting Amazon product link...")
        amazon_link = extract_amazon_link(input_path)
        if amazon_link:
            print(f"  Found Amazon link: {amazon_link}")
        else:
            print(f"  No Amazon link found, using general creator link")
        
        # Step 8: Export for each platform (using date-based folders)
        print("\nStep 8: Exporting videos...")
        date_folder = datetime.now().strftime("%Y-%m-%d")
        
        uploaded_videos = {}  # Store upload results
        
        # Only process platforms that are enabled in UPLOAD_PLATFORMS
        # If upload is disabled, process all platforms (for manual review)
        platforms_to_process = config.UPLOAD_PLATFORMS if config.AUTO_UPLOAD_ENABLED else ["youtube", "instagram", "tiktok"]
        
        print(f"\nProcessing videos for platforms: {', '.join(platforms_to_process)}")
        
        for platform in platforms_to_process:
            output_folder = config.get_output_folder(platform, date_folder)
            output_path = output_folder / f"{video_name}.mp4"
            
            # Choose the appropriate clip for each platform
            if platform == "youtube":
                # YouTube: Use original landscape format (full length)
                platform_clip = youtube_clip
            elif platform == "instagram":
                # Instagram: Use full-length vertical format
                platform_clip = instagram_clip
            else:  # tiktok
                # TikTok: Use full-length vertical format
                platform_clip = tiktok_clip
            
            # Export video
            export_video(platform_clip, output_path, platform)
            
            # Generate and save metadata
            metadata = generate_metadata(video_name, platform, amazon_link)
            save_metadata(metadata, output_path, platform)
            
            # Store metadata for upload step
            uploaded_videos[platform] = {
                'path': output_path,
                'metadata': metadata
            }
        
        # Cleanup
        print("\nCleaning up...")
        if clip:
            clip.close()
        if instagram_clip:
            instagram_clip.close()
        if tiktok_clip:
            tiktok_clip.close()
        # Note: youtube_clip is just a reference to clip, so no need to close separately
        
        # Step 9: Upload to platforms (if enabled)
        if config.AUTO_UPLOAD_ENABLED and UPLOADERS_AVAILABLE:
            print(f"\n{'='*60}")
            print("Step 9: Uploading videos to platforms...")
            print(f"{'='*60}")
            print(f"Configured platforms: {', '.join(config.UPLOAD_PLATFORMS)}")
            print(f"{'='*60}\n")
            
            upload_results = upload_videos(uploaded_videos, video_name)
            
            # Save upload results to metadata
            for platform, result in upload_results.items():
                if result:
                    metadata_path = uploaded_videos[platform]['path'].with_suffix('.json')
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    metadata['upload'] = result
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
        elif config.AUTO_UPLOAD_ENABLED and not UPLOADERS_AVAILABLE:
            print("\nWarning: Upload enabled but uploaders not available")
            print("  Install required packages: pip install -r requirements.txt")
        
        # Archive the video if requested
        if archive:
            print("\nArchiving source video...")
            archive_video(input_path)
        
        print(f"\n{'='*60}")
        print("[OK] Processing complete!")
        print(f"{'='*60}\n")
        
        log_processing(video_name, "success")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n{'='*60}")
        print(f"[ERROR] Processing failed: {error_msg}")
        print(f"{'='*60}\n")
        
        # Cleanup on error
        try:
            if clip:
                clip.close()
            if 'instagram_clip' in locals() and instagram_clip:
                instagram_clip.close()
            if 'tiktok_clip' in locals() and tiktok_clip:
                tiktok_clip.close()
            if final_clip:
                final_clip.close()
        except:
            pass
        
        log_processing(video_name, "failed", error_msg)
        return False


def process_batch(input_folder: Path = None, archive: bool = True):
    """
    Process all video files in the input folder.
    
    Args:
        input_folder: Folder containing videos to process. If None, uses config.INPUT_FOLDER
        archive: Whether to archive videos after successful processing
    """
    if input_folder is None:
        input_folder = config.INPUT_FOLDER
    else:
        input_folder = Path(input_folder)
    
    if not input_folder.exists():
        print(f"Error: Input folder not found: {input_folder}")
        return
    
    # Find all video files
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.m4v'}
    video_files = [
        f for f in input_folder.iterdir()
        if f.is_file() and f.suffix.lower() in video_extensions
    ]
    
    if not video_files:
        print(f"No video files found in {input_folder}")
        return
    
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING: Found {len(video_files)} video(s)")
    print(f"{'='*60}\n")
    
    results = {"success": 0, "failed": 0, "failed_files": []}
    
    for i, video_file in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] Processing: {video_file.name}")
        success = process_video(video_file, archive=archive)
        
        if success:
            results["success"] += 1
        else:
            results["failed"] += 1
            results["failed_files"].append(video_file.name)
    
    # Summary
    print(f"\n{'='*60}")
    print("BATCH PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total videos: {len(video_files)}")
    print(f"Successful: {results['success']}")
    print(f"Failed: {results['failed']}")
    
    if results["failed_files"]:
        print(f"\nFailed files:")
        for filename in results["failed_files"]:
            print(f"  - {filename}")
    
    print(f"{'='*60}\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Process Amazon review videos for social media platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single video
  python process.py --input video.mp4
  
  # Process a single video (full path)
  python process.py --input "C:/path/to/video.mp4"
  
  # Process all videos in storage/inputs folder
  python process.py --batch
  
  # Process all videos in a specific folder
  python process.py --batch --input-folder "C:/path/to/videos"
  
  # Process single video without archiving
  python process.py --input video.mp4 --no-archive
        """
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Path to input video file (for single video processing)"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process all videos in the input folder"
    )
    parser.add_argument(
        "--input-folder",
        type=str,
        help="Folder containing videos (for batch processing). Defaults to storage/inputs"
    )
    parser.add_argument(
        "--no-archive",
        action="store_true",
        help="Don't archive videos after processing"
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload videos to platforms (overrides AUTO_UPLOAD_ENABLED setting)"
    )
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip uploading videos (overrides AUTO_UPLOAD_ENABLED setting)"
    )
    
    args = parser.parse_args()
    
    archive = not args.no_archive
    
    # Handle upload flag (overrides config)
    if args.upload:
        config.AUTO_UPLOAD_ENABLED = True
    elif args.no_upload:
        config.AUTO_UPLOAD_ENABLED = False
    
    # Batch processing mode
    if args.batch:
        input_folder = Path(args.input_folder) if args.input_folder else None
        process_batch(input_folder, archive=archive)
        return
    
    # Single video processing mode
    if not args.input:
        parser.error("Either --input or --batch must be specified")
    
    input_path = Path(args.input)
    
    # If input is just a filename, check in INPUT_FOLDER
    if not input_path.is_absolute() and not input_path.exists():
        potential_path = config.INPUT_FOLDER / input_path
        if potential_path.exists():
            input_path = potential_path
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return
    
    if not input_path.is_file():
        print(f"Error: Input path is not a file: {input_path}")
        return
    
    # Process the video
    process_video(input_path, archive=archive)


if __name__ == "__main__":
    main()

