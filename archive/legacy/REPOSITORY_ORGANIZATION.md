# Repository Organization Guide

**Last Updated:** February 5, 2026  
**Version:** 0.3.0 (Reorganized)

---

## 📂 Directory Structure

```
AV-Morning-Star/
├── 📄 Core Application Files
│   ├── main.py                    # Main PyQt5 application (1595 lines)
│   ├── constants.py               # Application constants and configuration
│   ├── browser_utils.py           # Browser detection and cookie utilities
│   ├── create_icon.py             # Icon generation script
│   │
│   └── Extractors (modular download backends)
│       └── extractors/
│           ├── __init__.py        # Factory function (get_extractor)
│           ├── base.py            # BaseExtractor (common interface)
│           ├── youtube_ytdlp.py   # YouTube with PO token support
│           ├── odysee.py          # Odysee/LBRY platform
│           └── generic.py         # Fallback for 1000+ sites
│
├── 📚 User Documentation
│   ├── README.md                  # Main user guide (clean, professional)
│   ├── CHANGELOG.md               # Version history and release notes
│   └── docs/
│       ├── README.md              # Documentation index
│       ├── ARCHITECTURE.md        # Technical system design
│       ├── AUTHENTICATION_GUIDE.md # YouTube auth explanation
│       ├── GETTING_STARTED.md     # Beginner tutorial
│       ├── PROJECT_STRUCTURE.md   # Complete file organization
│       ├── SECURITY_AUDIT.md      # 8000+ word security review
│       ├── SECURITY_AND_PRIVACY.md # User-friendly security guide
│       ├── SMART_BROWSER_DETECTION.md # Auto-detection feature guide
│       ├── CONSTANTS.md           # Constants documentation
│       └── REORGANIZATION.md      # v0.3.0 reorganization notes
│
├── 🛠️ Build & Deployment
│   ├── start.sh                   # Quick start script (recommended)
│   ├── test.sh                    # Test runner script
│   ├── build-appimage.sh          # Build portable AppImage
│   ├── VERSION                    # Version file (0.3.0)
│   ├── requirements.txt           # Python dependencies (5 packages)
│   ├── av-morning-star.desktop    # Desktop entry file
│   ├── av-morning-star.png        # Application icon
│   │
│   └── Configuration
│       └── .gitignore             # Git ignore rules (comprehensive)
│
├── 📦 Archive (Historical & Deprecated)
│   ├── README.md                  # Archive index and explanation
│   ├── backup/                    # Backup implementations
│   │   └── youtube.py.backup      # Previous YouTube extractor
│   │
│   ├── deprecated/                # Legacy code (no longer used)
│   │   ├── youtube_oauth.py       # OAuth2 approach (too complex)
│   │   ├── download_icon.py       # Icon download (superseded)
│   │   ├── test_codecs.py         # Legacy codec testing
│   │   └── replace-icon.sh        # Icon replacement (obsolete)
│   │
│   ├── reports/                   # Code analysis & review (v0.3.0)
│   │   ├── CODE_REVIEW_REPORT.md  # Comprehensive audit
│   │   ├── IMPLEMENTATION_REPORT.md # Fix implementation details
│   │   ├── FINAL_VERIFICATION_REPORT.md # Final verification
│   │   ├── README_IMPROVEMENTS.md # README enhancement analysis
│   │   └── README_REVIEW_SUMMARY.md # README review summary
│   │
│   ├── docs/                      # Historical development docs
│   │   ├── INNERTUBE_GUIDE.md
│   │   ├── YOUTUBE_FIX_*.md       # YouTube fix development notes
│   │   ├── OPTIMAL_SETUP_COMPLETE.md
│   │   ├── READY_TO_USE.md
│   │   └── NEXT_STEPS.txt
│   │
│   └── scripts/                   # Historical scripts
│
└── 🔧 Version Control
    ├── .git/                      # Git repository
    └── .github/                   # GitHub configuration
        └── copilot-instructions.md # AI coding agent instructions
```

---

## 🎯 File Organization Principles

### Root Level – Keep It Clean
Only essential application files and documentation:
- ✅ Application code (main.py, constants.py, etc.)
- ✅ User documentation (README.md, CHANGELOG.md)
- ✅ Build scripts (start.sh, build-appimage.sh)
- ✅ Configuration (requirements.txt, .gitignore)

### `docs/` – User-Facing Documentation
All user guides and technical documentation:
- ✅ Setup guides (GETTING_STARTED.md)
- ✅ Technical documentation (ARCHITECTURE.md)
- ✅ Security guides (SECURITY_AUDIT.md)
- ✅ Feature explanations (SMART_BROWSER_DETECTION.md)

### `archive/` – Historical & Deprecated
Organized by purpose for easy reference:
- ✅ `backup/` – Alternative implementations
- ✅ `deprecated/` – Legacy code not in use
- ✅ `reports/` – Analysis and review documents
- ✅ `docs/` – Historical development notes
- ✅ `scripts/` – Old utility scripts

### `extractors/` – Modular Download Backends
Platform-specific extractors following the factory pattern:
- ✅ Consistent interface (inherit from BaseExtractor)
- ✅ Easy to extend (add new platform in 4 steps)
- ✅ Clean separation of concerns

---

## 📋 What's in Each Key File

### Application Core

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | 1595 | Main PyQt5 GUI, threading, preferences |
| `constants.py` | 431 | All UI strings, configuration, defaults |
| `browser_utils.py` | 116 | Browser detection, cookie extraction |
| `create_icon.py` | ~100 | SVG/PNG icon creation |

### Extractors

