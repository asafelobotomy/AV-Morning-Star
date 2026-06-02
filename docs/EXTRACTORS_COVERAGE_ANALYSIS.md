# Extractors Coverage Analysis

**Date:** February 5, 2026  
**Status:** Review & Recommendations

---

## Current Extractor Status

### Active Extractors

| Extractor | Sites | Purpose | Status |
|-----------|-------|---------|--------|
| **youtube_ytdlp.py** | YouTube, YouTube Music | Dedicated YouTube extractor with PO token support | ✅ SPECIALIZED |
| **odysee.py** | Odysee, LBRY | Dedicated Odysee/LBRY extractor | ✅ SPECIALIZED |
| **podcast_page.py** | Podcast/media pages | Direct-download pages serving audio/video files | ✅ SPECIALIZED |
| **generic.py** | 1000+ other sites | Fallback using yt-dlp backend | ✅ CATCH-ALL |
| **base.py** | All platforms | Common base class with shared logic | ✅ FOUNDATION |

### Current Architecture

```
Factory Function (get_extractor)
├── youtube.com / youtu.be
│   └── YouTubeExtractor (dedicated handler)
├── odysee.com / lbry.tv
│   └── OdyseeExtractor (dedicated handler)
├── podcast/media pages (direct audio/video URLs)
│   └── PodcastPageExtractor (direct-download handler)
└── Everything else
    └── GenericExtractor (fallback to yt-dlp)
```

---

## Top Video/Audio Sharing Platforms

### Tier 1: MEGA Platforms (100M+ daily users)

| Platform | Users | Audio | Video | Current Handler | Needs Dedicated? |
|----------|-------|-------|-------|-----------------|------------------|
| **YouTube** | 2.5B+ | ✓ (YouTube Music) | ✓ | YouTubeExtractor | ✅ YES (HAS IT) |
| **TikTok** | 1B+ | ✓ | ✓ | GenericExtractor | ⚠️ MAYBE |
| **Instagram** | 2B+ | ✓ (Reels, Stories) | ✓ | GenericExtractor | ⚠️ MAYBE |
| **Facebook/Meta** | 3B+ | ✓ (Watch, Stories) | ✓ | GenericExtractor | ⚠️ MAYBE |
| **Twitter/X** | 550M+ | ✓ (Spaces) | ✓ | GenericExtractor | ⚠️ MAYBE |

### Tier 2: Major Platforms (10M-100M daily users)

| Platform | Users | Audio | Video | Current Handler | Needs Dedicated? |
|----------|-------|-------|-------|-----------------|------------------|
| **Twitch** | 150M+ | ✓ | ✓ | GenericExtractor | ⚠️ MAYBE |
| **Vimeo** | 260M+ | ✓ | ✓ | GenericExtractor | ⚠️ MAYBE |
| **Reddit** | 430M+ | ✓ (some) | ✓ | GenericExtractor | ⚠️ MAYBE |
| **Rumble** | 50M+ | ✓ | ✓ | GenericExtractor | ⚠️ MAYBE |
| **DailyMotion** | 300M+ | ✓ | ✓ | GenericExtractor | ⚠️ MAYBE |
| **Odysee/LBRY** | 10M+ | ✓ | ✓ | OdyseeExtractor | ✅ YES (HAS IT) |

### Tier 3: Specialized Platforms (1M-10M daily users)

| Platform | Type | Current Handler | Needs Dedicated? |
|----------|------|-----------------|------------------|
| **BitChute** | Video alternative | GenericExtractor | ❌ NO (works fine) |
| **Rumble Clips** | Short video | GenericExtractor | ❌ NO (works fine) |
| **Kick** | Live streaming | GenericExtractor | ⚠️ MAYBE |
| **Patreon** | Audio/video | GenericExtractor | ⚠️ MAYBE |
| **Bandcamp** | Audio | GenericExtractor | ⚠️ MAYBE |
| **SoundCloud** | Audio | GenericExtractor | ❌ NO (yt-dlp handles well) |
| **Spotify** | Audio | GenericExtractor | ❌ NO (DRM-protected) |

---

## Analysis: When Do You Need a Dedicated Extractor?

### ✅ Good Reasons for Dedicated Extractor

1. **Authentication Required**
   - Special login needs (YouTube cookies, Twitch OAuth, etc.)
   - Browser-based authentication
   - Platform-specific APIs

2. **Bot Detection / Anti-Scraping**
   - JavaScript challenges (YouTube PO tokens)
   - Rate limiting that needs special handling
   - Geo-blocking or region restrictions

3. **Special Quality/Format Handling**
   - Platform-specific quality naming
   - Unique format selections
   - HLS vs DASH differences

4. **Complex Metadata**
   - Non-standard title/duration formats
   - Special subtitle requirements
   - Custom filename templating

