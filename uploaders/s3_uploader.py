"""
AWS S3 uploader for Instagram video URLs.

This module uploads videos to AWS S3 and makes them publicly accessible
so they can be used with Instagram Graph API (which requires video_url).
"""

import os
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
from typing import Optional


class S3Uploader:
    """
    Uploads videos to AWS S3 and makes them publicly accessible.
    Automatically cleans up files after Instagram upload (optional).
    """
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = None
        self.region = None
        self.cleanup_after_upload = True  # Clean up S3 files after Instagram upload
        self.last_uploaded_key = None  # Store S3 key for cleanup
    
    def authenticate(self) -> bool:
        """
        Authenticate with AWS S3.
        
        Uses AWS credentials from environment variables or AWS credentials file.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Get AWS credentials from environment
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            self.region = os.getenv("AWS_REGION", "us-east-1")
            self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
            
            if not aws_access_key or not aws_secret_key:
                print("  Error: AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY not set in .env")
                print("  Get these from: https://console.aws.amazon.com/iam/")
                return False
            
            if not self.bucket_name:
                print("  Error: AWS_S3_BUCKET_NAME not set in .env")
                print("  Create a bucket at: https://s3.console.aws.amazon.com/")
                return False
            
            # Create S3 client
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=self.region
            )
            
            # Test connection by checking if bucket exists and get actual region
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                
                # Get the actual bucket region (may differ from .env setting)
                try:
                    bucket_location = self.s3_client.get_bucket_location(Bucket=self.bucket_name)
                    actual_region = bucket_location.get('LocationConstraint', 'us-east-1')
                    # us-east-1 returns None, so handle that
                    if actual_region is None or actual_region == '':
                        actual_region = 'us-east-1'
                    
                    # Update region to match bucket's actual region
                    if actual_region != self.region:
                        print(f"  [INFO] Bucket region is {actual_region} (not {self.region} from .env)")
                        self.region = actual_region
                        # Recreate client with correct region
                        self.s3_client = boto3.client(
                            's3',
                            aws_access_key_id=aws_access_key,
                            aws_secret_access_key=aws_secret_key,
                            region_name=self.region
                        )
                except Exception as e:
                    print(f"  Warning: Could not get bucket region: {e}")
                    print(f"  Using region from .env: {self.region}")
                
                print(f"  [OK] Authenticated with AWS S3")
                print(f"  Bucket: {self.bucket_name}")
                print(f"  Region: {self.region}")
                return True
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    print(f"  Error: Bucket '{self.bucket_name}' not found")
                    print(f"  Create it at: https://s3.console.aws.amazon.com/")
                elif error_code == '403':
                    print(f"  Error: Access denied to bucket '{self.bucket_name}'")
                    print(f"  Check your AWS credentials and bucket permissions")
                else:
                    print(f"  Error accessing bucket: {e}")
                return False
                
        except Exception as e:
            print(f"  Error authenticating with AWS S3: {e}")
            return False
    
    def upload_video_and_get_url(
        self,
        video_path: Path,
        folder_prefix: str = "instagram-videos"
    ) -> Optional[str]:
        """
        Upload video to S3 and return publicly accessible URL.
        
        Args:
            video_path: Path to video file
            folder_prefix: Prefix for S3 object key (folder path)
            
        Returns:
            Public URL to the video file, or None if failed
        """
        if not self.s3_client:
            if not self.authenticate():
                return None
        
        try:
            # Generate S3 object key (file path in bucket)
            # Format: instagram-videos/2025-11-19/video-name.mp4
            from datetime import datetime
            date_folder = datetime.now().strftime("%Y-%m-%d")
            s3_key = f"{folder_prefix}/{date_folder}/{video_path.name}"
            
            print(f"  Uploading video to S3...")
            print(f"  Bucket: {self.bucket_name}")
            print(f"  Key: {s3_key}")
            
            # Upload file to S3
            # Note: ACLs are disabled on newer buckets, so we rely on bucket policy for public access
            self.s3_client.upload_file(
                str(video_path),
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': 'video/mp4'
                    # ACL removed - bucket policy handles public access
                }
            )
            
            # Generate public URL
            # Format: https://BUCKET_NAME.s3.REGION.amazonaws.com/KEY
            public_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            # Alternative: Use S3 website endpoint if bucket is configured for static hosting
            # But the direct URL above should work fine
            
            print(f"  [OK] Video uploaded to S3")
            print(f"  [OK] Public URL: {public_url[:60]}...")
            
            # Store S3 key for potential cleanup later
            self.last_uploaded_key = s3_key
            
            return public_url
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                print(f"  Error: Bucket '{self.bucket_name}' does not exist")
            elif error_code == 'AccessDenied':
                print(f"  Error: Access denied. Check bucket permissions and IAM policy")
            else:
                print(f"  Error uploading to S3: {e}")
            return None
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3 (cleanup after Instagram upload).
        
        Args:
            s3_key: S3 object key (path) to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            print(f"  [OK] Cleaned up S3 file: {s3_key}")
            return True
        except Exception as e:
            print(f"  Warning: Could not delete S3 file: {e}")
            return False

