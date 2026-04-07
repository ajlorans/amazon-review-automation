"""
Quick check that INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID work.
Loads .env via config; does not process or upload any video.
"""

import os

import config  # noqa: F401 — loads .env
from uploaders.instagram_uploader import InstagramUploader

print("=" * 60)
print("Instagram access token check")
print("=" * 60)

token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

if not token:
    print("\n[ERROR] INSTAGRAM_ACCESS_TOKEN not set in .env")
    raise SystemExit(1)
if not account_id:
    print("\n[ERROR] INSTAGRAM_ACCOUNT_ID not set in .env")
    raise SystemExit(1)

print(f"\nINSTAGRAM_ACCOUNT_ID: {account_id}")
print("Calling Graph API GET /me (validates token)...")

uploader = InstagramUploader()
ok = uploader.authenticate()

print("\n" + "=" * 60)
if ok:
    print("[OK] Token is valid; Instagram API accepted it.")
else:
    print("[FAILED] Token invalid or expired — see messages above.")
print("=" * 60)
raise SystemExit(0 if ok else 1)
