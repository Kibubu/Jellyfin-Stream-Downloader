#!/usr/bin/env python3

import os
import requests
import json
import shutil
from tqdm import tqdm

# --- CONFIGURATION ---
# Configuration with environment variable support
JELLYFIN_URL = os.getenv('JELLYFIN_URL', 'http://localhost')
USER_NAME = os.getenv('USER_NAME', 'jelly')
JELLYFIN_PASSWORD = os.getenv('JELLYFIN_PASSWORD', 'fin')
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', './')
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() in ('true', '1', 'yes', 'on')

# --- END OF CONFIGURATION ---


def authenticate_and_get_token(session, base_url, username, password):
    """Authenticates with username/password to get an access token and user ID."""
    auth_url = f"{base_url}/Users/AuthenticateByName"
    auth_payload = {"Username": username, "Pw": password}
    auth_headers = {
        "Content-Type": "application/json",
        "X-Emby-Authorization": 'MediaBrowser Client="SimpleDownloader", Device="Script", DeviceId="SimpleDownloaderV1", Version="1.0"'
    }

    print(f"🔒 Authenticating user '{username}'...")
    try:
        response = session.post(auth_url, headers=auth_headers, data=json.dumps(auth_payload))
        response.raise_for_status()
        auth_data = response.json()
        access_token = auth_data.get("AccessToken")
        user_id = auth_data.get("User", {}).get("Id")

        if not access_token or not user_id:
            print("❌ Authentication failed - no access token or user ID returned.")
            return None, None

        print("✅ Authentication successful!")
        return access_token, user_id
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication failed: {e}")
        return None, None


def get_all_media(session, base_url, user_id):
    """Gets all media items from Jellyfin."""
    print("🔎 Fetching all media items...")

    params = {
        "recursive": "true",
        "userId": user_id,
        "fields": "Path,ParentId,PremiereDate,OriginalTitle",
    }

    try:
        response = session.get(f"{base_url}/Items", params=params)
        response.raise_for_status()
        items = response.json().get("Items", [])

        # Filter out folders and get only video files
        media_items = [item for item in items if item.get("Type") != "Folder" and item.get("MediaType") == "Video"]

        print(f"✅ Found {len(media_items)} media items")
        return media_items
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching media: {e}")
        return []


def download_media_item(session, base_url, item, download_path):
    """Downloads a single media item."""
    item_id = item["Id"]
    item_name = item.get("Name", "Unknown")
    original_path = item.get("Path", f"{item_name}.mp4")
    _, original_extension = os.path.splitext(original_path)

    # Sanitize filename
    safe_name = "".join(c for c in item_name if c.isalnum() or c in " .-_()")
    filename = f"{safe_name}{original_extension}"
    filepath = os.path.join(download_path, filename)

    # Skip if file already exists
    if os.path.exists(filepath):
        print(f"⏭️ Skipping '{item_name}' - file already exists")
        return True

    stream_url = f"{base_url}/Videos/{item_id}/stream.mp4"
    print(f"🔽 Downloading '{item_name}'")

    if DRY_RUN:
        print(f"    [DRY RUN] Would download: {filename}")
        return True

    try:
        with session.get(stream_url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))

            with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))

        print(f"    ✅ Downloaded: {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Failed to download '{item_name}': {e}")
        return False
    except IOError as e:
        print(f"    ❌ Failed to write file '{filename}': {e}")
        return False


def main():
    """Main function to download all media from Jellyfin."""
    print("🚀 Starting Jellyfin Media Downloader")

    if DRY_RUN:
        print("🔍 DRY RUN MODE - No files will be downloaded")

    # Ensure download directory exists
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    print(f"📂 Download directory: {DOWNLOAD_PATH}")

    # Authenticate with Jellyfin
    session = requests.Session()
    access_token, user_id = authenticate_and_get_token(session, JELLYFIN_URL, USER_NAME, JELLYFIN_PASSWORD)

    if not access_token or not user_id:
        print("❌ Authentication failed. Exiting.")
        return

    session.headers.update({"X-Emby-Authorization": f'MediaBrowser Token="{access_token}"'})

    # Get all media items
    media_items = get_all_media(session, JELLYFIN_URL, user_id)

    if not media_items:
        print("❌ No media items found. Exiting.")
        return

    # Download all media items
    print(f"\n📥 Starting download of {len(media_items)} items...")
    successful_downloads = 0
    failed_downloads = 0

    for i, item in enumerate(media_items, 1):
        print(f"\n--- Item {i}/{len(media_items)} ---")
        if download_media_item(session, JELLYFIN_URL, item, DOWNLOAD_PATH):
            successful_downloads += 1
        else:
            failed_downloads += 1

    # Summary
    print(f"\n🎉 Download Complete!")
    print(f"✅ Successful: {successful_downloads}")
    print(f"❌ Failed: {failed_downloads}")
    print(f"📂 Files saved to: {DOWNLOAD_PATH}")


if __name__ == "__main__":
    main()
