# Smart Browser Cookie Detection

## Overview

AV Morning Star now features **intelligent browser detection** that automatically finds and uses your browser's YouTube cookies when needed, while preferring cookieless downloads when possible.

## How It Works

### 1. Automatic Browser Detection

During the fetch/retry flow when a cookieless download fails and Auto mode is enabled, the app:
- ✅ Scans for installed browsers (Brave, Firefox, Chrome, Edge, etc.)
- ✅ Checks which browsers have YouTube authentication cookies
- ✅ Auto-selects the best browser with active YouTube login
- ✅ Falls back to cookieless if no authentication found

**Supported Browsers:**
- Brave
- Firefox
- Chrome
- Chromium
- Microsoft Edge
- Opera
- Vivaldi

### 2. Smart Download Strategy

**For YouTube URLs:**

```
┌─────────────────────────────────────┐
│  User enters YouTube URL            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Try cookieless download first      │
│  (no authentication required)       │
└──────────────┬──────────────────────┘
               │
               ├──► SUCCESS ──────────► Download works! ✅
               │
               └──► FAILED (bot detection)
                             │
                             ▼
               ┌─────────────────────────────────┐
               │  Auto-detect browsers with      │
               │  YouTube login                  │
               └──────────────┬──────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
     Found browsers              No browsers found
                │                         │
                ▼                         ▼
  ┌──────────────────────┐    ┌──────────────────────┐
  │ Prompt user:         │    │ Show error with      │
  │ "I detected Brave!"  │    │ instructions to      │
  │ "Retry with login?"  │    │ sign into YouTube    │
  └──────────┬───────────┘    └──────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
  User says        User says
   "Yes"             "No"
    │                 │
    ▼                 │
  Retry with          │
  cookies ✅          │
                      ▼
                 Show error ❌
```

**For Non-YouTube URLs:**
- Uses cookies if browser preference is set
- Otherwise tries cookieless download

### 3. User Experience

**Scenario 1: First-time user (cookieless works)**
1. User enters YouTube URL
2. App tries cookieless download
3. ✅ **Success!** Video downloads without authentication

**Scenario 2: YouTube requires authentication**
1. User enters YouTube URL
2. App tries cookieless download
3. ❌ YouTube bot detection triggered
4. 🔍 App automatically detects Brave browser with YouTube login
5. 📢 App prompts: "I detected you're logged in via Brave. Retry with authentication?"
6. User clicks "Yes"
7. ✅ **Success!** Video downloads using browser cookies

**Scenario 3: No browser detected**
1. User enters YouTube URL
2. App tries cookieless download
3. ❌ YouTube bot detection triggered
4. 🔍 App checks for browsers
5. ❌ No browsers with YouTube cookies found
6. 📢 App shows helpful message: "Sign into YouTube in Firefox/Chrome/Brave, then try again"
7. User signs into YouTube in their browser
8. User tries again
9. ✅ **Success!** App auto-detects the login

## Benefits

### For Users

✅ **Zero configuration** - Works out of the box  
✅ **Privacy by default** - Tries cookieless first  
✅ **Automatic authentication** - No manual browser selection needed  
✅ **Smart error handling** - Clear guidance when authentication required  
✅ **One-click retry** - No need to navigate menus  

### Technical Benefits

✅ **Respects privacy** - Only uses cookies when necessary  
✅ **Reduces bot detection** - Cookieless downloads preferred  
✅ **Better UX** - Automatic vs. manual configuration  
✅ **Fewer support requests** - Self-diagnosing authentication issues  
✅ **Cross-platform** - Works on macOS and Linux; Windows browser path detection is not currently implemented  

## Manual Override

Users can still manually select a browser in **Tools > Preferences** if they want to:
- Force authentication even if cookieless works
- Switch between multiple YouTube accounts
- Disable cookies entirely (set to "None")

## Detection Logic

### Browser Availability Check

The app checks for browser cookie database files in standard locations:

**Linux:**
```
~/.config/BraveSoftware/Brave-Browser/Default/Cookies
~/.mozilla/firefox/
~/.config/google-chrome/Default/Cookies
# ... etc
```

**macOS:**
```
~/Library/Application Support/BraveSoftware/Brave-Browser/Default/Cookies
~/Library/Application Support/Firefox/Profiles/
~/Library/Application Support/Google/Chrome/Default/Cookies
# ... etc
```

### YouTube Authentication Check

For each available browser, the app:
1. Attempts to extract cookies from encrypted database
2. Searches for YouTube-specific authentication cookies:
   - `SAPISID` (API session ID)
   - `SID` (Session ID)
   - `SSID` (Secure Session ID)
   - `HSID` (Host Session ID)
   - `APISID` (API ID)
3. If found, marks browser as "logged in to YouTube"

### Priority Order

1. **First choice:** Browser with YouTube authentication cookies
2. **Second choice:** Any available browser
3. **Fallback:** None (cookieless mode)

## Privacy & Security

### What Gets Checked

✅ **Checked:** Browser cookie database file existence  
✅ **Checked:** Presence of YouTube authentication cookies  
✅ **Checked:** Cookie domain (only YouTube cookies examined)  

