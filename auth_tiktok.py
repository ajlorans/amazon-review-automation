"""
TikTok OAuth2 Authentication Helper
This script will help you get your TikTok access token.
"""

import os
import sys
import urllib.parse
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

print("=" * 70)
print("TikTok OAuth2 Authentication Setup")
print("=" * 70)

# Step 1: Get Client Key and Secret
print("\nStep 1: Getting your TikTok App credentials...")
print("-" * 70)

client_key = os.getenv("TIKTOK_CLIENT_KEY")
client_secret = os.getenv("TIKTOK_CLIENT_SECRET")

if not client_key or client_key == "your_key_here":
    print("\n[INFO] TIKTOK_CLIENT_KEY not found in .env")
    print("\nTo get your Client Key and Secret:")
    print("1. Go to: https://developers.tiktok.com/")
    print("2. Log in and go to your app")
    print("3. Go to 'Basic Information' or 'Keys' section")
    print("4. Copy your Client Key and Client Secret")
    print("\nThen update your .env file with:")
    print("  TIKTOK_CLIENT_KEY=your_client_key_here")
    print("  TIKTOK_CLIENT_SECRET=your_client_secret_here")
    
    # Ask user to input them
    print("\n" + "=" * 70)
    print("Enter your TikTok App credentials:")
    print("=" * 70)
    client_key = input("\nClient Key: ").strip()
    client_secret = input("Client Secret: ").strip()
    
    if not client_key or not client_secret:
        print("\n[ERROR] Client Key and Secret are required!")
        sys.exit(1)
    
    # Update .env file
    env_file = Path(".env")
    if env_file.exists():
        content = env_file.read_text()
        # Update or add TIKTOK_CLIENT_KEY
        if "TIKTOK_CLIENT_KEY=" in content:
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith("TIKTOK_CLIENT_KEY="):
                    new_lines.append(f"TIKTOK_CLIENT_KEY={client_key}")
                elif line.startswith("TIKTOK_CLIENT_SECRET="):
                    new_lines.append(f"TIKTOK_CLIENT_SECRET={client_secret}")
                else:
                    new_lines.append(line)
            env_file.write_text('\n'.join(new_lines))
        else:
            # Append to file
            with open(env_file, 'a') as f:
                f.write(f"\nTIKTOK_CLIENT_KEY={client_key}\n")
                f.write(f"TIKTOK_CLIENT_SECRET={client_secret}\n")
        print("\n[OK] Credentials saved to .env file")
    else:
        print("\n[WARNING] .env file not found. Please add these manually:")
        print(f"TIKTOK_CLIENT_KEY={client_key}")
        print(f"TIKTOK_CLIENT_SECRET={client_secret}")

# Get redirect URI
print("\nStep 2: Setting up OAuth2 flow...")
print("-" * 70)

# Default redirect URI (you should set this in your TikTok app settings)
redirect_uri = input("\nEnter your Redirect URI (from TikTok app settings, or press Enter for http://localhost:8080): ").strip()
if not redirect_uri:
    redirect_uri = "http://localhost:8080"
    print(f"Using default: {redirect_uri}")

print(f"\n[INFO] Make sure this redirect URI is configured in your TikTok app:")
print(f"       {redirect_uri}")
print("\nTo set it up:")
print("1. Go to your TikTok app in https://developers.tiktok.com/")
print("2. Go to 'Platform' or 'OAuth' settings")
print("3. Add this redirect URI to the allowed list")

input("\nPress Enter when you've configured the redirect URI in your TikTok app...")

# Step 3: Generate authorization URL
print("\nStep 3: Generating authorization URL...")
print("-" * 70)

auth_url = "https://www.tiktok.com/v2/auth/authorize/"
params = {
    "client_key": client_key,
    "scope": "video.upload",
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "state": "tiktok_auth"
}

full_auth_url = auth_url + "?" + urllib.parse.urlencode(params)

print(f"\n[INFO] Opening browser for authorization...")
print(f"\nIf browser doesn't open, copy this URL:")
print(f"\n{full_auth_url}\n")

try:
    webbrowser.open(full_auth_url)
except Exception as e:
    print(f"[WARNING] Could not open browser automatically: {e}")
    print(f"\nPlease open this URL manually:\n{full_auth_url}\n")

