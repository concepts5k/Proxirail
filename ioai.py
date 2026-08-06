import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from ultralytics import YOLO
from shapely import Polygon, box, union_all
from shapely.geometry import MultiPolygon
from pathlib import Path
import csv
import cv2
import numpy as np

BASE = Path(__file__).resolve().parents[2]
ZONE_LABEL = BASE / "Data" / "Cros-2" / "train" / "labels" / "I_Samp1.txt"
VIDEO_IN = BASE / "Data" / "Samps" / "I_Samp.mp4"
OUT = BASE / "out"

PERSON, CAR, TRUCK = 0, 2, 6 #classes
SLICE = 0.15 #bottom slice of box for IoA

m1 = YOLO("yolo11n.pt")


cap = cv2.VideoCapture(str(VIDEO_IN))
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS) or 30

polys = [] #reading polygons from txt
for line in open(ZONE_LABEL):
    c = list(map(float, line.split()[1:]))
    pts = [(c[i] * W, c[i + 1] * H) for i in range(0, len(c), 2)]
    if len(pts) >= 3:
        polys.append(Polygon(pts))
zone = union_all(polys)

OUT.mkdir(exist_ok=True) #CSV writing
f = open(OUT / "Ievents.csv", "w", newline="")
out = csv.writer(f)
out.writerow(["frame", "car", "truck", "tid", "ioa"])

fourcc = cv2.VideoWriter_fourcc(*"MJPG")
vid_out = cv2.VideoWriter(str(OUT / "vis.avi"), fourcc, fps, (W,H))

idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    idx += 1

    r = m1.track(frame, persist=True, tracker="deepocsort.yaml")[0] #yolo 11pt called for IoA
    boxes = r.boxes.xyxy.tolist()
    clss = r.boxes.cls.int().tolist()
    tids = r.boxes.id.int().tolist() if r.boxes.id is not None else []

    car = int(any(box(*b).intersects(zone) for b, c in zip(boxes, clss) if c == CAR))
    truck = int(any(box(*b).intersects(zone) for b, c in zip(boxes, clss) if c == TRUCK))


    zone_polys = zone.geoms if isinstance(zone, MultiPolygon) else [zone]
    for zp in zone_polys:
        zone_pts = np.array(zp.exterior.coords, dtype=np.int32)
        cv2.polylines(frame, [zone_pts], True, (0,255,255), 2)

    people = [(t, b) for t, b, c in zip(tids, boxes, clss) if c == PERSON] #IoA calc
    if not people:
        out.writerow([idx, car, truck, "", ""])
    for tid, b in people:
        x1, y1, x2, y2 = b
        p = box(x1, y2 - (y2 - y1) * SLICE, x2, y2)
        ioa = round(p.intersection(zone).area / p.area, 4)
        out.writerow([idx, car, truck, tid, ioa])
        #visualize ioa/person
        color = (0, 0, 255) if ioa >= 0.5 else (0,255,0)
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        #visualize slice
        slice_y = int(y2 - (y2-y1) * SLICE)
        cv2.rectangle(frame, (int(x1), slice_y), (int(x2), int(y2)), color, 1)
        #label id and ioa
        label = f"ID:{tid} IoA:{ioa:.2f}"
        cv2.putText(frame, label, (int(x1), int(y1) - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    #car flag
    if car or truck:
        cv2.putText(frame, "CAR IN ZONE", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    vid_out.write(frame)


cap.release()
vid_out.release()
f.close()

with open(OUT / "Imeta.csv", "w", newline="") as m:
    csv.writer(m).writerow([fps])

