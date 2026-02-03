# Constants Library Documentation

**Version**: 0.3.0  
**Module**: `constants.py`

## Overview

The `constants.py` module centralizes all commonly used strings, configuration values, and application settings. This provides:

- **Consistency**: Single source of truth for all terminology
- **Maintainability**: Update in one place, reflect everywhere
- **Future-proofing**: Easy to add internationalization/localization
- **Type safety**: Clear naming conventions and organization

## Usage

### Importing

```python
# Import all constants
from constants import *

# Or import specific constants
from constants import APP_NAME, APP_VERSION, MAIN_WINDOW_TITLE
```

### Examples

```python
# Window titles
self.setWindowTitle(MAIN_WINDOW_TITLE)

# Button labels
btn = QPushButton(BTN_DOWNLOAD_SELECTED)

# Status messages
self.status_label.setText(STATUS_READY)

# Configuration
self.output_path = os.path.expanduser(DEFAULT_OUTPUT_DIR)
```

## Categories

### Application Identity
- `APP_NAME` - Application name
- `APP_VERSION` - Current version
- `APP_SUBTITLE` - Tagline
- `APP_COPYRIGHT` - Copyright notice
- `APP_DESCRIPTION` - Short description

### Window Titles
- `MAIN_WINDOW_TITLE` - Main window
- `ABOUT_WINDOW_TITLE` - About dialog
- `HELP_WINDOW_TITLE` - Help dialog
- `PREFERENCES_WINDOW_TITLE` - Preferences dialog

### Menu Items
- `MENU_TOOLS` - "Tools" menu
- `MENU_PREFERENCES` - "Preferences" action
- `MENU_ABOUT` - "About" action
- `MENU_HELP` - "Help" action

### Button Labels
- `BTN_FETCH` - "Fetch" button
- `BTN_DOWNLOAD_SELECTED` - "Download Selected" button
- `BTN_SELECT_ALL` / `BTN_SELECT_NONE` - Selection buttons
- `BTN_BROWSE` - File browser button
- `BTN_OK` / `BTN_CANCEL` / `BTN_SAVE` - Dialog buttons

### Status Messages
- `STATUS_READY` - Ready state
- `STATUS_FETCHING` - Fetching videos
- `STATUS_DOWNLOADING` - Download in progress
- `STATUS_COMPLETE` - Download complete
- Pattern: Use `.format()` for dynamic values

Example:
```python
self.status_label.setText(STATUS_STARTING_DOWNLOAD.format(count))
```

### Authentication
- `AUTH_MODE_AUTO` - "Auto (Recommended)"
- `AUTH_MODE_NONE` - "None (No authentication)"
- `AUTH_BROWSER_*` - Browser display names
- `BROWSER_*` - Internal browser values (lowercase)

### Download Options
- `MODE_BASIC` / `MODE_ADVANCED` - Download modes
- `FORMAT_VIDEO` / `FORMAT_AUDIO_ONLY` - Format types
- `QUALITY_*` - Video quality presets
- `CODEC_*` - Audio codec options
- `BITRATE_*` - Audio quality bitrates

### Filename Templates
- `TAG_*` - Template tag identifiers
- `FILENAME_TAGS` - Tag display names dict
- `DEFAULT_FILENAME_TAGS` - Default template

### UI Configuration
- `MAIN_WINDOW_MIN_WIDTH/HEIGHT` - Window size constraints
- `ICON_BANNER_SIZE` - Banner icon size (60px)
- `ICON_SPLASH_SIZE` - Splash screen size (400px)

### Default Values
- `DEFAULT_OUTPUT_DIR` - "~/Downloads"
- `DEFAULT_AUDIO_CODEC` - "mp3"
- `DEFAULT_AUDIO_QUALITY` - "192" (kbps)
- `DEFAULT_BROWSER_PREFERENCE` - "auto"

### File Paths
- `ICON_FILENAME` - "av-morning-star.png"
- `VERSION_FILE` - "VERSION"
- `DOC_*` - Documentation file paths

### Help & Documentation
- `HELP_GETTING_STARTED` - Getting started HTML
- `HELP_YOUTUBE_AUTH` - YouTube auth help
- `HELP_SUPPORTED_SITES` - Supported sites info
- `HELP_MORE_INFO` - Additional resources

