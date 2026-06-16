# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | Yes       |
| < 0.4   | No        |

## How AV Morning Star Handles Sensitive Data

- **No credentials on disk** — the app never writes browser cookies, passwords, or tokens to its own files.
- **Cookieless by default** — YouTube fetches start without authentication; cookies are read only after you confirm a retry prompt.
- **Explicit browser mode** — choosing a specific browser in Preferences uses that browser's cookies immediately (your choice).
- **No telemetry** — the app makes no analytics or phone-home requests.
- **Open source** — all code is inspectable in this repository.

## Reporting a Vulnerability

If you discover a security issue, **do not open a public GitHub issue**.

Instead, report it privately via [GitHub Security Advisories](https://github.com/asafelobotomy/AV-Morning-Star/security/advisories/new) or contact the maintainers through the repository's contact methods.

Please include:

1. A description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

We aim to acknowledge reports within 48 hours and provide a fix or mitigation plan within 7 days for critical issues.

## User Security Recommendations

- Keep your browser, OS, FFmpeg, Deno/Node.js, and yt-dlp up to date
- Use strong passwords and 2FA on your Google/YouTube account
- Review browser extensions regularly
- Only download content you have the right to access

For a detailed technical review, see [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md).
