# Supported Sources

AV Morning Star uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) as its download engine, which supports over 1,700 sites. This document describes the practical tiers of support within this app.

---

## Tier A — Works well (no login required)

These sources work reliably with default settings.

### General Video

| Source | Notes |
|--------|-------|
| **YouTube** | Full support: videos, playlists, channels, Shorts, live replays. PO tokens via Deno/Node.js (optional, improves reliability). See [Authentication Guide](AUTHENTICATION_GUIDE.md) if bot detection triggers. |
| **Odysee / LBRY** | Videos, playlists, channel pages via native `lbry` extractor |
| **Vimeo** (public) | Public videos, albums, groups, and unlisted (with direct link) |
| **Twitch** VOD & clips | Public VODs and clips; sub-only VODs need login (see Tier B) |
| **Kick** VOD & clips | Via native yt-dlp extractor |
| **TikTok** | Public videos; `tiktok:sound` and `tiktok:tag` extractors currently broken upstream |
| **Rumble** | Videos and channel pages |
| **Dailymotion** | Public videos and playlists |
| **PeerTube** | Any public PeerTube instance (federated) |
| **Streamable** | Short video clips |
| **BitChute** | Videos and channel pages |
| **Loom** | Public workspace videos |
| **9GAG** | Individual video posts |
| **Imgur** | Videos and GIFs |
| **Weibo** | Public video posts |
| **Floatplane** (public) | Public videos; subscription content needs login (see Tier B) |

### Audio / Music

| Source | Notes |
|--------|-------|
| **SoundCloud** (public) | Tracks, playlists, user profiles; some restricted tracks need login (see Tier B) |
| **Bandcamp** | Tracks, albums, and artist pages |
| **Mixcloud** | Mixes and shows |
| **Audius** | Tracks, albums, and artist pages |
| **Audiomack** | Tracks, albums, and playlists |
| **iHeartRadio** | On-demand podcast episodes |
| **Spreaker** | Podcast episodes and shows |
| **Niconico** (NicoVideo) | Public videos and playlists; some content requires account (see Tier B) |

### Social / Creator

| Source | Notes |
|--------|-------|
| **Twitter / X** | Public video posts; authenticated access reduces rate limits (see Tier B) |
| **Bluesky** | Public video posts |
| **Reddit** | Videos hosted on `v.redd.it` embedded in posts |
| **Tumblr** | Public video posts |
| **Substack** | Embedded video and audio posts |
| **Pinterest** | Public video pins |
| **VK** | Public videos from VK (Russian social network) |

### Education / Public Media

| Source | Notes |
|--------|-------|
| **PBS** (`pbs.org`) | Public broadcast videos; full-episode access may require US IP |
| **NPR** | Audio and video segments |
| **Khan Academy** | Public lesson videos |
| **MIT OpenCourseWare** (`ocw.mit.edu`) | Lecture videos |
| **TED** | Talks, playlists, and series |
| **C-SPAN** | Public government recordings |
| **Internet Archive** (`archive.org`) | Excellent; vast public AV collection |
| **Library of Congress** (`loc.gov`) | Public AV resources |
| **Wikimedia Commons** | Free media files from Wikipedia projects |
| **NHK World** | NHK international broadcast content |

### News / Journalism

| Source | Notes |
|--------|-------|
| **BBC** | BBC News and global content; BBC iPlayer requires UK IP / login (see Tier B) |
| **Al Jazeera** | Public news videos |
| **CNN** | News video clips |
| **Fox News** | News video clips |
| **NBC News** | News video clips |
| **Bloomberg** | Public news clips |
| **Washington Post** | Embedded video articles |
| **The Guardian** | Embedded video articles |
| **NY Times** | Embedded video articles (some paywalled) |
| **Wall Street Journal** | Video articles (some paywalled) |

### Podcast & RSS

| Source | Notes |
|--------|-------|
| **Podcast RSS/Atom feeds** | Paste any RSS/Atom feed URL — episodes are listed automatically |
| **Apple Podcasts** | Podcast pages are RSS-backed; works via feed URL |
| **Megaphone** | Podcast episodes from `megaphone.fm` embeds |
| **Simplecast** | Podcast episodes |
| **Podbean** | Podcast episodes |
| **Libsyn** | Podcast episodes |

### Direct Links / Generic

