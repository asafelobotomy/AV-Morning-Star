# YouTube Download Fix - February 2026

## Problem Analysis

YouTube has implemented **Proof of Origin (PO) Tokens** system that requires:
1. **External JavaScript Runtime** (Deno, Node.js, QuickJS, or Bun)
2. **PO Token Generation** for each request
3. **visitor_data** and **data_sync_id** parameters
4. **Browser cookies** alone are insufficient

### Current Implementation Issues:
- **InnerTube API** (via `innertube` library) cannot generate PO tokens
- **Browser cookies** extraction works but YouTube still blocks requests
- **No JS runtime** to execute YouTube's challenge code

## Solution: Use yt-dlp as Backend

**yt-dlp** has solved this problem by:
1. Supporting external JS runtimes (Deno, Node.js, etc.)
2. Automatically generating PO tokens when needed
3. Handling all YouTube bot detection mechanisms
4. Providing stable extraction via `--cookies-from-browser`

### Why yt-dlp is the Best Solution:
- ✅ **Actively maintained** - Updated weekly to combat YouTube changes
- ✅ **Built-in JS runtime support** - Handles PO token generation
- ✅ **Cookie extraction** - Already has robust browser cookie support
- ✅ **Battle-tested** - Used by millions, constantly adapting to YouTube
- ✅ **Python API** - Can be used programmatically

## Implementation Strategy

### Phase 1: Add yt-dlp as Fallback (RECOMMENDED)
Keep InnerTube for non-YouTube sites, use yt-dlp specifically for YouTube:

```python
def extract_info(self):
    """Extract video info - use yt-dlp for YouTube"""
    if 'youtube.com' in self.url or 'youtu.be' in self.url:
        return self._extract_with_ytdlp()
    else:
        return self._extract_with_innertube()  # Other sites

def _extract_with_ytdlp(self):
    """Use yt-dlp for YouTube extraction"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'cookiesfrombrowser': (self.cookies_from_browser,) if self.cookies_from_browser else None,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(self.url, download=False)
        # Convert to our format
        return self._convert_ytdlp_info(info)
```

### Phase 2: Install JavaScript Runtime
For best results, install **Deno** (recommended by yt-dlp):

```bash
# Linux
curl -fsSL https://deno.land/install.sh | sh

# Or add to requirements
echo "yt-dlp-ejs>=1.0" >> requirements.txt
```

### Phase 3: Update YouTube Extractor

See `extractors/youtube_ytdlp.py` for full implementation.

## GrayJay's Approach (For Reference)

GrayJay uses **JavaScript plugin system** where each platform has a custom extractor:
- Extractors run in a sandboxed V8/JavaScript environment
- Each plugin implements `getContentDetails()`, `getVideoSources()`, etc.
- Uses platform-specific tricks (user agents, tokens, API endpoints)
- For YouTube: Uses multiple client types (Android, iOS, TV) with rotation

**Why we can't replicate this exactly:**
- GrayJay is Android-native with embedded V8
- Their YouTube plugin is 2000+ lines of JavaScript
- Requires constant maintenance as YouTube changes
- We'd essentially be recreating yt-dlp

## Recommended Implementation

### Option A: yt-dlp Backend (RECOMMENDED)
**Pros:**
- ✅ Works immediately
- ✅ No maintenance burden
- ✅ Handles all edge cases
- ✅ Future-proof

**Cons:**
- ⚠️ Dependency on external tool
- ⚠️ Less control over extraction

### Option B: Hybrid Approach
**Pros:**
- ✅ Fast InnerTube for simple videos
- ✅ yt-dlp fallback for protected content
- ✅ Best of both worlds

**Cons:**
- ⚠️ More complex code
- ⚠️ Need to detect when to use which

### Option C: Full InnerTube + JS Runtime
**Pros:**
- ✅ Complete control
- ✅ No yt-dlp dependency

**Cons:**
- ❌ Must implement PO token generation
- ❌ Must maintain as YouTube evolves
- ❌ Requires JS runtime integration
- ❌ Essentially recreating yt-dlp

## Implementation Plan

1. **Immediate Fix** (Today):
   - Switch YouTubeExtractor to use yt-dlp backend
   - Keep same interface so main.py doesn't need changes
   - Test with problematic URLs

2. **Short Term** (This Week):
   - Add Deno installation to setup
   - Update documentation
   - Test with various video types

3. **Long Term** (Optional):
   - Implement hybrid approach if needed
   - Add progress callbacks for large playlists
   - Cache extraction results

## Files to Modify

1. `extractors/youtube.py` - Rewrite to use yt-dlp backend
2. `requirements.txt` - Ensure yt-dlp is latest version
3. `start.sh` - Add Deno installation check
4. `README.md` - Update with YouTube requirements

## Testing Checklist

- [ ] Single video download
- [ ] Playlist download
- [ ] Channel video extraction
- [ ] Age-restricted videos
- [ ] Private/unlisted videos (with cookies)
- [ ] Live streams
- [ ] Premieres

## References

- yt-dlp announcement: https://github.com/yt-dlp/yt-dlp/issues/15012
- PO Token documentation: https://github.com/yt-dlp/yt-dlp/wiki/EJS
- GrayJay source: https://github.com/futo-org/grayjay-android
- yt-dlp cookies wiki: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp
