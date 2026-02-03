# Security & Privacy - User Guide

## Is AV Morning Star Safe?

**Yes!** Your credentials and personal data are secure. Here's why:

### ✅ What We DON'T Store

- ❌ **No passwords** - We never see or save your YouTube password
- ❌ **No cookies on disk** - Cookies stay in your browser's secure storage
- ❌ **No personal data** - We don't collect or store ANY information about you
- ❌ **No tracking** - No analytics, telemetry, or phone-home functionality
- ❌ **No browsing history** - We only read the cookies needed for YouTube

### ✅ How Browser Authentication Works

1. **You select your browser** (Brave, Firefox, Chrome, etc.)
2. **We read cookies from your browser's encrypted database** (read-only)
3. **Cookies are used in memory only** (never written to our files)
4. **Cookies are sent to YouTube over HTTPS** (same as normal browsing)
5. **After download, cookies are discarded** (nothing persists)

**Think of it like:** Using browser cookies is like showing your library card to check out a book. We don't make a copy of your card - we just show the librarian (YouTube) your existing card.

---

## What Data Does YouTube See?

When you download a video using AV Morning Star:

**YouTube knows:**
- ✅ Your YouTube account (same as watching in browser)
- ✅ What videos you're downloading
- ✅ Your IP address (same as normal browsing)
- ✅ Download activity (may appear in watch history)

**This is IDENTICAL to:**
- Watching the video in your browser
- Using YouTube's official app
- Streaming the video normally

**We add NO additional tracking beyond what YouTube already does when you browse their site.**

---

## What About Deno?

**Deno** is a JavaScript runtime that generates "Proof of Origin" tokens to prove you're not a bot.

**Security:**
- ✅ Official tool from Deno.land (trusted source)
- ✅ Runs in a sandbox (isolated from your system)
- ✅ No access to your files, network, or cookies
- ✅ Only does math to generate tokens
- ✅ Open source (you can audit the code)

**Think of it like:** Deno is a calculator that solves YouTube's math problem to prove you're human. It doesn't know anything about you.

---

## What About yt-dlp?

**yt-dlp** is the industry-standard tool for downloading videos, used by millions of people worldwide.

**Security:**
- ✅ Open source (10,000+ contributors can audit it)
- ✅ 10+ million downloads per month
- ✅ Actively maintained since 2021
- ✅ Used by major organizations and projects
- ✅ No known security issues

**Read more:** https://github.com/yt-dlp/yt-dlp

---

## Can My Account Be Hacked?

**Short answer:** Using AV Morning Star is as safe as using your browser.

**Long answer:**

**We do NOT increase your risk because:**
1. We only READ cookies (never modify)
2. We don't store cookies anywhere
3. We use the same HTTPS encryption as your browser
4. We don't add any new security holes

