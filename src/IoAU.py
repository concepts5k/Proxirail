from ultralytics import YOLO
from shapely import Polygon, box, union_all
from pathlib import Path
import cv2
import numpy as np

BASE = Path(__file__).resolve().parents[1]
LABELS_DIR = BASE / "Data" / "Geo_data-4" / "train" / "labels"
VIDS_DIR = BASE / "Data" / "Samps"

ZONE_LABEL = LABELS_DIR / "CG_Up_png.txt"
VIDEO_IN = VIDS_DIR / "Main_Samp.mp4"
VIDEO_OUT = BASE / "output.mp4"


def danger_zone(txt_label, img_w, img_h):
    """Turns the segmented frame's label into a polygon to do math on."""
    rail = []
    with open(txt_label, "r") as f:
        for line in f:
            parts = f.readline().strip().split()
            if not parts:
                continue

        coords = list(map(float, parts[1:]))

        points = []
        for i in range(0, len(coords), 2):
            x = coords[i] * img_w
            y = coords[i + 1] * img_h
            points.append((x, y))      # <-- this was missing

            if len(points) < 3:
                continue

    rail.append(Polygon(points))
    return rail 


def compute_ioa(detections, rail, slice = 0.15, keep_classes = [0]):
    """detections: dict of {track_id: [x1, y1, x2, y2]}"""
    results = {}
    for track_id, det in detections.items(): # <-- .items(), not enumerate
        cls_id = det["cls"]  
        if keep_classes is not None and cls_id not in keep_classes:
            continue 
        x1, y1, x2, y2 = det["bbox"]

        h = y2 - y1
        y_top = y2 - (h * slice)
        det_poly = box(x1, y_top, x2, y2)

        intersection = det_poly.intersection(rail).area
        det_area = det_poly.area
        ioa = intersection / det_area if det_area > 0 else 0.0

        results[track_id] = {
            "bbox": det["bbox"],
            "ioa": round(ioa, 4),
            "cls": cls_id
        }
    return results


def draw_zone(frame, rail, ioa_results, threshold=0.3):
    overlay = frame.copy()
    for r in rail: 
        pts = np.array(r.exterior.coords, dtype=np.int32)
        cv2.fillPoly(overlay, [pts], (0, 0, 255))
    cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)   # <-- spelling + gamma
    for r in rail:
        pts = np.array(r.exterior.coords, dtype=np.int32)
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)  

    for track_id, data in ioa_results.items():
        x1, y1, x2, y2 = map(int, data["bbox"])
        ioa = data["ioa"]

        if ioa >= threshold:
            color = (0, 0, 255)
        elif ioa > 0:
            color = (0, 165, 255)
        else:
            color = (0, 255, 0)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"ID {track_id} IoA {ioa:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
        cv2.putText(frame, label, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return frame

def run_pipeline(video_in=VIDEO_IN, label_path=ZONE_LABEL):
    model = YOLO("yolo11n.pt")
    cap = cv2.VideoCapture(str(video_in))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_in}")

    img_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    img_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    zone = danger_zone(label_path, img_w, img_h)
    zone_union = union_all(zone)

    track_history = {}
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(frame, persist=True, tracker="deepocsort.yaml")

        if results[0].boxes.id is not None:
            track_ids = results[0].boxes.id.int().tolist()
            bboxes = results[0].boxes.xyxy.tolist()
            cls_ids = results[0].boxes.cls.int().tolist()

            detections = {tid: {"bbox": b, "cls": c}
                          for tid, b, c in zip(track_ids, bboxes, cls_ids)}

            ioa_results = compute_ioa(detections, zone_union)

            for track_id, data in ioa_results.items():
                data["frame"] = frame_idx          # <-- the key addition
                track_history.setdefault(track_id, []).append(data)

        frame_idx += 1

    cap.release()
    return track_history