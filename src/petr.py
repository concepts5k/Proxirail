from pathlib import Path
from collections import defaultdict
import csv

OUT = Path(__file__).resolve().parents[1] / "out"
IOA_THRESH = 0.5

rows = list(csv.DictReader(open(OUT / "events.csv")))
fps = float(next(csv.reader(open(OUT / "meta.csv")))[0])

trains = sorted({int(r["frame"]) for r in rows if r["train"] == "1"})

history = defaultdict(list)
for r in rows:
    if r["tid"]:
        history[int(r["tid"])].append((int(r["frame"]), float(r["ioa"]), r["gates"] == "1"))

pets = []
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
                print(f"Track {tid}: exit {exit_f}, train {after[0]}, PET {pet:.2f}s")
            tagged, exit_f = False, None

if pets:
    pets.sort()
    print(f"\nn={len(pets)}  min {pets[0]:.2f}s  median {pets[len(pets)//2]:.2f}s  max {pets[-1]:.2f}s")