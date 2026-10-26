# WalkingPad 🏃

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Custom Integration für **KingSmith WalkingPad** Laufbänder - Bluetooth Steuerung direkt aus Home Assistant!

## ✨ Features

- 📊 **Live-Sensoren**: Schritte, Distanz, Geschwindigkeit, Zeit, Kalorien, Status
- 🔘 **Switch**: Band starten/stoppen
- 🔢 **Slider**: Geschwindigkeit 0.5-6.0 km/h (0.5er Schritte)
- 🔵 **6 Speed-Presets**: Schnellzugriff auf voreingestellte Geschwindigkeiten
- 🤖 **Services**: Für Automationen nutzbar
- 🔍 **Auto-Discovery**: Findet dein WalkingPad automatisch

## 📦 Installation via HACS (empfohlen)

1. **HACS öffnen** (im Seitenmenü)
2. Auf die **drei Punkte** oben rechts klicken → **Benutzerdefinierte Repositories**
3. Diesen Link einfügen:
   ```
   https://github.com/troy/walkingpad-ha
   ```
4. Kategorie: **Integration**
5. **Hinzufügen** klicken
6. Nach **"WalkingPad"** suchen und **Downloaden**
7. **Home Assistant neu starten**
8. Einstellungen → Geräte & Dienste → **+ Integration hinzufügen** → **WalkingPad**

## 📦 Manuelle Installation

1. Lade den Ordner `custom_components/walkingpad/` herunter
2. Kopiere ihn nach `/config/custom_components/walkingpad/` auf deinem HA Server
3. **Home Assistant neu starten**
4. Einstellungen → Geräte & Dienste → **+ Integration hinzufügen** → **WalkingPad**

## 🎯 Erstellte Entitäten

### 📊 Sensoren

#### Aktuelle Session (werden bei Neustart des Geräts zurückgesetzt)
| Entität | Beschreibung | Quelle |
|---------|-------------|--------|
| `sensor.walkingpad_geschwindigkeit` | Aktuelle Geschwindigkeit (km/h) | ✅ Gerät |
| `sensor.walkingpad_schritte_session` | Schritte (aktuelle Session) | ✅ Gerät |
| `sensor.walkingpad_distanz_session` | Distanz in km (aktuelle Session) | ✅ Gerät |
| `sensor.walkingpad_zeit_session` | Aktive Zeit (Sekunden) | ✅ Gerät |
| `sensor.walkingpad_status` | Status (Bereit/Läuft/Pause/Stop) | ✅ Gerät |

#### 🏆 Gesamt-Statistik (bleibt über Neustarts gespeichert!)
| Entität | Beschreibung | Quelle |
|---------|-------------|--------|
| `sensor.walkingpad_schritte_gesamt` | **Schritte GESAMT** (nie zurückgesetzt) | ✅ Gerät |
| `sensor.walkingpad_distanz_gesamt` | **Distanz GESAMT** in km (nie zurückgesetzt) | ✅ Gerät |

> 💡 Die Gesamt-Sensoren speichern ihren Wert automatisch und setzen sich **nicht** zurück, wenn das WalkingPad oder Home Assistant neu gestartet wird!
> 
> ℹ️ **Hinweis:** Das WalkingPad liefert keine Kalorien-Daten. Alle Sensoren zeigen **echte Messwerte vom Gerät**.

### 🔢 Number (Slider)
| Entität | Beschreibung |
|---------|-------------|
| `number.walkingpad_geschwindigkeit` | Geschwindigkeit 0.5-6.0 km/h |

### 🔵 Buttons

#### Start/Stop
| Entität | Beschreibung |
|---------|-------------|
| `button.walkingpad_start` | ▶️ Band starten |
| `button.walkingpad_stop` | ⏹️ Band stoppen |

