from pathlib import Path
from collections import defaultdict
import csv, cv2, numpy as np

BASE = Path(__file__).resolve().parents[1]
ZONE_LABEL = BASE / "Data" / "Geo_data-4" / "train" / "labels" / "CG_Up_png.txt"
VIDEO_IN = BASE / "Data" / "Samps" / "Main_Samp.mp4"
OUT = BASE / "out"
SLICE = 0.15
FRESH = 30               # frames an exit stays highlighted before dimming

cap = cv2.VideoCapture(str(VIDEO_IN))
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 10**7
fps = cap.get(cv2.CAP_PROP_FPS) or 30
vw = cv2.VideoWriter(str(OUT / "viz.mp4"),
                     cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))

zone_pts = []
for line in open(ZONE_LABEL):
    c = list(map(float, line.split()[1:]))
    pts = [(c[i] * W, c[i + 1] * H) for i in range(0, len(c), 2)]
    if len(pts) >= 3:
        zone_pts.append(np.array(pts, np.int32))

by_frame = defaultdict(list)
for r in csv.DictReader(open(OUT / "events.csv")):
    by_frame[int(r["frame"])].append(r)

exits = defaultdict(list)                     # coords resolved once, then persisted
for n, r in enumerate(csv.DictReader(open(OUT / "exits.csv"))):
    f0 = int(r["exit_frame"])
    src = next((e for e in by_frame.get(f0, []) if e["tid"] == r["tid"]), None)
    if not src:
        continue
    cx = int((float(src["x1"]) + float(src["x2"])) / 2)
    cy = int(float(src["y2"]))
    rec = (f0, int(r["tid"]), float(r["pet"]), cx, cy, n)
    for k in range(f0, N + 1):
        exits[k].append(rec)

idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    idx += 1

    ov = frame.copy()                      # translucent danger zone
    cv2.fillPoly(ov, zone_pts, (0, 0, 200))
    frame = cv2.addWeighted(ov, 0.25, frame, 0.75, 0)
    cv2.polylines(frame, zone_pts, True, (0, 0, 255), 2)

    rows = by_frame.get(idx, [])
    if rows and rows[0]["tx1"]:            # train box
        tx1, ty1, tx2, ty2 = (int(float(rows[0][k])) for k in ("tx1","ty1","tx2","ty2"))
        cv2.rectangle(frame, (tx1, ty1), (tx2, ty2), (255, 160, 0), 3)
        cv2.putText(frame, "TRAIN", (tx1, ty1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 160, 0), 2)

    for r in rows:                         # people
        if not r["tid"]:
            continue
        x1, y1, x2, y2 = (int(float(r[k])) for k in ("x1", "y1", "x2", "y2"))
        ioa = float(r["ioa"])
        col = (0, int(255 * (1 - ioa)), int(255 * ioa))   # green -> red
        cv2.rectangle(frame, (x1, y1), (x2, y2), col, 2)
        ys = int(y2 - (y2 - y1) * SLICE)                  # the slice you measure
        cv2.rectangle(frame, (x1, ys), (x2, y2), col, -1 if ioa > 0 else 1)
        cv2.putText(frame, f"{r['tid']} IoA {ioa:.2f}", (x1, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2)

    for f0, tid, pet, cx, cy, n in exits.get(idx, []):    # persistent exit markers
        fresh = idx - f0 < FRESH
        col = (0, 255, 255) if fresh else (0, 190, 190)
        cv2.line(frame, (cx, 0), (cx, H), col, 2 if fresh else 1)
        cv2.drawMarker(frame, (cx, cy), col, cv2.MARKER_STAR, 26, 3)
        ly = 60 + (n % 6) * 22             # stagger so labels don't stack
        cv2.putText(frame, f"{tid}  PET {pet:.2f}s", (cx + 8, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, col, 2)

    cv2.putText(frame, f"f{idx}  gates={rows[0]['gates'] if rows else '?'}",
                (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    vw.write(frame)

cap.release()
vw.release()
