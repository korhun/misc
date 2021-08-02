import math
import os

import image_helper
import file_helper
from shutil import copyfile
import cv2
import contextlib

read_dir = "C:/_koray/train_datasets/aerial_vehicle/mun/0/"
write_dir = "C:/_koray/train_datasets/aerial_vehicle/mun/koray/"

classes = [
    "car",
    "lorry",
    "tractor",
    "caravan",
    "bike",
    "bus",
    "van",
    "caterpillar",
    "truck",
    "boat",
    "airplane"
]

suffix_class_id = [
    ("_bus.samp", classes.index("bus")),
    ("_pkw.samp", classes.index("car")),
    ("_truck.samp", classes.index("truck")),

    ("_truck_trail.samp", classes.index("lorry")),
    ("_van_trailer.samp", classes.index("van")),

    ("_cam.samp", classes.index("airplane")),
    ("_pkw_trail.samp", classes.index("boat"))
]


def rotate(cx, cy, w, h, angle_in_degrees):
    alpha = math.radians(angle_in_degrees)
    w1 = w * math.cos(alpha) - h * math.sin(alpha)
    h1 = w * math.sin(alpha) + h * math.cos(alpha)
    return w1, h1


for fn_jpg in file_helper.enumerate_files(read_dir, wildcard_pattern="*.jpg"):
    h0, w0 = image_helper.image_h_w(cv2.imread(fn_jpg))
    lines = []

    for suffix, class_id in suffix_class_id:
        fn0 = fn_jpg.replace(".JPG", suffix)
        if os.path.isfile(fn0):
            for line in file_helper.read_lines(fn0):
                line = line.replace("\t", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ")
                arr0 = line.split(" ")
                arr = []
                if len(arr0) > 0:
                    first_char = arr0[0][0]
                    if first_char not in ["#", "@"]:
                        arr.append(class_id)

                        angle_in_degrees = float(arr0[6])

                        # mult_h = math.sin(math.radians(angle))
                        # if abs(mult_h) < 0.001:
                        #     mult_h = 1.0
                        # else:
                        #     mult_h = 1.0 / mult_h
                        #
                        # mult_w = math.cos(math.radians(angle))
                        # if abs(mult_w) < 0.001:
                        #     mult_w = 1.0
                        # else:
                        #     mult_w = 1.0 / mult_w

                        cx = float(arr0[2])
                        cy = float(arr0[3])
                        h = float(arr0[4])
                        w = float(arr0[5])

                        if w > 0 and h > 0:
                            w *= 1.5
                            h *= 1.5

                            # w, h = rotate(cx, cy, w, h, angle_in_degrees)
                            rad = math.radians(angle_in_degrees)

                            s = abs(math.sin(rad))
                            c = abs(math.cos(rad))

                            H = w * s + h * c
                            W = w * c + h * s

                            div = (c * c - s * s)
                            if abs(div) < 0.001: div = 0.001
                            w1 = w / 2 + (H * c - W * s) / div
                            h1 = h / 2 - (H * s - W * c) / div

                            arr.append(cx / w0)
                            arr.append(cy / h0)
                            arr.append(w1 / w0)
                            arr.append(h1 / h0)

                            line = ' '.join(str(e) for e in arr)
                            lines.append(line)

    write_fn_txt = file_helper.path_join(write_dir, os.path.basename(fn_jpg)).replace(".JPG", ".txt")
    with contextlib.suppress(FileNotFoundError):
        os.remove(write_fn_txt)
    file_helper.write_lines(write_fn_txt, lines)

    write_fn_jpg = file_helper.path_join(write_dir, os.path.basename(fn_jpg))
    with contextlib.suppress(FileNotFoundError):
        os.remove(write_fn_jpg)
    copyfile(fn_jpg, write_fn_jpg)

print("finished")
