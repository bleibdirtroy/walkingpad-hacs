# WalkingPad 🏃

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Custom Integration für **KingSmith WalkingPad** Laufbänder - Bluetooth Steuerung direkt aus Home Assistant!

> ⚠️ **Nur mit KingSmith WalkingPad C1 getestet!**
> Funktioniert bisher nur mit diesem Modell (ggf. auch A1, R1 PRO - nicht getestet).

---

## ✨ Features

- 📊 **Live-Sensoren**: Schritte, Distanz, Geschwindigkeit, Zeit, Status (alle echten Werte vom Gerät)
- 🏆 **Gesamt-Statistik**: Schritte & Distanz GESAMT (bleiben über Neustarts gespeichert)
- 🔢 **Slider**: Geschwindigkeit 0.5-6.0 km/h (0.5er Schritte)
- 🔵 **Buttons**: Start, Stop, 6 Speed-Presets, 3 Modi (Auto/Manuell/Standby)
- 🔍 **Auto-Discovery**: Findet dein WalkingPad automatisch

## 📦 Installation via HACS

1. **HACS öffnen** (im Seitenmenü)
2. Auf die **drei Punkte** oben rechts klicken → **Benutzerdefinierte Repositories**
3. Diesen Link einfügen:
   ```
   https://github.com/bleibdirtroy/walkingpad-hacs
   ```
4. Kategorie: **Integration** → **Hinzufügen**
5. Nach **"WalkingPad"** suchen und **Downloaden**
6. **Home Assistant neu starten**
7. Einstellungen → Geräte & Dienste → **+ Integration hinzufügen** → **WalkingPad**

## 📦 Manuelle Installation

1. Lade den Ordner `custom_components/walkingpad/` herunter
2. Kopiere ihn nach `/config/custom_components/walkingpad/` auf deinem HA Server
3. **Home Assistant neu starten**
4. Einstellungen → Geräte & Dienste → **+ Integration hinzufügen** → **WalkingPad**

## 🎯 Erstellte Entitäten

### 📊 Sensoren (nur echte Werte vom Gerät!)

#### Aktuelle Session
| Entität | Beschreibung |
|---------|-------------|
| `sensor.walkingpad_geschwindigkeit` | Geschwindigkeit (km/h) |
| `sensor.walkingpad_schritte_session` | Schritte (aktuelle Session) |
| `sensor.walkingpad_distanz_session` | Distanz in km (aktuelle Session) |
| `sensor.walkingpad_zeit_session` | Aktive Zeit (Sekunden) |
| `sensor.walkingpad_status` | Status (Bereit/Läuft/Pause/Stop) |

#### 🏆 Gesamt-Statistik (persistent über Neustarts)
| Entität | Beschreibung |
|---------|-------------|
| `sensor.walkingpad_schritte_gesamt` | **Schritte GESAMT** (nie zurückgesetzt) |
| `sensor.walkingpad_distanz_gesamt` | **Distanz GESAMT** in km (nie zurückgesetzt) |

> ℹ️ **Hinweis:** Das WalkingPad liefert keine Kalorien-Daten. Alle Sensoren zeigen **echte Messwerte vom Gerät**.

### 🔢 Number (Slider)
| Entität | Beschreibung |
|---------|-------------|
| `number.walkingpad_geschwindigkeit` | Geschwindigkeit 0.5-6.0 km/h |

### 🔵 Buttons

| Entität | Beschreibung |
|---------|-------------|
| `button.walkingpad_start` | ▶️ Band starten |
| `button.walkingpad_stop` | ⏹️ Band stoppen |
| `button.walkingpad_speed_1_0_km_h_langsam` | 1.0 km/h 🐢 |
| `button.walkingpad_speed_2_0_km_h_gehen` | 2.0 km/h 🚶 |
| `button.walkingpad_speed_3_0_km_h_walking` | 3.0 km/h 🏃 |
| `button.walkingpad_speed_4_0_km_h_joggen` | 4.0 km/h 🏃‍♂️ |
| `button.walkingpad_speed_5_0_km_h_schnell` | 5.0 km/h ⚡ |
| `button.walkingpad_speed_6_0_km_h_max` | 6.0 km/h 🚀 |
| `button.walkingpad_modus_auto` | 🤖 Auto-Modus |
| `button.walkingpad_modus_manuell` | ✋ Manueller Modus |
| `button.walkingpad_modus_standby` | ⏸️ Standby-Modus |

## 🔧 Services

```yaml
service: walkingpad.start          # Band starten
service: walkingpad.stop           # Band stoppen
service: walkingpad.set_speed      # Geschwindigkeit setzen (data: {speed: 3.5})
```

## 🐛 Troubleshooting

- **"Keine Verbindung"** → WalkingPad einschalten, Bluetooth-Reichweite prüfen
- **Funktioniert nicht** → Nur mit **WalkingPad C1** getestet, andere Modelle nicht getestet!

## 🔗 Credits

- [ph4-walkingpad](https://pypi.org/project/ph4-walkingpad/) - Bluetooth Protokoll Library
- [bleak](https://github.com/hbldh/bleak) - Bluetooth Low Energy für Python

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE)
