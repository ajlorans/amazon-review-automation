"""
Main CLI tool for processing Amazon review videos.

Usage:
    python process.py --input path/to/video.mp4

This script:
1. Normalizes the input video
2. Converts to vertical 9:16 format (1080x1920)
3. Adds CTA overlay with Amazon creator link
4. Exports to platform-specific folders
5. Generates metadata files for each platform
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import config

# Import uploaders (optional - only if upload is enabled)
try:
    from uploaders import YouTubeUploader, InstagramUploader, TikTokUploader
    UPLOADERS_AVAILABLE = True
except ImportError:
    UPLOADERS_AVAILABLE = False


def normalize_video(clip: VideoFileClip) -> VideoFileClip:
    """
    Normalize the input video.
    
    This function ensures consistent frame rate and audio settings.
    For MVP, we'll standardize to 30fps and ensure audio is present.
    
    Args:
        clip: Input video clip
        
    Returns:
        Normalized video clip
    """
    # Standardize frame rate to 30fps
    # Note: FPS will be set during export, but we can note it here
    if clip.fps != 30:
        print(f"  Note: Video FPS is {clip.fps:.2f}, will be converted to 30fps on export")
    
    # Ensure audio is present (if original has no audio, we'll keep it silent)
    if clip.audio is None:
        print("Warning: Input video has no audio track.")
    
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
    
    Strategy:
    - If video is wider than tall: crop center and resize
    - If video is taller than wide: crop center and resize
    - Use blurred background if needed (for MVP, we'll use center crop)
    
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
    
    # Calculate how to crop and resize
    if current_aspect > target_aspect:
        # Video is wider than target (landscape)
        # Crop to match target aspect ratio
        new_height = current_height
        new_width = int(current_height * target_aspect)
        x_center = current_width / 2
        x1 = int(x_center - new_width / 2)
        x2 = int(x_center + new_width / 2)
        
        # Crop horizontally (MoviePy 2.x uses cropped() instead of crop())
        cropped = clip.cropped(x1=x1, x2=x2, y1=0, y2=current_height)
    else:
        # Video is taller than target (portrait or square)
        # Crop to match target aspect ratio
        new_width = current_width
        new_height = int(current_width / target_aspect)
        y_center = current_height / 2
        y1 = int(y_center - new_height / 2)
        y2 = int(y_center + new_height / 2)
        
        # Crop vertically (MoviePy 2.x uses cropped() instead of crop())
        cropped = clip.cropped(x1=0, x2=current_width, y1=y1, y2=y2)
    
    # Resize to target dimensions (MoviePy 2.x uses resized() instead of resize())
    vertical_clip = cropped.resized(new_size=(target_width, target_height))
    
    return vertical_clip


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


def export_video(clip: CompositeVideoClip, output_path: Path, platform: str):
    """
    Export video to specified path.
    
    Args:
        clip: Video clip to export
        output_path: Output file path
        platform: Platform name (for logging)
    """
    print(f"Exporting {platform} video to {output_path}...")
    clip.write_videofile(
        str(output_path),
        codec='libx264',
        audio_codec='aac',
        fps=30,
        preset='medium',  # Balance between speed and quality
        threads=4
    )
    print(f"[OK] {platform} video exported successfully!")


def generate_metadata(video_name: str, platform: str) -> dict:
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
        description = config.get_youtube_description(title, hashtags)
        metadata = {
            "title": title,
            "description": description,
            "hashtags": hashtags
        }
    elif platform == "instagram":
        caption = config.get_instagram_caption(title, hashtags)
        metadata = {
            "caption": caption,
            "hashtags": hashtags
        }
    elif platform == "tiktok":
        caption = config.get_tiktok_caption(title, hashtags)
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
    vertical_clip = None
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
        
        # Step 3: Extract segment (for MVP, use whole video or limit to max duration)
        print("\nStep 3: Extracting clip segment...")
        clip = extract_clip_segment(clip)
        print(f"  Segment: {clip.duration:.2f}s")
        
        # Step 4: Convert to vertical
        print("\nStep 4: Converting to vertical format (1080x1920)...")
        vertical_clip = convert_to_vertical(clip)
        print(f"  Vertical: {vertical_clip.w}x{vertical_clip.h}")
        
        # Step 5: Add CTA overlay
        print("\nStep 5: Adding CTA overlay...")
        final_clip = add_cta_overlay(vertical_clip)
        
        # Step 6: Export for each platform (using date-based folders)
        print("\nStep 6: Exporting videos...")
        date_folder = datetime.now().strftime("%Y-%m-%d")
        
        uploaded_videos = {}  # Store upload results
        
        for platform in ["youtube", "instagram", "tiktok"]:
            output_folder = config.get_output_folder(platform, date_folder)
            output_path = output_folder / f"{video_name}.mp4"
            
            # Export video
            export_video(final_clip, output_path, platform)
            
            # Generate and save metadata
            metadata = generate_metadata(video_name, platform)
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
        if vertical_clip:
            vertical_clip.close()
        if final_clip:
            final_clip.close()
        
        # Step 7: Upload to platforms (if enabled)
        if config.AUTO_UPLOAD_ENABLED and UPLOADERS_AVAILABLE:
            print(f"\n{'='*60}")
            print("Step 7: Uploading videos to platforms...")
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
            if vertical_clip:
                vertical_clip.close()
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

