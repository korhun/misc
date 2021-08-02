import os

import image_helper
import file_helper
import cv2
import contextlib

read_dir = "C:/_koray/train_datasets/aerial_vehicle/5_class/0/"
write_dir = "C:/_koray/train_datasets/aerial_vehicle/5_class/koray/"

'''
0 car
1 truck
2 bus
3 van
4 bike

OK
0 car
1 lorry
2 tractor
3 caravan
4 bike
5 bus
6 van
7 caterpillar
8 truck
9 boat
10 airplane
'''
# class_ids = []
class_ids_koray = {
    0: 0,  # car
    1: 8,  # truck
    2: 5,  # bus
    3: 6,  # van
    4: 4   # bike
}

for fn0 in file_helper.enumerate_files(read_dir, wildcard_pattern="*.txt"):
    lines = []
    for line in file_helper.read_lines(fn0):
        line = line.replace("\t", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ")
        arr = line.split(" ")
        if len(arr) > 0:
            arr[0] = class_ids_koray[int(arr[0])]
            line = ' '.join(str(e) for e in arr)
            lines.append(line)

    fn_write = file_helper.path_join(write_dir, os.path.basename(fn0))
    with contextlib.suppress(FileNotFoundError):
        os.remove(fn_write)
    file_helper.write_lines(fn_write, lines)

    # break
# class_ids.sort()
# print(class_ids)
print("finished")