| File | Lines | Purpose |
|------|-------|---------|
| `extractors/base.py` | 439 | Common interface, audio/video filters |
| `extractors/youtube_ytdlp.py` | 290 | YouTube with PO token support |
| `extractors/odysee.py` | ~150 | Odysee/LBRY platform |
| `extractors/generic.py` | ~150 | 1000+ other platforms fallback |
| `extractors/__init__.py` | ~40 | Factory pattern implementation |

### Documentation

| File | Type | Audience |
|------|------|----------|
| `README.md` | User guide | All users |
| `CHANGELOG.md` | Release notes | Users/developers |
| `docs/ARCHITECTURE.md` | Technical | Developers |
| `docs/GETTING_STARTED.md` | Tutorial | New users |
| `docs/SECURITY_AUDIT.md` | Security | Security-conscious users |

### Build & Deployment

| File | Purpose |
|------|---------|
| `start.sh` | Quick start (recommended) |
| `test.sh` | Run tests |
| `build-appimage.sh` | Build portable executable |
| `requirements.txt` | Python dependencies (5 packages) |
| `VERSION` | Version identifier (0.3.0) |

---

## 🗂️ Archive Organization

### Why Organized This Way?

1. **`backup/`** – Quick access to previous implementations
2. **`deprecated/`** – Clearly marked as "not in use"
3. **`reports/`** – Separated from code for clarity
4. **`docs/`** – Historical development notes together
5. **`scripts/`** – Legacy build/utility scripts

### Archive Index

The `archive/README.md` contains:
- ✅ Directory map
- ✅ Explanation of each file
- ✅ Why things were deprecated
- ✅ When it's safe to remove
- ✅ Historical context

---

## 🚀 What Changed in v0.3.0

### Reorganization Summary

| Item | Before | After | Benefit |
|------|--------|-------|---------|
| Review reports | Root level | `archive/reports/` | Cleaner root |
| Backup files | Scattered | `archive/backup/` | Easy to find |
| Old code | Mixed with active | `archive/deprecated/` | Clear separation |
| .gitignore | Basic | Comprehensive | Better control |
| Archive docs | Minimal | Detailed index | Better context |

### Files Moved to Archive

**Reports (→ `archive/reports/`):**
- CODE_REVIEW_REPORT.md
- IMPLEMENTATION_REPORT.md
- FINAL_VERIFICATION_REPORT.md
- README_IMPROVEMENTS.md
- README_REVIEW_SUMMARY.md

**Backups (→ `archive/backup/`):**
- youtube.py.backup (from extractors/)

### Improved .gitignore

Added:
- ✅ `.mypy_cache/` – Type checking
- ✅ `.dmypy.json` – MyPy cache
- ✅ `.env` – Environment variables
- ✅ `.coverage` – Test coverage

Clarified:
- ✅ Build artifacts
- ✅ AppImage build files
- ✅ IDE specific files

---

## 📊 Repository Size Impact

### Root Level (Clean)
- Essential files only
- ~25 files total
- Professional appearance

### Archive (Organized)
- Reports: 5 files
- Deprecated: 5 files
- Historical docs: 8 files
- Total: ~18 files (organized by purpose)

### Total Footprint
- Application: ~80 KB (Python + extractors)
- Documentation: ~500 KB (including archive)
- Reasonable for version control

---

## ✅ Verification Checklist

- [x] Root level is clean (only essential files)
- [x] Review reports moved to archive/reports/
- [x] Backup files moved to archive/backup/
- [x] Deprecated code organized clearly
- [x] .gitignore is comprehensive
- [x] Archive README is detailed
- [x] Documentation is well-indexed
- [x] All links are valid
- [x] No orphaned files

---

## 🎯 Quick Navigation

### For New Users
→ Start with [README.md](README.md)

### For Setup
→ Follow [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)

### For Developers
→ Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

### For Detailed History
→ Check [archive/README.md](archive/README.md)

### For YouTube Auth
→ See [docs/AUTHENTICATION_GUIDE.md](docs/AUTHENTICATION_GUIDE.md)

### For Security
→ Review [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md)

---

## 🔐 Git Notes

All files (including archive) are committed to version control. This is intentional:

### What's Tracked
- ✅ All source code
- ✅ All documentation
- ✅ Archive (for history)
- ✅ Configuration files

### What's Ignored (Not Tracked)
- ❌ Python cache (`__pycache__/`, `.pyc`)
- ❌ Virtual environment (`.venv/`)
- ❌ Build artifacts (`build/`, `dist/`)
- ❌ IDE files (`.vscode/`, `.idea/`)
- ❌ OS files (`.DS_Store`, `Thumbs.db`)

See [.gitignore](.gitignore) for complete list.

---

## 📝 Maintenance Notes

### Regular Tasks
- Keep archive README updated with new changes
- Move reports to archive after version release
- Clean up any temporary files regularly
- Update documentation links

### Version Releases
1. Update VERSION file
2. Update CHANGELOG.md
3. Move analysis reports to archive/reports/
4. Tag release in Git

### Long-term Cleanup
- Archive can be cleared after v2.0.0 release
- Deprecated code can be removed after 2+ major versions
- Historical docs can be archived to separate repo if needed

---

## 🤝 Contributing

When organizing new files:
1. Keep root level for active application code
2. Put documentation in `docs/`
3. Move old code to `archive/` with explanation
4. Update this guide and archive/README.md
5. Update .gitignore as needed

---

<div align="center">

**Repository Organization**

*Clean structure, easy navigation, professional appearance*

AV Morning Star v0.3.0 – Well-Organized Project

</div>
