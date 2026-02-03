# AV Morning Star - YouTube Authentication Guide

## Overview

As of February 2026, YouTube has implemented bot protection that blocks both yt-dlp and InnerTube API access. The solution is to **authenticate using your browser's cookies**, which makes YouTube believe you're a logged-in user.

## How It Works

1. You log into YouTube using your browser (Firefox, Chrome, Brave, etc.)
2. AV Morning Star extracts your authentication cookies from the browser
3. These cookies are passed to both InnerTube API and yt-dlp
4. YouTube recognizes you as an authenticated user and allows downloads

## Supported Browsers

- **Firefox** (including Firefox ESR, LibreWolf, IceCat)
- **Chrome** / Chromium
- **Brave**
- **Edge**
- **Opera**
- **Safari** (macOS only)
- **Vivaldi**

## Current Status (February 2026)

### InnerTube API (Default)
- **Library**: innertube 2.1.19
- **Status**: Supports cookie authentication via custom httpx.Client
- **Implementation**: COMPLETE ✓
- **How to use**:
  ```python
  from extractors import get_extractor
  
  # Authenticate with Brave browser cookies
  extractor = get_extractor(url, cookies_from_browser='brave')
  
  # Or Firefox
  extractor = get_extractor(url, cookies_from_browser='firefox')
  ```

### yt-dlp Fallback
- **Library**: yt-dlp 2026.1.31
- **Status**: Also supports browser cookies natively
- **Automatic**: Cookies are automatically passed to yt-dlp downloads

## How to Enable YouTube Downloads

### Option 1: Using Firefox (Recommended)

1. **Open Firefox and log into YouTube**
   - Go to https://www.youtube.com
   - Sign in with your Google account
   - Make sure you're fully logged in (see your profile picture)

2. **No additional steps needed!**
   - AV Morning Star will automatically use your Firefox cookies
   - Just paste any YouTube URL and download

### Option 2: Using Brave Browser

1. **Open Brave and log into YouTube**
   - Same as Firefox - just sign in normally

2. **Specify browser when extracting** (currently manual, UI coming soon)
   ```python
   extractor = get_extractor(youtube_url, cookies_from_browser='brave')
   ```

### Option 3: Using Chrome/Chromium

1. **Log into YouTube in Chrome**
2. **Specify 'chrome' as browser**:
   ```python
   extractor = get_extractor(youtube_url, cookies_from_browser='chrome')
   ```

## Technical Implementation

### YouTubeExtractor Cookie Flow

```python
class YouTubeExtractor:
    def __init__(self, url, cookies_from_browser=None):
        # 1. Extract cookies from specified browser
        cookies = self._extract_browser_cookies()  # Uses yt-dlp's extraction
        
        # 2. Create custom httpx.Client with cookies
        session = httpx.Client(
            base_url=config.base_url,
            cookies=httpx_cookies,  # Converted from cookie jar
            headers={
                'User-Agent': '...',
                'Origin': 'https://www.youtube.com',
                'Referer': 'https://www.youtube.com/'
            }
        )
        
        # 3. Create InnerTubeAdaptor with authenticated session
        adaptor = InnerTubeAdaptor(context=context, session=session)
        self.client = Client(adaptor=adaptor)
```

### Download Flow with Cookies

```python
# In get_download_opts():
ydl_opts['cookiesfrombrowser'] = (self.cookies_from_browser,)

# yt-dlp uses the same browser cookies for downloads
```

## Security & Privacy

### Are my cookies safe?
YES. Your cookies are:
- ✓ Extracted temporarily at runtime
- ✓ Never saved to disk by AV Morning Star
- ✓ Only sent to YouTube/Google servers (same as your browser)
- ✓ Not shared with any third parties
- ✓ Discarded when the application closes

### What cookies are used?
Only YouTube/Google authentication cookies:
- SSID, APISID, SAPISID, HSID, SID (Google auth)
- LOGIN_INFO (YouTube auth)
- Domain: .youtube.com, youtube.com

### Do I need to stay logged in?
Yes, keep your browser session active:
- Don't log out of YouTube while using AV Morning Star
- If you log out, downloads will fail
- Just log back in and try again

## Troubleshooting

###  "Failed to extract cookies from {browser}"

**Cause**: Browser not found or no YouTube cookies exist

**Solutions**:
1. Make sure you're logged into YouTube in that browser
2. Try a different browser (e.g., switch from Brave to Firefox)
3. Check that the browser is installed and you've used it recently

### ⚠️ "YouTube bot detection active: Sign in to confirm you're not a bot"

**Cause**: Cookie extraction failed or cookies expired

**Solutions**:
1. **Log out and log back into YouTube** in your browser
2. Visit a few YouTube videos to refresh your session
3. Try downloading again
4. If still failing, restart your browser

### ⚠️ Downloads work but metadata extraction fails

**Cause**: InnerTube API still blocked even with cookies

**Solutions**:
- This is normal - download will continue via yt-dlp fallback
- Videos will still download successfully
- Metadata (title, uploader) may show as "Unknown" but file will be correct

## Future Enhancements (Coming Soon)

### UI Integration
- [ ] **Browser selection dropdown** in main UI
- [ ] **"Login with Browser" button** to test cookies
- [ ] **Status indicator** showing authentication state
- [ ] **Auto-detect default browser**

### Advanced Features
- [ ] **OAuth2 login** (when innertube library adds support)
- [ ] **Cookie file support** (load from cookies.txt)
- [ ] **Multi-account support** (switch between Google accounts)
- [ ] **Persistent authentication** (remember browser choice)

## Comparison: Before vs After Authentication

### Before (Unauthenticated - Feb 2026)
```
❌ InnerTube API: LOGIN_REQUIRED
❌ yt-dlp: Bot detection errors
❌ Result: No YouTube downloads work
```

### After (With Browser Cookies)
```
✅ InnerTube API: Authenticated access
✅ yt-dlp: Downloads work with cookies
✅ Result: YouTube downloads work normally!
```

## Example Code Usage

### Basic Download (Auto-detect browser)
```python
from extractors import get_extractor

# Will use Firefox by default if available
extractor = get_extractor(
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    cookies_from_browser='firefox'
)

videos = extractor.extract_info()
# Downloads proceed normally with authentication
```

### Multiple Videos with Cookies
```python
playlist_url = 'https://www.youtube.com/playlist?list=...'
extractor = get_extractor(playlist_url, cookies_from_browser='brave')

videos = extractor.extract_info()  # Gets all playlist videos
for video in videos:
    print(f"{video['title']} - {video['uploader']}")
```

## Why This Works

1. **YouTube's bot protection** checks for:
   - Valid user-agent headers ✓ (We mimic browsers)
   - Authentication cookies ✓ (We use real browser cookies)
   - Request patterns ✓ (InnerTube mimics official clients)

2. **Using real browser cookies** means:
   - YouTube sees you as a legitimate logged-in user
   - All videos accessible to your account can be downloaded
   - Age-restricted and members-only content works

3. **Combining InnerTube + cookies**:
   - InnerTube uses YouTube's official internal API
   - Adding cookies authenticates the API requests
   - Same method used by successful apps like GrayJay

## Recommended Setup

1. **Keep Firefox/Brave open** with an active YouTube session
2. **Use Firefox as default** (best cookie extraction support)
3. **Stay logged in** while using AV Morning Star
4. **Refresh your session** periodically (watch a video or two)

---

**Last Updated**: February 3, 2026  
**Compatible with**: innertube 2.1.19, yt-dlp 2026.1.31
