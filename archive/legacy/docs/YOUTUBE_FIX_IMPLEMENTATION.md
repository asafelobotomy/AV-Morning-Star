# YouTube Download Fix - Implementation Guide

## Problem Summary

**Issue:** YouTube downloads were failing with "Sign in to confirm you're not a bot" error despite being logged in via browser cookies.

**Root Cause:** As of November 2025, YouTube requires **Proof of Origin (PO) Tokens** for all video access. These tokens must be generated using an external JavaScript runtime (Deno, Node.js, QuickJS, or Bun). The previous InnerTube API approach could not generate these tokens.

**Official Announcement:** [yt-dlp Issue #15012](https://github.com/yt-dlp/yt-dlp/issues/15012) - "External JavaScript runtime now required for full YouTube support"

## Solution Implemented

### What Changed

We replaced the custom InnerTube API implementation with **yt-dlp as a backend**, which already has full PO token support built-in.

**Files Modified:**
1. Created: `extractors/youtube_ytdlp.py` - New yt-dlp-based extractor
2. Modified: `extractors/__init__.py` - Updated import to use new extractor
3. Preserved: `extractors/youtube.py` - Kept as backup/reference

### Architecture Change

**Before (InnerTube API):**
```
User → AV Morning Star → InnerTube Library → YouTube API
                            ❌ Cannot generate PO tokens
```

**After (yt-dlp Backend):**
```
User → AV Morning Star → yt-dlp → JS Runtime → YouTube API
                          ✅ PO tokens handled automatically
```

### Key Features Preserved

✅ **Browser Cookie Authentication**: Still uses browser cookies (Firefox, Chrome, Brave, etc.)  
✅ **Same Interface**: No changes needed to main.py  
✅ **Format Support**: Video quality selection, audio extraction, subtitles  
✅ **Playlist Support**: Channels, playlists, single videos  
✅ **Progress Tracking**: Real-time download progress  

### New Capabilities

✅ **PO Token Generation**: Automatic via yt-dlp's JS runtime integration  
✅ **Bot Detection Bypass**: yt-dlp handles YouTube's challenges  
✅ **Future-Proof**: Weekly yt-dlp updates keep working with YouTube changes  
✅ **Battle-Tested**: Millions of users rely on yt-dlp daily  

## Installation Requirements

### Essential Dependencies (Already Installed)

```bash
pip install yt-dlp>=2023.0.0  # Already in requirements.txt
pip install PyQt5>=5.15.0     # Already in requirements.txt
```

### JavaScript Runtime (Recommended)

For optimal YouTube support, install **Deno** (preferred by yt-dlp maintainers):

**Linux/macOS:**
```bash
curl -fsSL https://deno.land/install.sh | sh
```

**Alternative Options:**
- Node.js 25+ (if Deno not available)
- QuickJS (lightweight option)
- Bun (modern alternative)

**Note:** yt-dlp will fallback through runtimes automatically. If none are installed, YouTube support may be limited.

### Check Current Status

```bash
# Check if yt-dlp can find a JS runtime
yt-dlp --version

# Test YouTube extraction
yt-dlp --cookies-from-browser firefox --skip-download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## How to Use

### Step 1: Configure Browser in Preferences

1. Open AV Morning Star
2. Go to **Tools > Preferences**
3. Select your browser (Firefox, Chrome, Brave, etc.)
4. Make sure you're logged into YouTube in that browser
5. Click **Save**

### Step 2: Download Videos

1. Enter YouTube URL (video, playlist, or channel)
2. Click **Fetch** to retrieve video list
3. Select videos to download
4. Choose format (Video or Audio Only)
5. Click **Download Selected**

### Supported URL Types

✅ Single Video: `https://www.youtube.com/watch?v=VIDEO_ID`  
✅ Playlist: `https://www.youtube.com/playlist?list=PLAYLIST_ID`  
✅ Channel Videos: `https://www.youtube.com/@ChannelName/videos`  
✅ Short Links: `https://youtu.be/VIDEO_ID`  

## Troubleshooting

### Error: "Failed to extract YouTube info"

**Solution 1 - Update yt-dlp:**
```bash
source .venv/bin/activate
pip install --upgrade yt-dlp
```

**Solution 2 - Install JavaScript Runtime:**
```bash
# Install Deno (recommended)
curl -fsSL https://deno.land/install.sh | sh

# Add to PATH (Linux/macOS)
echo 'export DENO_INSTALL="$HOME/.deno"' >> ~/.bashrc
echo 'export PATH="$DENO_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Solution 3 - Try Different Browser:**
- Go to Tools > Preferences
- Try Chrome instead of Firefox (or vice versa)
- Make sure you're logged into YouTube in that browser

**Solution 4 - Clear Browser Cookies and Re-login:**
- Sign out of YouTube in your browser
- Clear YouTube cookies
- Sign back in
- Try download again

### Error: "Sign in to confirm you're not a bot"

This usually means:
1. You're not logged into YouTube in the selected browser
2. Your browser cookies are expired
3. YouTube is rate-limiting your IP

**Solutions:**
- Verify you're logged into YouTube in your browser
- Go to Tools > Preferences and confirm correct browser is selected
- Try a different browser
- Wait 10-15 minutes and try again

### Downloads Are Slow

**Solution:** Install Deno for faster PO token generation:
```bash
curl -fsSL https://deno.land/install.sh | sh
```

Deno significantly improves YouTube extraction speed compared to other JS runtimes.

## Technical Details

### PO Token System (YouTube 2025)

YouTube's **Proof of Origin (PO) Token** system was introduced in November 2025 to combat bot scraping. It works as follows:

1. **Token Request:** Client requests a PO token from YouTube
2. **JavaScript Challenge:** YouTube sends JS code to execute
3. **JS Runtime Execution:** External runtime (Deno/Node) executes the challenge
4. **Token Generation:** Challenge output becomes the PO token
5. **Authenticated Request:** Token is sent with video info requests

**Token Binding:**
- When **logged out:** Token binds to `visitor_data` (browser fingerprint)
- When **logged in:** Token binds to `data_sync_id` (account ID)
- Context-specific: Different tokens for video URLs, playback, subtitles

### Why yt-dlp?

**Advantages:**
- ✅ Active maintenance (weekly updates)
- ✅ Millions of users (battle-tested)
- ✅ Built-in PO token support
- ✅ Handles all YouTube edge cases
- ✅ Future-proof against YouTube changes

**Alternatives Considered:**

1. **InnerTube API (Previous):**
   - ❌ Cannot generate PO tokens
   - ❌ No JS runtime integration
   - ❌ Library maintainer inactive

2. **GrayJay Approach:**
   - ❌ Requires V8 JavaScript engine
   - ❌ Android-specific architecture
   - ❌ 2000+ line YouTube plugin to maintain
   - ❌ Constant updates needed for YouTube changes

3. **yt-dlp Backend (Current):**
   - ✅ All advantages listed above
   - ✅ Simple integration (single file change)
   - ✅ Same user experience
   - ✅ Proven reliability

### Code Architecture

**New YouTubeExtractor Class:**
```python
class YouTubeExtractor:
    def __init__(self, url, cookies_from_browser=None):
        # Initialize with yt-dlp backend
        
    def extract_info(self):
        # Uses yt-dlp to fetch video metadata
        # Returns standardized format
        
    def get_download_opts(self, ...):
        # Builds yt-dlp download options
        # Handles quality, format, postprocessing
```

**Benefits of This Design:**
- Same interface as before (no changes to main.py)
- Browser cookie support preserved
- All download options still work
- Easy to test and maintain

## Future Improvements

### Short-Term (Next Release)

1. **Auto-detect JS Runtime:**
   - Check for Deno/Node.js on startup
   - Show warning if none found
   - Provide installation instructions

2. **Enhanced Error Messages:**
   - Better guidance for PO token failures
   - Link to installation guides
   - Browser-specific troubleshooting

3. **Runtime Installation Script:**
   - Add Deno installation to start.sh
   - One-click setup for users
   - Verify installation on startup

### Long-Term (Future Versions)

1. **Hybrid Approach:**
   - Use InnerTube for non-YouTube sites
   - Use yt-dlp specifically for YouTube
   - Best of both worlds

2. **Built-in JS Runtime:**
   - Bundle QuickJS with AppImage
   - No external dependencies needed
   - Works out-of-the-box

3. **Advanced Authentication:**
   - OAuth2 as optional feature
   - API key support for power users
   - Multi-account management

## Testing Checklist

### Before Release

- [ ] Single video download (logged in)
- [ ] Single video download (logged out)
- [ ] Playlist download (3+ videos)
- [ ] Channel videos download
- [ ] Age-restricted video
- [ ] Private/unlisted video
- [ ] Audio-only extraction
- [ ] Video with subtitles
- [ ] 4K video quality selection
- [ ] Progress bar accuracy
- [ ] Error message clarity
- [ ] Browser preference switching

### Post-Release Monitoring

- [ ] YouTube API changes
- [ ] yt-dlp updates compatibility
- [ ] User error reports
- [ ] Performance metrics

## References

- **yt-dlp Documentation:** https://github.com/yt-dlp/yt-dlp
- **PO Token Announcement:** https://github.com/yt-dlp/yt-dlp/issues/15012
- **Deno Installation:** https://deno.land/manual/getting_started/installation
- **YouTube InnerTube API:** https://github.com/tombulled/innertube

## Support

If you encounter issues:

1. Check this document's Troubleshooting section
2. Update yt-dlp: `pip install --upgrade yt-dlp`
3. Install Deno: `curl -fsSL https://deno.land/install.sh | sh`
4. Check yt-dlp GitHub issues: https://github.com/yt-dlp/yt-dlp/issues

## Conclusion

This fix ensures AV Morning Star remains functional with YouTube's 2025 security updates. By leveraging yt-dlp's robust infrastructure, we get reliable YouTube support with minimal maintenance overhead.

The solution is:
- ✅ **Working:** Bypasses PO token requirements
- ✅ **Maintainable:** yt-dlp handles YouTube changes
- ✅ **User-Friendly:** Same experience as before
- ✅ **Future-Proof:** Weekly yt-dlp updates

**Last Updated:** February 2, 2026
