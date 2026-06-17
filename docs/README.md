# AV Morning Star Documentation

**Version 0.4.1**

## Index

### Users
| Guide | Description |
|-------|-------------|
| [Main README](../README.md) | Installation, features, troubleshooting |
| [Getting Started](GETTING_STARTED.md) | First-run walkthrough |
| [Authentication Guide](AUTHENTICATION_GUIDE.md) | YouTube browser cookie auth |
| [Smart Browser Detection](SMART_BROWSER_DETECTION.md) | Auto mode and retry flow |
| [Security & Privacy](SECURITY_AND_PRIVACY.md) | Plain-language security overview |
| [SECURITY.md](../SECURITY.md) | Vulnerability reporting |

### Developers
| Guide | Description |
|-------|-------------|
| [Architecture](ARCHITECTURE.md) | Extractors, threading, download pipeline |
| [Project Structure](PROJECT_STRUCTURE.md) | Repository layout |
| [Constants Reference](CONSTANTS.md) | `constants.py` documentation |
| [Security Audit](SECURITY_AUDIT.md) | Technical security review |
| [Changelog](../CHANGELOG.md) | Release history |

## Quick answers

- **YouTube auth failing?** → [Authentication Guide](AUTHENTICATION_GUIDE.md)
- **Adding a platform?** → [Architecture — Adding a new platform](ARCHITECTURE.md)
- **Building AppImage?** → [Main README — Build from Source](../README.md#build-appimage-from-source)
- **Running tests?** → `python3 -m unittest discover -s tests -p "test_*.py"`
