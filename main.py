import time
import csv
import os
from datetime import datetime
from collections import deque

class Charger:
    def __init__(self, cid, power_kw):
        self.cid = cid
        self.power_kw = power_kw
        self.busy = False

class Vehicle:
    def __init__(self, name, capacity_kwh, battery_pct):
        self.name = name
        self.capacity = capacity_kwh
        self.battery = battery_pct

RATE = 10  # cost per kWh

chargers = [Charger(1, 7), Charger(2, 22), Charger(3, 50)]

def show_chargers():
    for c in chargers:
        state = "Occupied" if c.busy else "Available"
        print(f"Charger {c.cid} ({c.power_kw} kW): {state}")

def save_session(vehicle, charger, energy, cost):
    file_exists = os.path.exists("sessions.csv")
    with open("sessions.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["time", "vehicle", "charger", "energy_kwh", "cost"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            vehicle.name,
            charger.cid,
            round(energy, 2),
            round(cost, 2),
        ])

def charge(vehicle, charger, target=100):
    charger.busy = True
    start = vehicle.battery
    while vehicle.battery < target:
        kwh = charger.power_kw / 60
        vehicle.battery = min(100, vehicle.battery + kwh / vehicle.capacity * 100)
        print(f"{vehicle.name}: {vehicle.battery:.1f}%")
        time.sleep(0.2)
    charger.busy = False
    used = (vehicle.battery - start) / 100 * vehicle.capacity
    print(f"Done. Energy: {used:.2f} kWh, Cost: {used * RATE:.2f}")
    save_session(vehicle, charger, used, used * RATE)

queue = deque()

def add_to_queue():
    name = input("Vehicle name: ")
    cap = float(input("Battery capacity (kWh): "))
    pct = float(input("Current battery %: "))
    queue.append(Vehicle(name, cap, pct))
    print(f"{name} added. Waiting: {len(queue)}")

def process_queue():
    if not queue:
        print("Queue is empty.")
        return
    while queue:
        free = next((c for c in chargers if not c.busy), None)
        if free is None:
            print("No free charger.")
            break
        v = queue.popleft()
        print(f"\n{v.name} -> Charger {free.cid}")
        charge(v, free)

def main():
    while True:
        print("\n1. Show chargers\n2. Start charging\n3. Add to queue")
        print("4. Process queue\n5. View history\n6. Exit")
        choice = input("Choose: ")
        if choice == "1":
            show_chargers()
        elif choice == "2":
            show_chargers()
            cid = int(input("Charger number: "))
            charger = next((c for c in chargers if c.cid == cid), None)
            if charger is None or charger.busy:
                print("Not available.")
                continue
            v = Vehicle("EV", 40, float(input("Current battery %: ")))
            charge(v, charger)
        elif choice == "3":
            add_to_queue()
        elif choice == "4":
            process_queue()
        elif choice == "5":
            if os.path.exists("sessions.csv"):
                print(open("sessions.csv").read())
            else:
                print("No sessions yet.")
        elif choice == "6":
            break

main()