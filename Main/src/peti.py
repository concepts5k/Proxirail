from pathlib import Path
from collections import defaultdict
import csv

OUT = Path(__file__).resolve().parents[1] / "out"
IOA_THRESH = 0.75

rows = list(csv.DictReader(open(OUT / "Ievents.csv")))
fps = float(next(csv.reader(open(OUT / "Imeta.csv")))[0])

# frames where a vehicle is touching the zone -> (frame, type)
vehicles = sorted(
    {(int(r["frame"]), "car") for r in rows if r["car"] == "1"}
    | {(int(r["frame"]), "truck") for r in rows if r["truck"] == "1"}
)

history = defaultdict(list)
for r in rows:
    if r["tid"] and int(r["tid"]) != -1:
        history[int(r["tid"])].append((int(r["frame"]), float(r["ioa"])))

pets = []
exits = []

for tid, series in sorted(history.items()):
    tagged, exit_f = False, None
    for f, ioa in series:
        if ioa >= IOA_THRESH:
            tagged = True
        if tagged and ioa > 0:
            exit_f = f
        elif tagged and ioa == 0:
            after = [v for v in vehicles if v[0] > exit_f]
            if after:
                veh_f, veh_type = after[0]
                pet = (veh_f - exit_f) / fps
                pets.append(pet)
                exits.append((exit_f, tid, veh_f, veh_type, round(pet, 2)))
                print(f"Track {tid}: exit {exit_f}, {veh_type} {veh_f}, PET {pet:.2f}s")
            tagged, exit_f = False, None

with open(OUT / "Iexits.csv", "w", newline="") as e:
    w = csv.writer(e)
    w.writerow(["exit_frame", "tid", "veh_frame", "veh_type", "pet"])
    w.writerows(sorted(exits))

if pets:
    pets.sort()
    print(f"\nn={len(pets)}  min {pets[0]:.2f}s  median {pets[len(pets)//2]:.2f}s  max {pets[-1]:.2f}s")