### Symbols & Emoji
- `SYMBOL_CHECK` - "✓"
- `SYMBOL_SUCCESS` - "✅"
- `SYMBOL_ERROR` - "❌"
- `SYMBOL_WARNING` - "⚠"
- `SYMBOL_LIGHTBULB` - "💡"

## Best Practices

### 1. Use Constants for All User-Facing Text

**Bad:**
```python
btn = QPushButton("Download Selected")
self.setWindowTitle("AV Morning Star - Media Downloader")
```

**Good:**
```python
btn = QPushButton(BTN_DOWNLOAD_SELECTED)
self.setWindowTitle(MAIN_WINDOW_TITLE)
```

### 2. Use Format Strings for Dynamic Content

**Bad:**
```python
status = f"Downloading {filename}"
```

**Good:**
```python
status = STATUS_DOWNLOADING.format(filename)
```

### 3. Group Related Constants

Keep related constants together:
```python
# Video qualities
QUALITY_BEST = "Best"
QUALITY_4K = "4K (2160p)"
VIDEO_QUALITIES = [QUALITY_BEST, QUALITY_4K, ...]
```

### 4. Use Descriptive Names

**Bad:**
```python
SIZE_1 = 60
SIZE_2 = 400
```

**Good:**
```python
ICON_BANNER_SIZE = 60
ICON_SPLASH_SIZE = 400
```

### 5. Provide Lists for Combo Boxes

```python
# Define individual items
QUALITY_1080P = "1080p"
QUALITY_720P = "720p"

# Provide list for easy iteration
VIDEO_QUALITIES = [QUALITY_1080P, QUALITY_720P, ...]

# Usage
self.quality_combo.addItems(VIDEO_QUALITIES)
```

## Adding New Constants

### Step 1: Add to constants.py

```python
# ===== YOUR CATEGORY =====
NEW_CONSTANT = "value"
ANOTHER_CONSTANT = "another value"
```

### Step 2: Update main.py

```python
# Old
label = QLabel("Hard-coded text")

# New
label = QLabel(NEW_CONSTANT)
```

### Step 3: Document Here

Add to the appropriate category above.

## Internationalization (Future)

The constants module is designed to support future internationalization:

```python
# Future implementation
def get_localized_string(key, locale='en'):
    translations = {
        'en': ENGLISH_STRINGS,
        'es': SPANISH_STRINGS,
        'fr': FRENCH_STRINGS
    }
    return translations[locale].get(key, key)

# Usage
BTN_DOWNLOAD = get_localized_string('BTN_DOWNLOAD_SELECTED')
```

## Version History

- **0.3.0** (2026-02-03): Initial constants module created
  - Centralized all hardcoded strings
  - Added comprehensive documentation
  - Future-proofed for i18n

## Migration Guide

### For Existing Code

1. Import constants: `from constants import *`
2. Find hardcoded strings
3. Replace with constants
4. Test application

### Example Migration

**Before:**
```python
class MyDialog(QDialog):
    def __init__(self):
        self.setWindowTitle("Preferences - AV Morning Star")
        self.setMinimumSize(550, 350)
        
        title = QLabel("Preferences")
        btn = QPushButton("Save")
```

**After:**
```python
from constants import *

class MyDialog(QDialog):
    def __init__(self):
        self.setWindowTitle(PREFERENCES_WINDOW_TITLE)
        self.setMinimumSize(PREFERENCES_WINDOW_MIN_WIDTH, 
                           PREFERENCES_WINDOW_MIN_HEIGHT)
        
        title = QLabel(MENU_PREFERENCES)
        btn = QPushButton(BTN_SAVE)
```

## Testing

Run tests to verify constants work:

```bash
# Test import
python3 -c "from constants import *; print(APP_NAME)"

# Test application
python3 main.py
```

## See Also

- [Project Structure](PROJECT_STRUCTURE.md) - Overall architecture
- [Architecture](ARCHITECTURE.md) - Technical design
- [CHANGELOG.md](../CHANGELOG.md) - Version history

---

**Last Updated**: February 3, 2026  
**Module Version**: 0.3.0