5. **Live Stream Handling**
   - Special live stream logic (Twitch, Kick)
   - Live chat archiving
   - Segment handling

### ❌ Reasons Generic Handler Works Fine

1. **yt-dlp Already Handles It**
   - Modern yt-dlp supports 1000+ sites
   - Constantly updated to handle anti-bot measures
   - Works without special authentication

2. **Simple Extraction Needs**
   - Standard video/audio extraction
   - No special quality selection needed
   - Default formats work well

3. **Low Volume Usage**
   - Not main focus of application
   - Occasional downloads are fine
   - Don't need performance optimization

---

## Detailed Recommendations

### 🔴 HIGH PRIORITY: Consider Dedicated Extractors

#### 1. **Twitch** (150M+ daily users, live streaming)
**Why:** 
- Live streaming is complex (segments, quality variants)
- VOD vs Live stream different handling
- Rate limiting can be aggressive
- Requires OAuth for some content

**Current Status:** GenericExtractor works but...
- May struggle with live streams
- Quality selection could be better
- Rate limiting not optimized

**Effort:** Medium (1-2 hours)

**Recommendation:** ✅ **CREATE DEDICATED EXTRACTOR**

---

#### 2. **TikTok** (1B+ daily users, but restricted)
**Why:**
- Aggressive bot detection
- China-based company (extra restrictions)
- Multiple authentication layers
- yt-dlp constantly fighting this

**Current Status:** GenericExtractor works intermittently
- High failure rate (TikTok actively blocks)
- Often requires proxy/VPN
- Quality options limited

**Effort:** High (2-3 hours, may require Deno)

**Recommendation:** ⚠️ **MAYBE - Low ROI (TikTok actively prevents scraping)**

---

#### 3. **Instagram/Meta** (2B+ daily users)
**Why:**
- Meta actively fights automation
- Requires authentication for many videos
- Instagram Reels vs Stories vs Posts different
- Region-specific restrictions

**Current Status:** GenericExtractor works for public content
- Problems: Private/restricted content
- Story downloading very limited
- Reels quality options limited

**Effort:** High (2-3 hours)

**Recommendation:** ⚠️ **MAYBE - Medium ROI (Meta actively blocks)**

---

#### 4. **Vimeo** (260M+ monthly visitors)
**Why:**
- Popular for professional creators
- Multiple subscription levels (Free, Plus, Pro)
- Different quality/features per tier
- Some content restricted by uploader

**Current Status:** GenericExtractor works for public content
- Free tier works fine
- Pro content requires special handling
- Embed restrictions complex

**Effort:** Low-Medium (1-2 hours)

**Recommendation:** ✅ **CONSIDER (High ROI for professional creators)**

---

#### 5. **Twitter/X** (550M+ daily users)
**Why:**
- X recently restricted API
- Video extraction still complex
- Different quality options
- Rate limiting aggressive

**Current Status:** GenericExtractor works but...
- Quality options limited
- Often hits rate limits
- Requires special handling for Spaces

**Effort:** Medium (1-2 hours)

**Recommendation:** ⚠️ **MAYBE (Medium ROI, requires careful implementation)**

---

### 🟡 MEDIUM PRIORITY: Monitor

#### Reddit (430M+ daily users)
- GenericExtractor works for most videos
- Some communities restrict downloads
- Could benefit from account-based access
- **Recommendation:** Monitor, add if issues arise

#### DailyMotion (300M+ monthly)
- GenericExtractor works well
- Not heavily restricted
- **Recommendation:** Keep generic, no dedicated needed

#### Rumble (50M+ users)
- GenericExtractor works well
- Conservative, user-friendly platform
- **Recommendation:** Keep generic, no dedicated needed

---

### 🟢 LOW PRIORITY: Keep Generic

#### YouTube Music
- Already handled by YouTube extractor
- No separate extractor needed

#### SoundCloud
- yt-dlp handles it well
- No special needs

#### Bandcamp
- yt-dlp handles it well
- No special needs

#### Other 900+ Sites
- GenericExtractor + yt-dlp works fine
- No dedicated extractors needed

---

## Recommended Implementation Plan

### Phase 1: IMMEDIATE (v0.4.0)
```
1. ✅ Keep current setup (YouTube, Odysee, Generic)
2. ✅ Monitor TikTok/Instagram/Facebook issues
3. ✅ Improve error messages from GenericExtractor
```

### Phase 2: SHORT TERM (v0.5.0)
```
If issues arise with popular platforms:
- Twitch: Create twitch.py
- Vimeo: Create vimeo.py
```

### Phase 3: MEDIUM TERM (v1.0.0)
```
If significant demand:
- Twitter/X: Create twitter.py
- Reddit: Create reddit.py
```

