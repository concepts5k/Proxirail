from ultralytics import YOLO
from shapely import Polygon, box, union_all
from pathlib import Path
import csv
import cv2

BASE = Path(__file__).resolve().parents[1]
ZONE_LABEL = BASE / "Data" / "Geo_data-4" / "train" / "labels" / "CG_Up_png.txt"
VIDEO_IN = BASE / "Data" / "Samps" / "Main_Samp.mp4"
OUT = BASE / "out"

PERSON, TRAIN, GATES_DOWN = 0, 6, 0 #classes
SLICE = 0.15 #bottom slice of box for IoA

m1 = YOLO("yolo11n.pt")
m2 = YOLO("models/yolov11cg.pt")

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
f = open(OUT / "events.csv", "w", newline="")
out = csv.writer(f)
out.writerow(["frame", "gates", "train", "tx1", "ty1", "tx2", "ty2",
              "tid", "x1", "y1", "x2", "y2", "ioa"])

idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    idx += 1

    gates = int(any(int(d.cls) == GATES_DOWN for d in m2(frame)[0].boxes))

    r = m1.track(frame, persist=True, tracker="deepocsort.yaml")[0] #yolo 11pt called for IoA
    boxes = r.boxes.xyxy.tolist()
    clss = r.boxes.cls.int().tolist()
    tids = r.boxes.id.int().tolist() if r.boxes.id is not None else [-1] * len(boxes)

    tbox = next((b for b, c in zip(boxes, clss)
                 if c == TRAIN and box(*b).intersects(zone)), None)
    train = int(tbox is not None)
    tb = [round(v, 1) for v in tbox] if tbox else ["", "", "", ""]

    people = [(t, b) for t, b, c in zip(tids, boxes, clss) if c == PERSON] #IoA calc
    if not people:
        out.writerow([idx, gates, train, "", ""])
    for tid, b in people:
        x1, y1, x2, y2 = b
        p = box(x1, y2 - (y2 - y1) * SLICE, x2, y2)
        ioa = round(p.intersection(zone).area / p.area, 4)
        out.writerow([idx, gates, train, *tb, tid,
                      *[round(v, 1) for v in b], ioa])

cap.release()
f.close()

with open(OUT / "meta.csv", "w", newline="") as m:
    csv.writer(m).writerow([fps])
