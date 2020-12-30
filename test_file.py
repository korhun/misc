import math
import os

import image_helper
import file_helper
from shutil import copyfile
import cv2
import contextlib

read_dir = "C:/_koray/train_datasets/vehicle_registration_plate0/"
write_dir = "C:/_koray/train_datasets/vehicle_registration_plate/"

for fn_jpg in file_helper.enumerate_files(read_dir, wildcard_pattern="*.jpg"):
    h, w = image_helper.image_h_w(cv2.imread(fn_jpg))
    lines = []

    fn0 = fn_jpg.replace(".jpg", ".txt")
    for line in file_helper.read_lines(fn0):
        line = line.replace("\t", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ")
        arr0 = line.split(" ")
        arr = [0]
        x1 = float(arr0[1])
        y1 = float(arr0[2])
        x2 = float(arr0[3])
        y2 = float(arr0[4])
        arr.append((x1 + x2) * 0.5 / w)
        arr.append((y1 + y2) * 0.5 / h)
        arr.append((x2 - x1) / w)
        arr.append((y2 - y1) / h)
        line = ' '.join(str(e) for e in arr)
        lines.append(line)

        write_fn_txt = file_helper.path_join(write_dir, os.path.basename(fn_jpg)).replace(".jpg", ".txt")
        with contextlib.suppress(FileNotFoundError):
            os.remove(write_fn_txt)
        file_helper.write_lines(write_fn_txt, lines)

        write_fn_jpg = file_helper.path_join(write_dir, os.path.basename(fn_jpg))
        with contextlib.suppress(FileNotFoundError):
            os.remove(write_fn_jpg)
        copyfile(fn_jpg, write_fn_jpg)

print("finished")
