"""FFmpeg filter strings and ANSI stripping helpers."""

import re

_ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

VIDEO_DENOISE_FILTER = "hqdn3d=4:3:6:4.5"
VIDEO_SHARPEN_FILTER = "unsharp=5:5:0.8:5:5:0.4"
AUDIO_DENOISE_FILTER = "afftdn=nf=-20:nr=15:tn=1"
AUDIO_LOUDNORM_FILTER = "loudnorm=I=-16:LRA=11:TP=-1.5,aresample=48000"
AUDIO_DYNAUDNORM_FILTER = "dynaudnorm=p=0.95:m=10:s=12:g=5"


def strip_ansi_codes(text):
    """Remove ANSI escape codes from an error string for clean display."""
    return _ANSI_ESCAPE_RE.sub("", text)
