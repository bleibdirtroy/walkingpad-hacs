# WalkingPad 🏃

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

🇬🇧 **English** | [🇩🇪 Deutsch](README_de.md)

Custom integration for **KingSmith WalkingPad** treadmills - Bluetooth control directly from Home Assistant!

> 🔒 **100% local - no cloud!**
> All data stays with you. No internet connection to the manufacturer required.

> ⚠️ **Only tested with KingSmith WalkingPad C1!**
> Works so far only with this model (possibly also A1, R1 PRO - not tested).

---

## ✨ Features

- 📊 **Live sensors**: Steps, distance, speed, time, status (all real values from the device)
- 🏆 **Total statistics**: Total steps & distance (persisted across restarts)
- 🔢 **Slider**: Speed 0.5-6.0 km/h (0.5 steps)
- 🔵 **Buttons**: Start, Stop, 6 speed presets, 3 modes (Auto/Manual/Standby)

## 🔌 Connection

- **Bluetooth (BLE) only** - directly from Home Assistant to the device
- During setup, the device name **"WalkingPad"** is searched and its **MAC address** is stored
- The WalkingPad must be within **Bluetooth range**
- **No cloud, no internet, no manufacturer servers** - everything runs locally on your network!

## 📦 Installation via HACS

1. Open **HACS** (in the sidebar)
2. Click the **three dots** in the top right → **Custom repositories**
3. Enter this link:
   ```
   https://github.com/bleibdirtroy/walkingpad-hacs
   ```
4. Category: **Integration** → **Add**
5. Search for **"WalkingPad"** and **Download**
6. **Restart Home Assistant**
7. Settings → Devices & Services → **+ Add Integration** → **WalkingPad**

## 📦 Manual Installation

1. Download the `custom_components/walkingpad/` folder
2. Copy it to `/config/custom_components/walkingpad/` on your HA server
3. **Restart Home Assistant**
4. Settings → Devices & Services → **+ Add Integration** → **WalkingPad**

## 🎯 Created Entities

### 📊 Sensors (only real values from the device!)

#### Current Session
| Entity | Description |
|--------|-------------|
| `sensor.walkingpad_speed` | Speed (km/h) |
| `sensor.walkingpad_steps_session` | Steps (current session) |
| `sensor.walkingpad_distance_session` | Distance in km (current session) |
| `sensor.walkingpad_time_session` | Active time (seconds) |
| `sensor.walkingpad_status` | Status (Ready/Running/Paused/Stopped) |

#### 🏆 Total Statistics (persistent across restarts)
| Entity | Description |
|--------|-------------|
| `sensor.walkingpad_total_steps` | **Total steps** (never reset) |
| `sensor.walkingpad_total_distance` | **Total distance** in km (never reset) |

### 🔢 Number (Slider)
| Entity | Description |
|--------|-------------|
| `number.walkingpad_speed` | Speed 0.5-6.0 km/h |

### 🔵 Buttons

| Entity | Description |
|--------|-------------|
| `button.walkingpad_start` | ▶️ Start belt |
| `button.walkingpad_stop` | ⏹️ Stop belt |
| `button.walkingpad_speed_1_0_km_h_slow` | 1.0 km/h 🐢 |
| `button.walkingpad_speed_2_0_km_h_walk` | 2.0 km/h 🚶 |
| `button.walkingpad_speed_3_0_km_h_walking` | 3.0 km/h 🏃 |
| `button.walkingpad_speed_4_0_km_h_jogging` | 4.0 km/h 🏃‍♂️ |
| `button.walkingpad_speed_5_0_km_h_fast` | 5.0 km/h ⚡ |
| `button.walkingpad_speed_6_0_km_h_max` | 6.0 km/h 🚀 |
| `button.walkingpad_mode_auto` | 🤖 Auto mode |
| `button.walkingpad_mode_manual` | ✋ Manual mode |
| `button.walkingpad_mode_standby` | ⏸️ Standby mode |

## 🔧 Services

```yaml
service: walkingpad.start          # Start belt
service: walkingpad.stop           # Stop belt
service: walkingpad.set_speed      # Set speed (data: {speed: 3.5})
```

## 🔗 Credits

- [ph4-walkingpad](https://pypi.org/project/ph4-walkingpad/) - Bluetooth protocol library
- [bleak](https://github.com/hbldh/bleak) - Bluetooth Low Energy for Python

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🤖 AI Usage Disclosure

This project was developed with assistance from AI tools (Claude by Anthropic). The code was reviewed, tested, and adapted for this specific use case. While AI helped with code generation and structure, all functionality has been verified and tested with a real WalkingPad C1 device.
