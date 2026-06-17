# AV Morning Star — Project Structure

**Version:** 0.4.1

```
AV-Morning-Star/
├── main.py                 # PyQt5 GUI entry point
├── threads.py              # URLScraperThread, DownloadThread
├── dialogs.py              # PreferencesDialog
├── ui_widgets.py           # FlowLayout, VideoCheckbox, pixmap helpers
├── settings.py             # QSettings persistence
├── browser_utils.py        # Browser detection and cookie helpers
├── constants.py            # Shared strings and defaults
├── themes.py               # Dark/light QSS themes
├── pyproject.toml          # Ruff lint configuration
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
│   ├── podcast_page.py     # Direct-download podcast pages
│   └── generic.py          # Odysee + all other yt-dlp sites
│
├── tests/                  # unittest suite
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
├── docs/                   # Documentation
└── .github/
    ├── workflows/ci.yml    # Tests, ruff, pip-audit
    └── dependabot.yml      # Weekly dependency updates
```

Historical code and superseded docs were removed; use `git log` for prior implementations.
