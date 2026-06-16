# AV Morning Star — Project Structure

**Version:** 0.4.0

```
AV-Morning-Star/
├── main.py                 # PyQt5 GUI entry point
├── threads.py              # URLScraperThread, DownloadThread
├── dialogs.py              # PreferencesDialog
├── settings.py             # QSettings persistence
├── browser_utils.py        # Browser detection and cookie helpers
├── constants.py            # Shared strings and defaults
├── themes.py               # Dark/light QSS themes
├── start.sh                # Dev launcher (venv + deps + run)
├── requirements.txt        # Runtime dependencies (pinned)
├── requirements-lock.txt   # Transitive runtime lockfile
├── VERSION                 # Release version (synced with constants.py)
├── SECURITY.md             # Security policy
├── README.md               # User-facing documentation
├── CHANGELOG.md            # Release notes
│
├── extractors/             # Platform-specific download logic
│   ├── __init__.py         # get_extractor() factory
│   ├── base.py             # BaseExtractor + FFmpeg filter options
│   ├── youtube_ytdlp.py    # YouTube (cookies, PO tokens via yt-dlp)
│   ├── odysee.py           # Odysee/LBRY
│   ├── podcast_page.py     # Direct-download podcast pages
│   └── generic.py          # Fallback for all other yt-dlp sites
│
├── tests/                  # unittest suite (133 tests)
│   ├── test_extractors.py
│   ├── test_main_logic.py
│   ├── test_browser_utils.py
│   └── test_settings.py
│
├── scripts/
│   ├── build-appimage.sh   # Reproducible AppImage build
│   ├── create_icon.py      # Icon generator
│   └── test.sh             # Local smoke test (imports + unit tests)
│
├── packaging/              # Linux desktop integration
│   ├── com.github.asafelobotomy.avmorningstar.desktop
│   └── com.github.asafelobotomy.avmorningstar.appdata.xml
│
├── docs/                   # Documentation (this folder)
└── .github/workflows/      # CI (tests + pip-audit)
    └── ci.yml
```

## Module roles

| Module | Purpose |
|--------|---------|
| `main.py` | UI, fetch/download orchestration, auth policy |
| `threads.py` | Background metadata fetch and download workers |
| `dialogs.py` | Preferences UI |
| `settings.py` | Persist auth mode, theme, output directory |
| `browser_utils.py` | Detect installed browsers; probe cookies only when consented |
| `extractors/` | Map URLs → yt-dlp options per platform |

## Build outputs (gitignored)

- `build/`, `dist/`, `*.AppImage` — AppImage build artifacts
- `.venv/` — local virtual environment
- `appimagetool-x86_64.AppImage` — downloaded build tool

Historical code and superseded docs were removed from the tree; use `git log` if you need prior implementations (InnerTube, OAuth, old reports).
