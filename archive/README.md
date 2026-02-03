# Archive

This directory contains old documentation and deprecated code from the development process of AV Morning Star.

## Directory Structure

```
archive/
├── docs/              # Old development documentation
├── deprecated/        # Deprecated scripts and code
└── scripts/           # Old utility scripts
```

## Documentation Archive (`docs/`)

Historical documentation from development phases:

- **INNERTUBE_GUIDE.md**: Early attempt at using InnerTube API (replaced by yt-dlp backend)
- **YOUTUBE_FIX_IMPLEMENTATION.md**: Implementation notes for YouTube bot detection fix
- **YOUTUBE_FIX_SOLUTION.md**: Solution research for YouTube PO token issue
- **YOUTUBE_FIX_SUMMARY.md**: Summary of YouTube authentication implementation
- **YOUTUBE_STATUS.md**: Status updates during YouTube fix development
- **OPTIMAL_SETUP_COMPLETE.md**: Setup completion documentation
- **READY_TO_USE.md**: Previous "ready to use" guide
- **NEXT_STEPS.txt**: Development roadmap notes

## Deprecated Code (`deprecated/`)

Code that has been replaced or is no longer used:

- **youtube_oauth.py**: OAuth2 authentication attempt (rejected as too complex)
- **download_icon.py**: Old icon download script
- **replace-icon.sh**: Icon replacement utility
- **test_codecs.py**: Codec testing script

## Why These Files Were Archived

### InnerTube Replacement
The InnerTube API approach was replaced with yt-dlp backend because:
- InnerTube cannot generate YouTube Proof of Origin (PO) tokens
- yt-dlp has better bot detection bypass
- yt-dlp supports remote components for JavaScript challenge solving
- More reliable long-term solution

### OAuth2 Rejection
OAuth2 authentication was implemented but removed because:
- Required Google Cloud Console setup (too complex for average users)
- Needed client ID/secret management
- Browser cookie method is simpler and more user-friendly
- OAuth2 still subject to YouTube rate limiting

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