print("=" * 70)
print("IMPORTANT: After authorizing, you'll be redirected to your redirect URI")
print("The URL will contain a 'code' parameter - copy that code!")
print("=" * 70)

# Step 4: Get authorization code from user
print("\nStep 4: Getting authorization code...")
print("-" * 70)
print("\nAfter you authorize the app, you'll be redirected to a URL like:")
print(f"  {redirect_uri}?code=AUTHORIZATION_CODE&state=tiktok_auth")
print("\nCopy the 'code' value from the URL and paste it below.")
print("(If you see an error page, the code might still be in the URL)\n")

auth_code = input("Authorization Code: ").strip()

if not auth_code:
    print("\n[ERROR] Authorization code is required!")
    sys.exit(1)

# Step 5: Exchange code for access token
print("\nStep 5: Exchanging code for access token...")
print("-" * 70)

token_url = "https://open.tiktokapis.com/v2/oauth/token/"

token_data = {
    "client_key": client_key,
    "client_secret": client_secret,
    "code": auth_code,
    "grant_type": "authorization_code",
    "redirect_uri": redirect_uri
}

print("\n[INFO] Requesting access token...")
try:
    response = requests.post(token_url, json=token_data)
    
    if response.status_code == 200:
        token_response = response.json()
        
        if "data" in token_response and "access_token" in token_response["data"]:
            access_token = token_response["data"]["access_token"]
            refresh_token = token_response["data"].get("refresh_token", "")
            expires_in = token_response["data"].get("expires_in", 0)
            
            print("\n[SUCCESS] Access token received!")
            print(f"  Token expires in: {expires_in} seconds")
            
            # Save to .env
            env_file = Path(".env")
            if env_file.exists():
                content = env_file.read_text()
                if "TIKTOK_ACCESS_TOKEN=" in content:
                    lines = content.split('\n')
                    new_lines = []
                    for line in lines:
                        if line.startswith("TIKTOK_ACCESS_TOKEN="):
                            new_lines.append(f"TIKTOK_ACCESS_TOKEN={access_token}")
                        else:
                            new_lines.append(line)
                    env_file.write_text('\n'.join(new_lines))
                else:
                    with open(env_file, 'a') as f:
                        f.write(f"\nTIKTOK_ACCESS_TOKEN={access_token}\n")
                print("\n[OK] Access token saved to .env file")
            else:
                print("\n[WARNING] .env file not found. Please add manually:")
                print(f"TIKTOK_ACCESS_TOKEN={access_token}")
            
            # Test the token
            print("\nStep 6: Testing access token...")
            print("-" * 70)
            
            test_response = requests.get(
                "https://open.tiktokapis.com/v2/user/info/",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"fields": "open_id,union_id,avatar_url,display_name"}
            )
            
            if test_response.status_code == 200:
                user_data = test_response.json()
                print("\n[SUCCESS] Token is valid!")
                if "data" in user_data and "user" in user_data["data"]:
                    user = user_data["data"]["user"]
                    print(f"  Display Name: {user.get('display_name', 'N/A')}")
                    print(f"  Open ID: {user.get('open_id', 'N/A')}")
                
                print("\n" + "=" * 70)
                print("[COMPLETE] TikTok authentication setup successful!")
                print("=" * 70)
                print("\nYou can now upload videos to TikTok using:")
                print("  python process.py --input video.mp4 --upload")
            else:
                print(f"\n[WARNING] Token test failed: {test_response.status_code}")
                print(f"Response: {test_response.text}")
                print("\nBut the token was saved - you can try using it anyway.")
        else:
            print("\n[ERROR] No access token in response")
            print(f"Response: {token_response}")
    else:
        print(f"\n[ERROR] Failed to get access token: {response.status_code}")
        print(f"Response: {response.text}")
        print("\nCommon issues:")
        print("  - Authorization code expired (codes expire quickly)")
        print("  - Redirect URI mismatch (must match exactly)")
        print("  - Invalid client credentials")
        print("\nTry running this script again to get a fresh code.")
        
except Exception as e:
    print(f"\n[ERROR] An error occurred: {e}")
    import traceback
    traceback.print_exc()

