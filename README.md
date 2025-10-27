# Jellyfin Media Downloader

A simple Python script to download all media files from a Jellyfin server.

## Requirements

- Python 3.6+
- `requests` library
- `tqdm` library for progress bars

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The script supports configuration via environment variables or by editing the configuration section in `getJellyfin.py`.

### Environment Variables (Recommended)

Create a `.env` file or set environment variables:

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
JELLYFIN_URL=https://your-jellyfin-server.com
USER_NAME=your_username
JELLYFIN_PASSWORD=your_password
DOWNLOAD_PATH=/data
DRY_RUN=false
```

### Direct Configuration

Alternatively, edit the configuration section at the top of `getJellyfin.py`:

```python
# --- CONFIGURATION ---
JELLYFIN_URL = os.getenv('JELLYFIN_URL', 'https://your-jellyfin-server.com')
USER_NAME = os.getenv('USER_NAME', 'your_username')
JELLYFIN_PASSWORD = os.getenv('JELLYFIN_PASSWORD', 'your_password')
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', '/data')
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() in ('true', '1', 'yes', 'on')
```

### Configuration Options

- `JELLYFIN_URL`: Full URL to your Jellyfin server
- `USER_NAME`: Your Jellyfin username
- `JELLYFIN_PASSWORD`: Your Jellyfin password
- `DOWNLOAD_PATH`: Local directory where files will be saved
- `DRY_RUN`: Set to `true` to see what would be downloaded without actually downloading

## Usage

### Docker (Recommended)

1. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your Jellyfin server details
   ```

2. Build and run with Docker:
   ```bash
   # Build the image
   docker build -t jellyfin-downloader .

   # Run with environment file
   docker run --env-file .env -v $(pwd)/downloads:/data jellyfin-downloader

   # Or run with individual environment variables
   docker run -e JELLYFIN_URL=https://your-server.com \
              -e USER_NAME=your_user \
              -e JELLYFIN_PASSWORD=your_pass \
              -v $(pwd)/downloads:/data \
              jellyfin-downloader
   ```

### Direct Python

1. Configure the script with your Jellyfin server details (via environment variables or editing the file)
2. Run the script:
   ```bash
   python3 getJellyfin.py
   ```

The script will:
1. Authenticate with your Jellyfin server
2. Fetch all video media items
3. Download each file to your specified directory
4. Show progress for each download
5. Skip files that already exist

## Security Note

⚠️ **Warning**: This script stores your Jellyfin password in plain text. Make sure to:
- Keep the script file secure and private
- Consider using environment variables for sensitive information
- Only run this script on trusted systems

## Example Output

```
🚀 Starting Jellyfin Media Downloader
📂 Download directory: /data
🔒 Authenticating user 'username'...
✅ Authentication successful!
🔎 Fetching all media items...
✅ Found 150 media items

📥 Starting download of 150 items...

--- Item 1/150 ---
🔽 Downloading 'Item Title'
Item Title.mp4: 100%|████████| 1.2GB/1.2GB [02:30<00:00, 8.1MB/s]
    ✅ Downloaded: Item Title.mp4

🎉 Download Complete!
✅ Successful: 149
❌ Failed: 1
📂 Files saved to: /data
```

## License

This project is open source and available under the MIT License.
