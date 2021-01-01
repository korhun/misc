import os

import image_helper
import file_helper
import cv2
import contextlib

fn_ann = "C:/_koray/train_datasets/aerial_vehicle/oid_v6/annotation1024.txt"
read_dir = "C:/_koray/train_datasets/aerial_vehicle/oid_v6/Vehicules1024/"
write_dir = "C:/_koray/train_datasets/aerial_vehicle/oid_v6/Vehicules1024_koray/"

'''
[1, 2, 4, 5, 7, 8, 9, 10, 11, 23, 31]
1 car
2 truck
4 tractor
5 caravan
7 bus
9 van
10 caterpillar
11 van
23 boat
31 airplane
'''
# class_ids = []
class_ids_koray = {
    "001": 0,  # car
    "002": 1,  # lorry
    "004": 2,  # tractor
    "005": 3,  # caravan
    "007": 4,  # motorbike
    "008": 5,  # bus
    "009": 6,  # van
    "010": 7,  # caterpillar
    "011": 8,  # truck
    "023": 9,  # boat
    "031": 10  # airplane
}

for line in file_helper.read_lines(fn_ann):
    line = line.replace("\t", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ")
    arr = line.split(" ")
    if len(arr) > 0:
        fn_png = "{}{}_co.png".format(read_dir, arr[0])
        fn_jpg = "{}{}.jpg".format(write_dir, arr[0])
        fn_txt = "{}{}.txt".format(write_dir, arr[0])

        # with contextlib.suppress(FileNotFoundError):
        #     os.remove(fn_txt)

        for i in range(len(arr)):
            if i != 12:
                arr[i] = float(arr[i])

        # class_id = class_ids_koray[int(arr[12])]
        # class_id = int(arr[12])
        # if class_id not in [13]:
        #     continue
        # class_id = int(arr[12])
        # if class_id not in class_ids:
        #     class_ids.append(class_id)

        class_id = class_ids_koray[arr[12]]

        mat = cv2.imread(fn_png)
        h, w = image_helper.image_h_w(mat)
        cv2.imwrite(fn_jpg, mat)

        x1 = min(arr[4], arr[5], arr[6], arr[7])
        y1 = min(arr[8], arr[9], arr[10], arr[11])

        x2 = max(arr[4], arr[5], arr[6], arr[7])
        y2 = max(arr[8], arr[9], arr[10], arr[11])

        cx = (arr[4] + arr[5] + arr[6] + arr[7]) / 4
        cy = (arr[8] + arr[9] + arr[10] + arr[11]) / 4

        cx_ = cx / h
        cy_ = cy / w
        w_ = (x2 - x1) / h
        h_ = (y2 - y1) / w
        yolo_txt = "{} {} {} {} {}".format(class_id, cx_, cy_, w_, h_)
        file_helper.append_line(fn_txt, yolo_txt)

    # break
# class_ids.sort()
# print(class_ids)
print("finished")
