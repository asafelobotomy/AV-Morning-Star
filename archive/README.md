# Archived Code

This folder contains deprecated implementations that have been superseded by better approaches.

## What's Here

### Deprecated YouTube Implementations

#### `youtube_innertube.py`
**Reason for Deprecation:** YouTube extended anti-bot protection to the InnerTube API  
**Replaced By:** `extractors/youtube_ytdlp.py` using yt-dlp backend  
**Status:** Archived Feb 2026 (v0.3.0)  
**Why It Failed:** InnerTube API was YouTube's internal API, but by early 2026, YouTube had implemented bot detection at the InnerTube level as well, making it unreliable.

#### `deprecated/youtube_oauth.py`
**Reason for Deprecation:** OAuth2 approach was overly complex and unreliable  
**Replaced By:** Browser cookie extraction via yt-dlp  
**Status:** Archived (proof-of-concept only)  
**Why It Failed:** Requires maintaining Google API credentials, handling token refresh, and managing complex OAuth flows. Browser cookie extraction via yt-dlp is simpler and more reliable.

#### `deprecated/download_icon.py`
**Purpose:** Icon download utility (superseded by SVG and PNG creation)  
**Status:** Archived

#### `deprecated/test_codecs.py`
**Purpose:** Codec compatibility testing (legacy testing approach)  
**Status:** Archived, replaced by `test.sh`

#### `deprecated/replace-icon.sh`
**Purpose:** Icon replacement script (no longer needed)  
**Status:** Archived

### Why Keep the Archive?

These files serve important purposes:

1. **Historical Reference**: Show what approaches were tried and why they failed
2. **Understanding Evolution**: Demonstrate how YouTube's anti-bot measures evolved and our responses
3. **Fallback Options**: Provides reference implementations if the current method breaks
4. **Learning Resource**: Valuable for understanding the technical challenges in video downloading

### When to Remove

The archive can be safely removed when:

- Minimum Python version is bumped significantly (e.g., 3.9 → 3.11+)
- A major version release occurs (e.g., v2.0.0)
- Disk space becomes a constraint in distribution
- yt-dlp adoption is 5+ years stable without major changes

### Important Notes

⚠️ **Do NOT attempt to resurrect InnerTube or OAuth implementations without updating yt-dlp alternatives first.** YouTube's anti-bot measures evolve rapidly, and reverting to older approaches will likely fail immediately.

✅ **The current approach (yt-dlp backend) is battle-tested** and handles:
- Proof of Origin (PO) Tokens
- JavaScript challenge solving
- Bot detection bypasses
- Browser cookie authentication
- 1000+ other video platforms

## Migration Timeline

| Version | Date | Change |
|---------|------|--------|
| 0.2.0 | Jan 2026 | Switched from InnerTube to yt-dlp backend |
| 0.2.5 | Jan 2026 | Removed OAuth2 implementation |
| 0.3.0 | Feb 2026 | Cleaned up and archived deprecated code |

## For Developers

If you're curious about how we got here:

1. Read [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for current system design
2. Review [docs/AUTHENTICATION_GUIDE.md](../docs/AUTHENTICATION_GUIDE.md) for current auth approach
3. Examine this archive to understand what didn't work and why

## Historical Documentation

The `docs/` subdirectory contains development notes from various implementation attempts:

- **INNERTUBE_GUIDE.md**: Early attempt at using InnerTube API
- **YOUTUBE_FIX_IMPLEMENTATION.md**: Implementation notes for YouTube bot detection fix
- **YOUTUBE_FIX_SOLUTION.md**: Solution research for YouTube PO token issue
- **YOUTUBE_FIX_SUMMARY.md**: Summary of YouTube authentication implementation
- **YOUTUBE_STATUS.md**: Status updates during YouTube fix development
- **OPTIMAL_SETUP_COMPLETE.md**: Setup completion documentation
- **READY_TO_USE.md**: Previous "ready to use" guide
- **NEXT_STEPS.txt**: Development roadmap notes

These document the evolution of the project and can serve as reference for understanding the YouTube anti-bot landscape.

## Contact

If you have questions about deprecated implementations or the evolution of this project, please refer to the GitHub issues or contact the maintainers.

### Development Documentation
Old development docs archived because:
- Implementation completed and stabilized
- Current documentation (ARCHITECTURE.md, AUTHENTICATION_GUIDE.md, etc.) is more comprehensive
- Historical value only - not needed for regular usage

## Current Documentation

For up-to-date information, see the main project documentation:

- **README.md**: Getting started and usage
- **ARCHITECTURE.md**: Technical architecture
- **AUTHENTICATION_GUIDE.md**: YouTube cookie authentication
- **SECURITY_AUDIT.md**: Security review
- **SMART_BROWSER_DETECTION.md**: Browser detection feature
- **CHANGELOG.md**: Version history

---

**Last Updated**: February 3, 2026  
**Archive Created**: Version 0.3.0 reorganization
