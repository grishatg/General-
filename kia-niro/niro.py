#!/usr/bin/env python3
"""Command-line control for a Kia Niro EV via the Kia Connect (EU) cloud.

Uses the open-source hyundai_kia_connect_api library, the same back end the
Home Assistant Kia/Hyundai integration uses. It does the same things as the
official app, from a script.

Credentials come from environment variables, so they never live in code:
    KIA_USERNAME   Kia Connect email
    KIA_PASSWORD   Kia Connect password
    KIA_PIN        4-digit Kia Connect PIN (needed for remote commands)
"""
import argparse
import os
import sys

from hyundai_kia_connect_api import ClimateRequestOptions, VehicleManager

REGION_EUROPE = 1
BRAND_KIA = 1


def connect() -> VehicleManager:
    missing = [k for k in ("KIA_USERNAME", "KIA_PASSWORD", "KIA_PIN") if not os.environ.get(k)]
    if missing:
        sys.exit(f"Set these environment variables first: {', '.join(missing)}")
    vm = VehicleManager(
        region=REGION_EUROPE,
        brand=BRAND_KIA,
        username=os.environ["KIA_USERNAME"],
        password=os.environ["KIA_PASSWORD"],
        pin=os.environ["KIA_PIN"],
        language="en",
    )
    vm.check_and_refresh_token()
    return vm


def pick_vehicle(vm: VehicleManager):
    if not vm.vehicles:
        sys.exit("No vehicles found on this Kia Connect account.")
    return next(iter(vm.vehicles.values()))


def yes_no(value) -> str:
    return "?" if value is None else ("yes" if value else "no")


def show_status(v) -> None:
    rng = v.ev_driving_range
    print(f"{v.name or 'Vehicle'} ({v.model or 'unknown model'})")
    print(f"  Battery:        {v.ev_battery_percentage}%")
    print(f"  Range:          {rng} {v.ev_driving_range_unit or ''}".rstrip())
    print(f"  Plugged in:     {yes_no(v.ev_battery_is_plugged_in)}")
    print(f"  Charging:       {yes_no(v.ev_battery_is_charging)}")
    print(f"  Charge limits:  AC {v.ev_charge_limits_ac}% / DC {v.ev_charge_limits_dc}%")
    print(f"  Locked:         {yes_no(v.is_locked)}")
    print(f"  Bonnet open:    {yes_no(v.hood_is_open)}")
    print(f"  Climate on:     {yes_no(v.air_control_is_on)}")
    print(f"  12V battery:    {v.car_battery_percentage}%")
    print(f"  Odometer:       {v.odometer}")
    if v.ev_battery_soh_percentage is not None:
        print(f"  Battery health: {v.ev_battery_soh_percentage}%")
    print(f"  Last update:    {v.last_updated_at}")


def climate_blockers(v) -> list[str]:
    """Common reasons Kia rejects remote climate ('Please check your vehicle status')."""
    problems = []
    if v.is_locked is False:
        problems.append("car is UNLOCKED - lock it first (run: niro.py lock)")
    if v.hood_is_open:
        problems.append("bonnet is open")
    if v.engine_is_running:
        problems.append("car is switched on / in Ready mode")
    if v.ev_battery_percentage is not None and v.ev_battery_percentage < 20:
        problems.append("battery is low; remote climate may be refused unless plugged in")
    return problems


def main() -> None:
    p = argparse.ArgumentParser(description="Control your Kia Niro EV via Kia Connect")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status", help="Show the car's status")
    s.add_argument("--refresh", action="store_true",
                   help="Wake the car for fresh data (uses the 12V battery and daily API quota)")

    c = sub.add_parser("climate-on", help="Start pre-conditioning")
    c.add_argument("--temp", type=float, default=21.0, help="Target temperature in C (default 21)")
    c.add_argument("--minutes", type=int, default=15, help="Duration, 1-30 (default 15)")
    c.add_argument("--defrost", action="store_true", help="Front windscreen defrost")
    c.add_argument("--heat", action="store_true", help="Heated rear screen and mirrors")
    c.add_argument("--force", action="store_true", help="Send even if the pre-checks fail")

    sub.add_parser("climate-off", help="Stop climate")
    sub.add_parser("lock", help="Lock the doors")
    sub.add_parser("unlock", help="Unlock the doors")
    sub.add_parser("charge-start", help="Start charging (must be plugged in)")
    sub.add_parser("charge-stop", help="Stop charging")

    lim = sub.add_parser("charge-limit", help="Set AC and DC charge limits")
    lim.add_argument("ac", type=int, choices=range(50, 101, 10), metavar="AC", help="50-100, steps of 10")
    lim.add_argument("dc", type=int, choices=range(50, 101, 10), metavar="DC", help="50-100, steps of 10")

    args = p.parse_args()
    vm = connect()

    if args.cmd == "status" and args.refresh:
        vm.force_refresh_all_vehicles_states()
    vm.update_all_vehicles_with_cached_state()
    v = pick_vehicle(vm)

    if args.cmd == "status":
        show_status(v)
        return

    if args.cmd == "climate-on":
        problems = climate_blockers(v)
        if problems and not args.force:
            print("Kia is likely to reject this. Fix first (or re-run with --force):")
            for prob in problems:
                print(f"  - {prob}")
            sys.exit(1)
        opts = ClimateRequestOptions(
            set_temp=args.temp,
            duration=max(1, min(args.minutes, 30)),
            climate=True,
            defrost=args.defrost,
            heating=1 if args.heat else 0,
        )
        result = vm.start_climate(v.id, opts)
    elif args.cmd == "climate-off":
        result = vm.stop_climate(v.id)
    elif args.cmd == "lock":
        result = vm.lock(v.id)
    elif args.cmd == "unlock":
        result = vm.unlock(v.id)
    elif args.cmd == "charge-start":
        result = vm.start_charge(v.id)
    elif args.cmd == "charge-stop":
        result = vm.stop_charge(v.id)
    elif args.cmd == "charge-limit":
        result = vm.set_charge_limits(v.id, args.ac, args.dc)
    else:
        p.error("unknown command")

    print(f"Sent '{args.cmd}' to the car. Kia request id: {result}")
    print("It can take 30-60 seconds to apply. Check with: niro.py status --refresh")


if __name__ == "__main__":
    main()