❌ **NOT checked:** Browsing history  
❌ **NOT checked:** Saved passwords  
❌ **NOT stored:** Cookie data on disk  

**Note:** In Auto mode, browser cookies are inspected to identify which browsers have an active YouTube session before the retry prompt is shown.  

### When Cookies Are Used

Cookies are only extracted from browser when:
1. User approves authentication prompt, OR
2. User manually selected browser in Preferences, OR
3. Cookieless download failed and auto-retry approved

### Security Guarantees

- ✅ Cookies read from **encrypted** browser database
- ✅ Requires OS keyring authentication (gnome-keyring, etc.)
- ✅ Cookies used in **memory only** (never written to disk)
- ✅ User consent required for first-time authentication
- ✅ No cookies sent to third parties

## Troubleshooting

### "No browsers with YouTube cookies found"

**Cause:** You're not logged into YouTube in any installed browser

**Fix:**
1. Open Firefox, Chrome, or Brave
2. Go to https://youtube.com
3. Sign in to your account
4. Return to AV Morning Star
5. Try fetching again

### "I have multiple YouTube accounts"

**Solution:** Use Tools > Preferences to select specific browser:
- Use different browsers for different accounts
- Example: Firefox for personal, Chrome for work

### "Detection not finding my browser"

**Possible causes:**
1. Browser installed in non-standard location
2. Custom browser profile path
3. Browser not officially supported

**Fix:** Manually select browser in Tools > Preferences

### "I want to force cookieless mode"

**Solution:** Set browser preference to "None" in Tools > Preferences
- This disables all cookie usage
- Only public videos will work
- Lower quality may be enforced by YouTube

## Examples

### Example 1: Auto-Detection Success

```
User action: Enters https://www.youtube.com/watch?v=dQw4w9WgXcQ
App detects: Brave browser with YouTube login
Status: "Fetching with brave authentication..."
Result: ✅ Video fetched successfully
```

### Example 2: Cookieless Success

```
User action: Enters https://www.youtube.com/watch?v=public_video
App tries: Cookieless download
Status: "Fetching video information (no authentication)..."
Result: ✅ Video fetched successfully (no cookies needed)
```

### Example 3: Auto-Retry with Prompt

```
User action: Enters https://www.youtube.com/watch?v=restricted_video
App tries: Cookieless download
YouTube: ❌ Bot detection error
App detects: Brave browser with YouTube login
Prompt: "I detected you're logged in via Brave. Retry with authentication?"
User: Clicks "Yes"
App retries: With Brave cookies
Result: ✅ Video fetched successfully
```

### Example 4: No Authentication Available

```
User action: Enters https://www.youtube.com/watch?v=restricted_video
App tries: Cookieless download
YouTube: ❌ Bot detection error
App detects: No browsers with YouTube cookies
Message: "Please sign into YouTube in Firefox/Chrome/Brave, then try again"
User: Signs into YouTube in Firefox
User: Tries again
App detects: Firefox now has YouTube cookies
Result: ✅ Video fetched successfully
```

## API Reference

### Functions in `browser_utils.py`

#### `detect_available_browsers()`
Returns list of installed browsers that have accessible cookie databases.

**Returns:** `list` of browser names (e.g., `['brave', 'firefox']`)

**Example:**
```python
browsers = detect_available_browsers()
# ['brave', 'firefox', 'chrome']
```

#### `get_browsers_with_youtube_cookies()`
Returns list of browsers that have active YouTube authentication cookies.

**Returns:** `list` of browser names with YouTube login

**Example:**
```python
youtube_browsers = get_browsers_with_youtube_cookies()
# ['brave']  # User is logged into YouTube in Brave
```

**Note:** This function reads cookie stores. Only call it from `on_fetch_error()` after the user has been prompted — never during cookieless-first fetches.

## Migration Guide

### For Existing Users

**Before:** Manual browser selection required
```
1. Install app
2. Go to Tools > Preferences
3. Select browser
4. Try to download
```

**After:** Automatic detection
```
1. Install app
2. Try to download ✅ (automatic)
```

**Your existing preferences are preserved!** If you previously selected a browser in Preferences, it will continue to be used.

### For Developers

**Old approach:**
```python
# Hardcoded default
self.browser_preference = 'firefox'
```

**New approach:**
```python
# Auto mode — cookieless first; cookies only after user consent
self.browser_preference = 'auto'  # persisted via QSettings in settings.py
```

## Future Enhancements

Potential improvements for future versions:

- [ ] Remember which browser worked for each site
- [ ] Multi-account support (select YouTube account)
- [ ] Browser profile selection (for users with multiple profiles)
- [ ] Automatic cookie refresh detection
- [ ] Browser installation suggestions ("Would you like to install Firefox?")
- [ ] Cookie expiration warnings
- [ ] Integration with system keyring for enhanced security

## Changelog

**Version 1.1.0** (February 3, 2026)
- ✅ Added automatic browser detection
- ✅ Added smart cookieless-first strategy
- ✅ Added auto-retry with authentication prompt
- ✅ Improved error messages with actionable guidance
- ✅ Added `browser_utils.py` module

---

**Last Updated:** February 3, 2026  
**Feature Status:** ✅ STABLE  
**Tested On:** Linux (Arch), with Brave browser
