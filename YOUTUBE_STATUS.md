# YouTube Download Status - February 2026

## Current Situation

As of February 2026, YouTube has significantly enhanced its anti-bot protection systems, affecting multiple download methods:

### Affected Methods
1. **yt-dlp** - "n-parameter challenge solving failed" errors
2. **InnerTube API** - "LOGIN_REQUIRED" / "Sign in to confirm you're not a bot" responses
3. **Direct API calls** - Bot detection across all client types (WEB, ANDROID, IOS, TV)

## What We've Implemented

### InnerTube API Integration ✓
- **Primary extractor**: `extractors/youtube.py` now uses Google's official InnerTube API
- **Library**: `innertube>=2.1.0` (added to requirements.txt)
- **Client types tested**: WEB, ANDROID, IOS, TVHTML5, EMBEDDED_PLAYER variants
- **Smart error detection**: Identifies bot protection and provides clear user messages

### Architecture Benefits
The InnerTube implementation provides:
- **Future-proof foundation**: When innertube library updates to bypass new protections, we're ready
- **Cleaner extraction**: Uses YouTube's official API endpoints (same as youtube.com)
- **No cookie dependency**: Designed to work without browser cookie extraction
- **Professional approach**: Mimics official YouTube clients (Android, iOS, TV)

## Why InnerTube?

InnerTube is YouTube's **internal API** used by:
- YouTube website
- YouTube mobile apps (Android/iOS)
- YouTube TV
- YouTube Music
- YouTube Kids

It's the most "official" way to access YouTube data, which makes it:
1. **More reliable** long-term than third-party scrapers
2. **Faster to adapt** when YouTube changes detection
3. **Less likely to break** than URL pattern matching
4. **Used by GrayJay** and other successful apps

## Current Workarounds

Since YouTube has extended bot protection to all methods:

### Option 1: Wait for Library Updates
- Monitor innertube library for updates
- Check yt-dlp GitHub for n-parameter fixes
- Usually resolves within days/weeks

### Option 2: Use Alternative Platforms
- **Odysee**: Works perfectly (tested ✓)
- **PeerTube**: Community-owned, no restrictions
- **LBRY**: Decentralized alternative

### Option 3: Manual Downloads
- Use browser extensions temporarily
- Save videos while logged into YouTube
- Limited by browser policies

## Testing Results

```bash
# InnerTube API Status (Feb 3, 2026)
WEB client: LOGIN_REQUIRED ("Sign in to confirm you're not a bot")
ANDROID client: LOGIN_REQUIRED (same message)
IOS client: LOGIN_REQUIRED (same message)
TVHTML5 client: LOGIN_REQUIRED (same message)
EMBEDDED clients: ERROR or 404

# This affects ALL videos, even:
- Public videos
- Unlisted videos  
- First YouTube video ever (jNQXAC9IVRw)
```

## What This Means for Users

### Short Term (Current)
- YouTube downloads temporarily unavailable
- Clear error messages explain the situation
- Odysee and other platforms work normally

### Medium Term (Days/Weeks)
- innertube library will likely be updated
- yt-dlp community will solve n-parameter challenge
- One or both methods will start working again

### Long Term (Permanent)
- We have InnerTube foundation ready
- Can quickly switch between methods
- Multi-backend fallback system possible

## Development Roadmap

### Phase 1: InnerTube Foundation ✓
- [x] Install innertube library
- [x] Create InnerTube-based YouTube extractor
- [x] Test multiple client types
- [x] Implement error detection
- [x] Document bot protection issue

### Phase 2: Multi-Backend System (Next)
- [ ] Implement fallback chain: InnerTube → yt-dlp → Alternative methods
- [ ] Add backend selection in UI
- [ ] Cache working backends
- [ ] Auto-retry with different methods

### Phase 3: Advanced Features (Future)
- [ ] Playlist support via InnerTube browse endpoint
- [ ] Channel video extraction
- [ ] Subtitle downloading
- [ ] Quality/format selection from InnerTube streams
- [ ] Direct stream download (bypass yt-dlp completely)

## Technical Details

### InnerTube API Endpoints
```python
client.player(video_id)         # Get video streams and metadata
client.browse(browse_id)        # Get channel/playlist content
client.next(video_id)           # Get related videos and comments
client.search(query)            # Search YouTube
client.get_transcript(params)   # Get video transcripts
```

### Client Types Implemented
```python
'ANDROID' - Android mobile app (best compatibility)
'IOS' - iPhone app
'WEB' - Standard web browser
'TVHTML5' - Smart TV web client
'WEB_EMBEDDED_PLAYER' - Embedded player
```

### Error Handling Flow
1. Detect playability status from InnerTube response
2. Check for LOGIN_REQUIRED, ERROR, or other issues
3. Provide user-friendly error message with context
4. Suggest alternative actions (Odysee, wait, etc.)

## References

- **InnerTube GitHub**: https://github.com/tombulled/innertube
- **GrayJay (uses InnerTube)**: https://github.com/futo-org/grayjay-android
- **yt-dlp Issues**: #15684 (n challenge solver)
- **YouTube API Docs**: No official InnerTube docs (reverse-engineered)

## Conclusion

While YouTube downloads are currently blocked by anti-bot protection, we've built a solid foundation using InnerTube API. This is the **correct long-term approach** because:

1. ✓ Uses YouTube's official internal API
2. ✓ Same method as successful apps like GrayJay
3. ✓ Will work when innertube library updates
4. ✓ More maintainable than cookie/scraping hacks
5. ✓ Professional, sustainable solution

The bot protection is a **temporary arms race** between YouTube and downloaders. Having InnerTube ready means we'll benefit immediately when the library is updated to bypass the new protections.
