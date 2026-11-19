# Kia Niro EV: control from a script

Controls the car through Kia Connect (EU), the same cloud the official app
uses, via the open-source [hyundai_kia_connect_api](https://github.com/Hyundai-Kia-Connect/hyundai_kia_connect_api)
library. Nothing on the car itself is modified, so warranty and MOT are unaffected.

## Setup (once)

```bash
cd kia-niro
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export KIA_USERNAME="you@example.com"
export KIA_PASSWORD="your-kia-connect-password"
export KIA_PIN="1234"
```

Keep the credentials in your shell profile or a password manager. Never commit them.

## Commands

| Command | What it does |
|---|---|
| `python niro.py status` | Battery, range, lock state, charging, 12V level (cached, doesn't wake the car) |
| `python niro.py status --refresh` | Wakes the car for live data |
| `python niro.py climate-on --temp 21 --minutes 15 --defrost` | Pre-conditioning |
| `python niro.py climate-off` | Stop climate |
| `python niro.py lock` / `unlock` | Doors |
| `python niro.py charge-start` / `charge-stop` | Charging |
| `python niro.py charge-limit 80 90` | AC limit 80%, DC limit 90% |

## "Cannot start climate control. Please check your vehicle status."

Kia refuses remote climate when any of these is true. `climate-on` checks them first:
- the doors are **unlocked** (the most common cause)
- the bonnet is open
- the car is switched on / in Ready mode
- the battery is low and the car isn't plugged in

## Things to know
- Kia's EU API caps the number of calls per day (roughly 200). `--refresh` wakes the car and drains the 12V battery a little, so don't run it in a tight loop.
- For automations (e.g. pre-heat at 07:30 on weekdays, cap charging at 80%), the Home Assistant "Kia UVO / Hyundai Bluelink" integration uses this same library.