### Phase 4: LONG TERM (v2.0.0+)
```
Only if major changes happen:
- Platform-specific authentication
- New bot detection methods
- Regional variations
```

---

## Implementation Approach

### For Twitch (Best Candidate)

**What a dedicated Twitch extractor would do:**

```python
class TwitchExtractor(BaseExtractor):
    def extract_info(self):
        """
        Extract info for:
        - VODs (archived streams)
        - Clips
        - Live broadcasts
        - Channel content
        """
        
    def get_download_opts(self):
        """
        Handle Twitch-specific options:
        - Quality selection (bandwidth, resolution)
        - Format handling (HLS vs DASH)
        - Segment management
        - Rate limiting
        """
```

### For Vimeo (Medium Complexity)

**What a dedicated Vimeo extractor would do:**

```python
class VimeoExtractor(BaseExtractor):
    def extract_info(self):
        """
        Extract info for:
        - Free videos (always available)
        - Plus-only content (needs account)
        - Pro-only content (subscription)
        """
        
    def get_download_opts(self):
        """
        Handle Vimeo-specific:
        - Quality selection
        - Embed restrictions
        - Account-based features
        """
```

---

## Factory Function Update

When/if you add new extractors:

```python
def get_extractor(url, cookies_from_browser=None):
    url_lower = url.lower()
    
    # YouTube
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return YouTubeExtractor(url, cookies_from_browser=cookies_from_browser)
    
    # Odysee
    elif 'odysee.com' in url_lower or 'lbry.tv' in url_lower:
        return OdyseeExtractor(url)
    
    # Twitch (if added in v0.5.0)
    # elif 'twitch.tv' in url_lower:
    #     return TwitchExtractor(url)
    
    # Vimeo (if added in v0.5.0)
    # elif 'vimeo.com' in url_lower:
    #     return VimeoExtractor(url)
    
    # Generic fallback
    else:
        return GenericExtractor(url)
```

---

## Current Design Assessment

### ✅ Strengths

1. **Modular & Extensible**
   - Easy to add new extractors
   - Factory pattern works well
   - Clear inheritance structure

2. **Smart Defaults**
   - GenericExtractor handles 1000+ sites
   - BaseExtractor provides common functionality
   - No need for platform-specific boilerplate

3. **Balanced Approach**
   - Specialized extractors for complex platforms (YouTube, Odysee)
   - Generic fallback for others
   - Avoids over-engineering

### 🟡 Areas for Improvement

1. **Error Handling**
   - Could provide better site-specific error messages
   - GenericExtractor might benefit from better diagnostics

2. **Quality Selection**
   - Some platforms have unique quality naming
   - Could improve format detection

3. **Authentication**
   - Only YouTube has auth currently
   - Other platforms may need OAuth support

### 🎯 Verdict

**Your current architecture is EXCELLENT for a general-purpose tool.**

- ✅ YouTube: Specialized (complex authentication, bot detection)
- ✅ Odysee: Specialized (supports alternative platform)
- ✅ 1000+ others: Generic handler (works for 90%+ of cases)

**Current coverage is actually ideal:**
- Not over-engineered
- Easy to maintain
- Works for most users
- Room to add dedicated extractors when needed

---

## What I Recommend

### ✅ DO THIS NOW
- Keep current 2 dedicated extractors (YouTube, Odysee)
- Keep GenericExtractor as catch-all
- Document that yt-dlp supports 1000+ sites

### ✅ DO THIS IF ISSUES ARISE
- Monitor GitHub issues for platform-specific failures
- Add dedicated Twitch extractor if live streaming becomes critical
- Add dedicated Vimeo if professional creators complain

### ❌ DON'T DO THIS NOW
- Add extractors for TikTok, Instagram, Facebook (they actively block)
- Over-engineer for platforms that work fine with generic handler
- Create extractors without clear performance benefit

### 📊 Future Decision Tree

```
User reports site doesn't work:
├─ Is it in yt-dlp's supported list? 
│  ├─ Yes → Update yt-dlp (it handles it)
│  └─ No → Site not supported, explain limitation
│
├─ Does GenericExtractor fail for specific reason?
│  ├─ Authentication needed → Add dedicated extractor
│  ├─ Quality options limited → Enhance GenericExtractor
│  ├─ Rate limiting → Add retry logic to base
│  └─ Format issues → Improve error messages
│
└─ Is it a popular site (10M+ users)?
   ├─ Yes → Consider dedicated extractor in next version
   └─ No → Keep as generic, document limitation
```

---

<div align="center">

**Current Extractor Design: EXCELLENT ✅**

*Simple • Maintainable • Extensible • Future-Proof*

Add dedicated extractors when needed, not before.

</div>
