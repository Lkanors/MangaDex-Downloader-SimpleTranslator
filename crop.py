import tempfile
from pathlib import Path
from PIL import Image
import os
def crop_to_temp(image, coords, suffix=".png"):
    img = Image.open(image) if isinstance(image, (str, Path)) else image
    xs, ys = zip(*coords)
    cropped = img.crop((min(xs), min(ys), max(xs), max(ys)))
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    cropped.save(temp.name)
    temp.close()
    return temp.name


def cleanup_temp(path):
    Path(path).unlink(missing_ok=True)
    # os.remove(path)