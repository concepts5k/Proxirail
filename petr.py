from pathlib import Path
from collections import defaultdict
import csv

OUT = Path(__file__).resolve().parents[1] / "out"
IOA_THRESH = 0.75

rows = list(csv.DictReader(open(OUT / "events.csv")))
fps = float(next(csv.reader(open(OUT / "meta.csv")))[0])

trains = sorted({int(r["frame"]) for r in rows if r["train"] == "1"})

history = defaultdict(list)
for r in rows:
    if r["tid"] and int(r["tid"]) != -1:
        history[int(r["tid"])].append((int(r["frame"]), float(r["ioa"]), r["gates"] == "1"))

pets = []
exits = []

for tid, series in sorted(history.items()):
    tagged, exit_f = False, None
    for f, ioa, gates in series:
        if gates and ioa >= IOA_THRESH:
            tagged = True
        if tagged and ioa > 0:
            exit_f = f
        elif tagged and ioa == 0:
            after = [t for t in trains if t > exit_f]
            if after:
                pet = (after[0] - exit_f) / fps
                pets.append(pet)
                exits.append((exit_f, tid, after[0], round(pet, 2)))
                print(f"Track {tid}: exit {exit_f}, train {after[0]}, PET {pet:.2f}s")
            tagged, exit_f = False, None

    with open(OUT / "exits.csv", "w", newline="") as e:   # <-- 3. after both loops close
        w = csv.writer(e)
        w.writerow(["exit_frame", "tid", "train_frame", "pet"])
        w.writerows(sorted(exits))

if pets:
    pets.sort()
    print(f"\nn={len(pets)}  min {pets[0]:.2f}s  median {pets[len(pets)//2]:.2f}s  max {pets[-1]:.2f}s")