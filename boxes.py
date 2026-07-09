import numpy as np
from pathlib import Path
from paddleocr import PaddleOCR


class MangaOCR:
    def __init__(
        self,
        lang="japan",
        use_angle_cls=True,
        merge_distance=30,
        min_overlap_ratio=0.3,
    ):
        self.ocr = PaddleOCR(
            use_angle_cls=use_angle_cls,
            lang=lang,
            show_log=False,
            det_db_box_thresh=0.3,
            det_db_thresh=0.3,
            rec_batch_num=6,
        )
        self.merge_distance = merge_distance
        self.min_overlap_ratio = min_overlap_ratio

    def process_folder(self, folder_path: str) -> list:
        folder = Path(folder_path)
        
        if not folder.exists():
            return []
        
        if not folder.is_dir():
            return []
        
        img_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

        images = sorted([f for f in folder.rglob("*") if f.suffix.lower() in img_exts])

        if not images:

            return []
        
        results = []
        for img_path in images:
            print({img_path.relative_to(folder)})
            file_path = str(img_path.resolve())
            blocks = self.process_image(str(img_path))
            
            print(f"Blocks count: {len(blocks)}")
            
            for block in blocks:
                results.append([file_path, block["bbox"], block["text"]])

        return results

    def process_image(self, image_path: str) -> list:
        result = self.ocr.ocr(image_path, cls=True)
        if not result or not result[0]:
            return []

        lines = []
        for line in result[0]:
            box = np.array(line[0])
            text = line[1][0]
            conf = float(line[1][1])
            lines.append({"box": box, "text": text, "conf": conf})

        return self._merge_blocks(lines)

    def _merge_blocks(self, lines: list) -> list:
        n = len(lines)
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        for i in range(n):
            for j in range(i + 1, n):
                if self._should_merge(lines[i]["box"], lines[j]["box"]):
                    union(i, j)

        groups = {}
        for i in range(n):
            root = find(i)
            groups.setdefault(root, []).append(lines[i])

        merged = []
        for group in groups.values():
            all_boxes = np.vstack([g["box"] for g in group])
            x_min, y_min = all_boxes.min(axis=0)
            x_max, y_max = all_boxes.max(axis=0)
            merged_box = [
                [x_min, y_min],
                [x_max, y_min],
                [x_max, y_max],
                [x_min, y_max],
            ]

            sorted_group = sorted(group, key=lambda g: (g["box"][0][1] + g["box"][2][1]) / 2)
            text = "\n".join(g["text"] for g in sorted_group)

            merged.append({
                "bbox": merged_box,
                "text": text,
            })

        merged.sort(key=lambda b: (b["bbox"][0][1], b["bbox"][0][0]))
        return merged

    def _should_merge(self, box_a, box_b) -> bool:
        a_xmin, a_ymin = box_a.min(axis=0)
        a_xmax, a_ymax = box_a.max(axis=0)
        b_xmin, b_ymin = box_b.min(axis=0)
        b_xmax, b_ymax = box_b.max(axis=0)

        v_gap = max(0, max(a_ymin, b_ymin) - min(a_ymax, b_ymax))
        if v_gap > self.merge_distance:
            return False

        h_gap = max(0, max(a_xmin, b_xmin) - min(a_xmax, b_xmax))
        if h_gap > self.merge_distance:
            return False

        overlap_x = max(0, min(a_xmax, b_xmax) - max(a_xmin, b_xmin))
        min_width = min(a_xmax - a_xmin, b_xmax - b_xmin)
        if min_width > 0 and (overlap_x / min_width) < self.min_overlap_ratio:
            return False

        return True


def create(lang, folder_path):
    ocr = MangaOCR(lang=lang, merge_distance=25, min_overlap_ratio=0.25)
    def process():
        results = ocr.process_folder(folder_path)
        return results
    return process