# AGENTS.md - WalkingPad HACS Integration

> **For AI agents working on this project.** Quick reference for structure, conventions, and workflows.

---

## 🎯 Project Overview

**WalkingPad** is a [Home Assistant](https://www.home-assistant.io/) custom integration for **KingSmith WalkingPad C1** treadmills. It provides Bluetooth (BLE) control and monitoring - **100% local, no cloud**.

- **Type:** HACS custom integration
- **Language:** Python 3.11+
- **Communication:** Bluetooth Low Energy (BLE) via `bleak` and `ph4-walkingpad`
- **Tested with:** KingSmith WalkingPad C1 only (A1, R1 PRO not tested)

---

## 📁 Project Structure

```
integration/
├── AGENTS.md                 # This file
├── README.md                 # English documentation (HACS shows this)
├── README_de.md              # German documentation
├── LICENSE                   # MIT License
├── hacs.json                 # HACS configuration
├── .gitignore                # Python/HA ignores
│
└── custom_components/
    └── walkingpad/           # The actual integration
        ├── manifest.json     # HA integration manifest (version, requirements)
        ├── __init__.py       # Setup, services, platform loading
        ├── config_flow.py    # Setup wizard (auto-discovery by name "WalkingPad")
        ├── const.py          # Constants (DOMAIN, speeds, etc.)
        ├── coordinator.py    # DataUpdateCoordinator - BLE connection & data
        ├── sensor.py         # Sensors (session, daily, total)
        ├── number.py         # Speed slider (0.5-6.0 km/h)
        ├── button.py         # Start/Stop, speed presets, mode buttons
        ├── services.yaml     # Service definitions (start, stop, set_speed)
        ├── strings.json      # UI strings
        ├── brand/
        │   ├── icon.png      # 256x256 icon
        │   └── icon@2x.png   # 512x512 icon
        └── translations/
            ├── de.json       # German translations
            └── en.json       # English translations
```

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| Platform | Home Assistant (2024.1.0+) |
| Language | Python 3.11+ |
| Bluetooth | `bleak` (BLE library) |
| Protocol | `ph4-walkingpad==1.0.2` (reverse-engineered protocol) |
| Distribution | HACS (Home Assistant Community Store) |
| Hosting | GitHub: `bleibdirtroy/walkingpad-hacs` |

---

## 📊 Entities Created

### Sensors (only real device values - NO estimated calories!)
| Type | Entities | Reset |
|------|----------|-------|
| Session | `speed`, `steps`, `distance`, `time`, `status` | Device restart |
| Daily | `daily_steps`, `daily_distance` | Midnight (00:00) |
| Total | `total_steps`, `total_distance` | Never (persistent via RestoreEntity) |

### Controls
- **Number:** `speed` (slider 0.5-6.0 km/h, step 0.5)
- **Buttons:** `start`, `stop`, 6 speed presets, 3 modes (auto/manual/standby)

### Services
- `walkingpad.start` - Start belt
- `walkingpad.stop` - Stop belt
- `walkingpad.set_speed` - Set speed (data: `{speed: 3.5}`)

---

## 🔌 Connection Details

- **Protocol:** Bluetooth Low Energy (BLE)
- **Discovery:** Searches for device name `"WalkingPad"`, stores MAC address
- **Range:** Device must be within Bluetooth range
- **Cloud:** **NONE** - completely local
- **Reconnect:** Automatic on HA restart

---

## 🚀 Development Workflow

### Setup
```bash
cd /home/troy/Projekte/walkingpad
source .venv/bin/activate
pip install ph4-walkingpad bleak homeassistant
```

### Testing Locally
```bash
# Syntax check
python -m py_compile custom_components/walkingpad/*.py

# JSON validation
python -m json.tool custom_components/walkingpad/manifest.json

# YAML validation
python -c "import yaml; yaml.safe_load(open('custom_components/walkingpad/services.yaml'))"
```

### Git Workflow
```bash
# Check status
git status

# Commit
git add -A
git commit -m "Description"

# Push
git push origin main

# Release (create tag)
git tag -a v1.2.0 -m "Release v1.2.0 - Description"
git push origin v1.2.0
```

### Version Bumping
1. Update `version` in `custom_components/walkingpad/manifest.json`
2. Create git tag with same version: `v1.2.0`
3. Push tag: `git push origin v1.2.0`

---

## ⚠️ Important Conventions

### DO
- ✅ Only use **real values from the device** (no estimated/calculated calories!)
- ✅ Keep it **100% local** - no cloud, no external APIs
- ✅ Use `CoordinatorEntity` for all entities
- ✅ Use `RestoreEntity` for persistent values (total stats)
- ✅ Update **both** READMEs (English + German)
- ✅ Bump version in `manifest.json` for releases
- ✅ Create git tag for HACS releases

### DON'T
- ❌ Add cloud/online features
- ❌ Add estimated/calculated sensor values (like calories)
- ❌ Remove the `brand/` icons - HACS needs them
- ❌ Change the domain `walkingpad` - must match folder name
- ❌ Forget to update `translations/` when adding strings

---

## 🐛 Known Limitations

- **Only tested with WalkingPad C1** - other models (A1, R1 PRO) not verified
- **No maintenance/calibration mode** in the `ph4-walkingpad` library
- **No calorie data** from device (would be estimation only - we don't show this)
- Device must be in Bluetooth range (no WiFi/cloud fallback)

---

## 🔗 Key Files to Edit

| Task | File |
|------|------|
| Add/change sensors | `sensor.py` |
| Add/change buttons | `button.py` |
| Change speed slider | `number.py` |
| BLE logic, connection | `coordinator.py` |
| Setup flow, auto-discovery | `config_flow.py` |
| Version, requirements | `manifest.json` |
| HACS metadata | `hacs.json` |
| Documentation | `README.md` + `README_de.md` |
| Translations | `translations/de.json` + `translations/en.json` |
| Icons | `brand/icon.png` + `brand/icon@2x.png` |

---

## 📚 External References

- [ph4-walkingpad](https://pypi.org/project/ph4-walkingpad/) - Protocol library
- [bleak](https://github.com/hbldh/bleak) - BLE for Python
- [HACS Documentation](https://hacs.xyz/docs/publish/start)
- [HA Developer Docs](https://developers.home-assistant.io/)
- [Reference project](https://github.com/adrienbrault/geekmagic-hacs) - HACS structure example

---

## 🤖 AI Usage

This project was developed with AI assistance (Claude). All code is reviewed, tested, and verified with a real WalkingPad C1 device.

---

**Last updated:** 2025-01-26
**Maintainer:** @bleibdirtroy