**Your account could be compromised if:**
- ❌ You install malware on your computer (affects all apps)
- ❌ You use a weak password (use YouTube's password strength checker)
- ❌ You don't have 2FA enabled (enable it in Google Account settings)
- ❌ You install malicious browser extensions (review your extensions)

**These risks exist whether or not you use AV Morning Star.**

---

## Best Security Practices

### 1. Secure Your Browser

- ✅ Keep your browser updated
- ✅ Review installed extensions regularly
- ✅ Only install extensions from official stores
- ✅ Use browser password manager or trusted password manager

### 2. Secure Your Google/YouTube Account

- ✅ Use a strong, unique password
- ✅ Enable 2-Factor Authentication (2FA)
- ✅ Review account activity regularly: https://myaccount.google.com/
- ✅ Check for suspicious devices: https://myaccount.google.com/devices

### 3. Secure Your Computer

- ✅ Keep your OS updated (security patches)
- ✅ Use antivirus software
- ✅ Don't install untrusted software
- ✅ Lock your computer when away

---

## What Can I Verify?

### Check That No Files Are Created

```bash
# Run before download
ls ~/Downloads/

# Download a video

# Run after download
ls ~/Downloads/
# You should ONLY see the video file, no .txt or .cookies files
```

### Check Network Traffic (Advanced Users)

```bash
# Monitor network connections while downloading
sudo tcpdump -i any -n 'host youtube.com'
# You'll see HTTPS (encrypted) connections to YouTube only
# No connections to suspicious servers
```

### Review the Source Code

AV Morning Star is open source. You can read every line:
- GitHub: https://github.com/asafelobotomy/AV-Morning-Star
- All code is visible and auditable
- No hidden functionality
- No obfuscation

---

## Privacy Comparison

### AV Morning Star vs. Browser

| Feature | AV Morning Star | YouTube in Browser |
|---------|-----------------|-------------------|
| Sees your account | ✅ Yes | ✅ Yes |
| Tracks downloads | ❌ No | ✅ Yes (watch history) |
| Collects analytics | ❌ No | ✅ Yes (Google Analytics) |
| Shows ads | ❌ No | ✅ Yes |
| Stores cookies | ❌ No | ✅ Yes |
| Stores browsing history | ❌ No | ✅ Yes |

**AV Morning Star is MORE private than using YouTube in your browser** because we don't add any tracking beyond what YouTube already does.

---

## What If I'm Still Concerned?

### Option 1: Use Without Authentication

Set browser preference to "None" in Tools > Preferences:
- Downloads public videos only
- Lower quality may be available
- No age-restricted content
- No private/unlisted videos

**Trade-off:** Limited functionality but 100% no cookie access

### Option 2: Use a Dedicated Browser Profile

Create a separate browser profile just for YouTube downloads:

**Firefox:**
```bash
firefox -P
# Create new profile "YouTube Downloads"
# Sign into YouTube there only
# Select this profile in AV Morning Star preferences
```

**Chrome/Brave:**
```bash
brave --profile-directory="Profile 2"
# Create new profile
# Sign into YouTube
# Use this profile for downloads
```

**Benefit:** Isolates download activity from main browsing

### Option 3: Review Activity Regularly

Check what was downloaded via Google Activity:
- Go to: https://myactivity.google.com/
- Filter by "YouTube"
- Review and delete as needed

---

## Frequently Asked Questions

### Q: Does AV Morning Star send my cookies to the developers?

**A:** No. We don't have any servers, analytics, or telemetry. Your cookies never leave your computer except to go to YouTube (same as browser).

### Q: Can I verify cookies aren't saved to disk?

**A:** Yes! Check your Downloads folder after downloading. You'll only see video files, never .cookies or .txt files with credentials.

### Q: What happens to cookies after I close the app?

**A:** They're immediately discarded from memory. Nothing persists after the app closes.

### Q: Is this legal?

**A:** Yes. Downloading videos you have access to for personal use is legal in most jurisdictions. Check your local laws. Using browser cookies for authentication is the same as using your browser.

### Q: What if my YouTube account gets banned?

**A:** Using AV Morning Star is no different than watching videos in your browser. YouTube's Terms of Service apply the same way. If you download excessive amounts of content, YouTube may rate-limit or ban your account (same as excessive streaming).

### Q: Can I use this on a public/shared computer?

**A:** Not recommended. Anyone with access to the browser you're using could download videos as you. Use only on personal, secured computers.

---

## Reporting Security Issues

**Found a security problem?** Please report it responsibly:

1. **DO NOT** post publicly on GitHub
2. **DO** email the maintainers directly
3. **DO** include:
   - Description of the issue
   - Steps to reproduce
   - Your suggested fix (if any)

We take security seriously and will respond within 24 hours.

---

## Audit Trail

This application has undergone comprehensive security review:

- ✅ **No credential storage vulnerabilities**
- ✅ **No data leakage**
- ✅ **No network security issues**
- ✅ **Complies with privacy best practices**

**Last Security Audit:** February 3, 2026  
**Next Audit:** August 2026  

Full audit report: `SECURITY_AUDIT.md`

---

## Summary

**Is AV Morning Star safe?**

# ✅ YES

**Your data is secure because:**
- ✅ No credentials stored
- ✅ Cookies handled in memory only  
- ✅ HTTPS encryption
- ✅ Open source (auditable)
- ✅ No telemetry or tracking
- ✅ Uses trusted libraries (yt-dlp)

**Best practices:**
1. Keep software updated
2. Secure your Google account (2FA)
3. Use on trusted computers only
4. Review account activity regularly

**Still have questions?** See `SECURITY_AUDIT.md` for technical details.

---

**Last Updated:** February 3, 2026  
**Version:** 1.0.0