| Source | Notes |
|--------|-------|
| **Direct media URLs** | `.mp3`, `.m4a`, `.mp4`, `.webm`, `.m3u8` (non-DRM HLS), `.mpd` (non-DRM DASH) |
| **Google Drive** (public) | Publicly shared files |
| **Dropbox** (public) | Public shared file links |
| **Streamable** | Short clips |

---

## Tier B — Works with browser cookies enabled

These sources work when you set your browser in **Tools → Preferences → Authentication**.
The app reads your browser's login session (cookies) — no passwords are ever stored.

| Source | Why cookies help |
|--------|-----------------|
| **Patreon** | Patron-only posts require login |
| **Nebula** (`watchnebula.com`) | Subscription required for all content |
| **Dropout** (`dropout.tv`) | Subscription required |
| **CuriosityStream** | Subscription required |
| **Floatplane** (members content) | Creator-subscription required |
| **Rooster Teeth** | Some content requires membership |
| **Instagram** | Most content requires login; `instagram:user` extractor is currently broken upstream |
| **Twitter / X** | Rate limits dramatically reduced; some media requires login |
| **Private / password-protected Vimeo** | Needs authenticated session |
| **Facebook** | Most video content requires login |
| **Bilibili** | Higher-quality streams and some content requires login |
| **Niconico** | Premium/channel content requires login |
| **LinkedIn** (Learning) | LinkedIn Learning courses require subscription |
| **Udemy** | Course videos require purchase / subscription |
| **BBC iPlayer** | UK IP + BBC account required for iPlayer content |
| **SoundCloud** (restricted tracks) | Tracks restricted to subscribers |
| **Twitch** (sub-only VODs) | Twitch channel subscription required |
| **Substack** (paywalled posts) | Paid subscription required |
| **Reddit** (NSFW) | NSFW community content requires login |
| **Tumblr** (NSFW) | NSFW content requires logged-in account |

**How to enable:** Open **Tools → Preferences**, select the browser where you are logged in, and re-fetch the URL.

---

## Tier C — Not supported (DRM)

These services use DRM (Digital Rights Management) copy protection. The app will show a clear error if you attempt to use them, and yt-dlp explicitly refuses to process them.

### US Streaming / VOD

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

### Music Streaming

| Service | Domain |
|---------|--------|
| Spotify | `open.spotify.com` |
| Amazon Music | `music.amazon.com` (and regional variants) |
| Apple Music | `music.apple.com` |
| Deezer | `deezer.com` |

### Rakuten

| Service | Domain |
|---------|--------|
| Rakuten TV (EU) | `www.rakuten.tv` — Widevine DASH, not yet in upstream KnownDRMIE |
| Rakuten TV (JP) | `tv.rakuten.co.jp` — in yt-dlp KnownDRM list |

### Regional / Broadcaster (DRM-protected)

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

Some yt-dlp extractors are listed as **Currently broken** in the [official supported sites list](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) due to upstream API changes. Notable examples include:

| Extractor | Status |
|-----------|--------|
| Instagram (user profiles) | `instagram:user` — Currently broken upstream |
| Deutsche Welle (`dw.com`) | `dw` / `dw:article` — Currently broken upstream |
| Reuters | `Reuters` — Currently broken upstream |
| TikTok sound/tag | `tiktok:sound`, `tiktok:tag` — Currently broken upstream |
| NBC Sports | `NBCSports`, `NBCSportsStream` — Currently broken upstream |
| NBA | Multiple NBA extractors — Currently broken upstream |
| CBS / CBS Sports | `CBS`, `cbssports` — Currently broken upstream |
| Bayerischer Rundfunk (BR) | `BR` — Currently broken upstream |
| RTS.ch | `RTS` — Currently broken upstream |

These are not AV Morning Star bugs — they are tracked in the [yt-dlp issue tracker](https://github.com/yt-dlp/yt-dlp/issues). Keeping yt-dlp up to date (pinned in `requirements.txt`) will pick up fixes as they land.

---

## Full extractor list

yt-dlp's complete list of ~1,700 supported extractors: [supportedsites.md](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## Tooling notes

AV Morning Star uses **yt-dlp + FFmpeg** as its only download engine. There is no integration with:

- **streamlink** — for live HLS/DASH capture to player (different use case)
- **gallery-dl** — for image gallery sites (different media type)
- **spotDL** — for Spotify (DRM; ToS issues)
- **you-get** — superseded by yt-dlp

If you need live stream capture, use `streamlink` separately from the command line alongside this app.
