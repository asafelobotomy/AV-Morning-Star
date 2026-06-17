# Supported Sources

AV Morning Star uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) as its download engine, which supports over 1,700 sites. This document describes the practical tiers of support within this app.

---

## Tier A — Works well (no login required)

These sources work reliably with default settings.

| Source | Notes |
|--------|-------|
| **YouTube** | Full support: playlists, channels, Shorts. PO tokens via Deno/Node.js (optional, improves reliability). See [Authentication Guide](AUTHENTICATION_GUIDE.md) if bot detection triggers. |
| **Odysee / LBRY** | Via native `lbry` yt-dlp extractor |
| **Vimeo** (public) | Public videos and unlisted (with direct link) |
| **Twitch** VOD & clips | Live streams require timing; some sub-only VODs need login (see Tier B) |
| **Kick** VOD & clips | Via native yt-dlp extractor |
| **TikTok** | Public videos; some tag/sound extractors are currently broken upstream |
| **Rumble** | Video and channel pages |
| **PeerTube** | Any public PeerTube instance |
| **Dailymotion** | Public videos and playlists |
| **SoundCloud** | Public tracks and playlists; some tracks are restricted (see Tier B) |
| **Bandcamp** | Public tracks and albums |
| **Internet Archive** (`archive.org`) | Excellent; large public AV collection |
| **TED** | Talks and playlists |
| **C-SPAN** | Public recordings |
| **Podcast RSS feeds** | Paste any RSS/Atom feed URL — episodes are listed automatically |
| **Direct media URLs** | `.mp3`, `.m4a`, `.mp4`, `.webm`, `.m3u8` (non-DRM HLS), `.mpd` (non-DRM DASH) |
| **Google Drive** (public) | Publicly shared files |
| **Dropbox** (public) | Shared file links |

---

## Tier B — Works with browser cookies enabled

These sources work when you set your browser in **Tools → Preferences → Authentication**.
The app reads your browser's login session (cookies) — no passwords are ever stored.

| Source | Why cookies help |
|--------|-----------------|
| **Patreon** | Patron-only posts require login |
| **Nebula** (`watchnebula.com`) | Subscription required |
| **Instagram** | Most content requires login; user profile extractor is currently broken upstream |
| **Twitter / X** | Rate limits reduced; some media requires login |
| **Private / password-protected Vimeo** | Needs authenticated session |
| **Facebook** | Most video content requires login |
| **Bilibili** | Higher-quality streams and some content requires login |
| **SoundCloud** (some tracks) | Restricted or go-only tracks |
| **Twitch** (sub-only VODs) | Twitch subscription required |

**How to enable:** Open **Tools → Preferences**, select the browser where you are logged in, and re-fetch the URL.

---

## Tier C — Not supported (DRM)

These services use DRM (Digital Rights Management) copy protection. The app will show a clear error if you attempt to use them, and yt-dlp explicitly refuses to process them.

### Streaming / VOD

| Service | Domain |
|---------|--------|
| Netflix | `netflix.com` |
| Disney+ | `disneyplus.com` |
| Amazon Prime Video | `primevideo.com` |
| Hulu | `hulu.com` |
| Apple TV+ | `tv.apple.com` |
| HBO Max | `play.hbomax.com` |
| Peacock | `peacocktv.com` |
| Paramount+ | `paramountplus.com` |
| Crunchyroll | `crunchyroll.com` |
| Mubi | `mubi.com` |
| Viki | `viki.com` |
| Zee5 | `zee5.com` |
| Philo | `philo.com` |

### Music

| Service | Domain |
|---------|--------|
| Spotify | `open.spotify.com` |
| Amazon Music | `music.amazon.*` |
| Deezer | `deezer.com` |
| Apple Music | (via `tv.apple.com`) |

### Rakuten

| Service | Domain |
|---------|--------|
| Rakuten TV (EU) | `www.rakuten.tv` — Widevine DASH |
| Rakuten TV (JP) | `tv.rakuten.co.jp` — in yt-dlp KnownDRM list |

### Regional / Broadcaster

| Service | Domain |
|---------|--------|
| Channel 4 / Channel 5 | `channel4.com`, `channel5.com` |
| 6play (FR) | `6play.fr` |
| RTL+ (DE) | `plus.rtl.de` |
| RTLplay (BE) | `rtlplay.be` |
| RTLmost (HU) | `rtlmost.hu` |
| TV5MONDE+ | `tv5mondeplus.com` |
| CTV / Noovo / TSN (CA) | `ctv.ca`, `noovo.ca`, `tsn.ca` |
| NowTV (IT) | `nowtv.it` |
| Joyn (DE) | `joyn.de` |
| U-NEXT (JP) | `video.unext.jp` |

---

## "Currently broken" extractors

Some yt-dlp extractors are listed as **Currently broken** in the [official supported sites list](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) due to upstream API changes. Notable examples include parts of **Instagram** (user profiles), **NBC Sports**, **Reuters**, and some **TikTok** search/tag routes.

These are not AV Morning Star bugs — they are tracked in the yt-dlp issue tracker. Keeping yt-dlp up to date (it is pinned in `requirements.txt`) will pick up fixes as they land.

---

## Full extractor list

yt-dlp's complete list of ~1,700 supported sites: [supportedsites.md](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## Tooling notes

AV Morning Star uses **yt-dlp + FFmpeg** as its only download engine. There is no integration with:

- **streamlink** — for live HLS/DASH capture to player (different use case)
- **gallery-dl** — for image gallery sites (different media type)
- **spotDL** — for Spotify (DRM; ToS issues)
- **you-get** — superseded by yt-dlp

If you need live stream capture, use `streamlink` separately from the command line alongside this app.
