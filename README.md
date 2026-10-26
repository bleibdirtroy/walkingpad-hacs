# WalkingPad Home Assistant Integration 🏃

Custom Integration für KingSmith WalkingPad Laufbänder.

## 📦 Installation

### Schritt 1: Ordner auf HA kopieren

Kopiere den kompletten `walkingpad` Ordner nach:

```
/config/custom_components/walkingpad/
```

**Via SCP/Samba:**
```bash
# Von deinem PC auf den HA Server kopieren
scp -r walkingpad/ root@homeassistant.local:/config/custom_components/
```

**Via File Editor Add-on:**
1. In HA: Add-ons → File Editor → Installieren & Starten
2. Navigiere zu `/config/custom_components/`
3. Erstelle Ordner `walkingpad`
4. Kopiere alle Dateien hinein

### Schritt 2: Home Assistant neu starten

Einstellungen → System → **Neu starten**

### Schritt 3: Integration hinzufügen

1. Einstellungen → Geräte & Dienste → **Integration hinzufügen**
2. Suche nach **"WalkingPad"**
3. Das Gerät wird automatisch erkannt (Name: "WalkingPad")
4. Fertig! ✅

## 🎯 Erstellte Entitäten

Nach der Einrichtung hast du:

### 📊 Sensoren
| Entität | Beschreibung |
|---------|-------------|
| `sensor.walkingpad_geschwindigkeit` | Aktuelle Geschwindigkeit (km/h) |
| `sensor.walkingpad_schritte` | Schrittzahl |
| `sensor.walkingpad_distanz` | Distanz (km) |
| `sensor.walkingpad_aktive_zeit` | Aktive Zeit (Sekunden) |
| `sensor.walkingpad_kalorien` | Geschätzte Kalorien (kcal) |
| `sensor.walkingpad_status` | Status (Bereit/Läuft/Pause/Stop) |

### 🔘 Switch
| Entität | Beschreibung |
|---------|-------------|
| `switch.walkingpad` | Band starten/stoppen |

### 🔢 Number (Slider)
| Entität | Beschreibung |
|---------|-------------|
| `number.walkingpad_geschwindigkeit` | Geschwindigkeit 0.5-6.0 km/h in 0.5er Schritten |

### 🔵 Buttons (Speed Presets)
| Entität | Geschwindigkeit |
|---------|---------------|
| `button.walkingpad_speed_1_0_km_h_langsam` | 1.0 km/h 🐢 |
| `button.walkingpad_speed_2_0_km_h_gehen` | 2.0 km/h 🚶 |
| `button.walkingpad_speed_3_0_km_h_walking` | 3.0 km/h 🏃 |
| `button.walkingpad_speed_4_0_km_h_joggen` | 4.0 km/h 🏃‍♂️ |
| `button.walkingpad_speed_5_0_km_h_schnell` | 5.0 km/h ⚡ |
| `button.walkingpad_speed_6_0_km_h_max` | 6.0 km/h 🚀 |

## 🔧 Services (für Automationen)

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
min: 0
max: 6
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

### Kalorien-Benachrichtigung
```yaml
alias: "100 Kalorien verbrannt!"
trigger:
  - platform: numeric_state
    entity_id: sensor.walkingpad_kalorien
    above: 100
condition:
  - condition: state
    entity_id: switch.walkingpad
    state: "on"
action:
  - service: notify.mobile_app
    data:
      message: "🔥 Du hast 100 kcal verbrannt! Weiter so!"
```

## 🐛 Troubleshooting

| Problem | Lösung |
|---------|--------|
| Integration nicht gefunden | HA neu starten, Ordner prüfen: `/config/custom_components/walkingpad/` |
| "Keine Verbindung" | WalkingPad einschalten, Bluetooth-Reichweite prüfen |
| `ph4-walkingpad` nicht installiert | HA installiert automatisch aus `manifest.json` requirements |
| Mehrere Geräte | MAC-Adresse wird automatisch gespeichert |

## 📁 Dateistruktur

```
walkingpad/
├── manifest.json          # Metadaten & Abhängigkeiten
├── __init__.py            # Haupt-Setup
├── config_flow.py         # Einrichtungs-Assistent
├── const.py               # Konstanten
├── coordinator.py         # Bluetooth-Kommunikation
├── sensor.py              # Sensoren
├── switch.py              # An/Aus-Schalter
├── number.py              # Geschwindigkeits-Slider
├── button.py              # Speed-Presets
├── services.yaml          # Service-Definitionen
├── strings.json           # UI-Texte
└── translations/
    ├── de.json            # Deutsch
    └── en.json            # Englisch
```

## 🔗 Basierend auf

- [ph4-walkingpad](https://pypi.org/project/ph4-walkingpad/) - Bluetooth Protokoll
- [bleak](https://github.com/hbldh/bleak) - Bluetooth Low Energy

Viel Spaß! 🚶‍♂️💨