#### Speed Presets
| Entität | Geschwindigkeit |
|---------|---------------|
| `button.walkingpad_speed_1_0_km_h_langsam` | 1.0 km/h 🐢 |
| `button.walkingpad_speed_2_0_km_h_gehen` | 2.0 km/h 🚶 |
| `button.walkingpad_speed_3_0_km_h_walking` | 3.0 km/h 🏃 |
| `button.walkingpad_speed_4_0_km_h_joggen` | 4.0 km/h 🏃‍♂️ |
| `button.walkingpad_speed_5_0_km_h_schnell` | 5.0 km/h ⚡ |
| `button.walkingpad_speed_6_0_km_h_max` | 6.0 km/h 🚀 |

#### Modi
| Entität | Beschreibung |
|---------|-------------|
| `button.walkingpad_modus_auto` | 🤖 Auto-Modus (automatische Geschwindigkeitsregelung) |
| `button.walkingpad_modus_manuell` | ✋ Manueller Modus (feste Geschwindigkeit) |
| `button.walkingpad_modus_standby` | ⏸️ Standby-Modus |

## 🔧 Services

```yaml
# Band starten
service: walkingpad.start

# Band stoppen
service: walkingpad.stop

# Geschwindigkeit setzen
service: walkingpad.set_speed
data:
  speed: 3.5
```

## 🃏 Lovelace Karte Beispiel

```yaml
type: entities
title: 🏃 WalkingPad
entities:
  - switch.walkingpad
  - number.walkingpad_geschwindigkeit
  - sensor.walkingpad_status
  - sensor.walkingpad_geschwindigkeit
  - sensor.walkingpad_schritte
  - sensor.walkingpad_distanz
  - sensor.walkingpad_aktive_zeit
  - sensor.walkingpad_kalorien
---
type: glance
title: Speed Presets
entities:
  - button.walkingpad_speed_2_0_km_h_gehen
  - button.walkingpad_speed_3_0_km_h_walking
  - button.walkingpad_speed_4_0_km_h_joggen
  - button.walkingpad_speed_6_0_km_h_max
---
type: gauge
entity: sensor.walkingpad_geschwindigkeit
name: Geschwindigkeit
min: 0
max: 6
unit: km/h
severity:
  green: 0
  yellow: 3
  red: 5
```

## 🤖 Automationen Beispiele

### Beim Nachhausekommen starten
```yaml
alias: "WalkingPad beim Nachhausekommen"
trigger:
  - platform: zone
    entity_id: person.troy
    zone: zone.home
    event: enter
action:
  - service: walkingpad.set_speed
    data:
      speed: 3.0
  - service: switch.turn_on
    target:
      entity_id: switch.walkingpad
```

### Nach 30 Minuten stoppen
```yaml
alias: "WalkingPad nach 30 Minuten stoppen"
trigger:
  - platform: state
    entity_id: switch.walkingpad
    to: "on"
    for:
      minutes: 30
action:
  - service: switch.turn_off
    target:
      entity_id: switch.walkingpad
```

## 🐛 Troubleshooting

| Problem | Lösung |
|---------|--------|
| Integration nicht in HACS | Repo-URL prüfen, HACS neu laden |
| "Keine Verbindung" | WalkingPad einschalten, Bluetooth-Reichweite prüfen |
| `ph4-walkingpad` fehlt | Wird automatisch aus `manifest.json` installiert |
| Nach Update Probleme | HA neu starten, Cache leeren |

## 📁 Projekt-Struktur

```
├── custom_components/
│   └── walkingpad/
│       ├── manifest.json
│       ├── __init__.py
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── sensor.py
│       ├── switch.py
│       ├── number.py
│       ├── button.py
│       ├── services.yaml
│       ├── strings.json
│       └── translations/
├── hacs.json
├── README.md
└── .github/
    └── workflows/
        ├── hacs.yaml
        └── validate.yaml
```

## 🔗 Credits

- [ph4-walkingpad](https://pypi.org/project/ph4-walkingpad/) - Bluetooth Protokoll Library
- [bleak](https://github.com/hbldh/bleak) - Bluetooth Low Energy für Python
- [HACS](https://hacs.xyz/) - Home Assistant Community Store

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE)

---

**Viel Spaß beim Walken!** 🚶‍♂️💨
