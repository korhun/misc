import os

import cv2
import image_helper
import file_helper
import contextlib


def _oidv6_to_yolo(class_id, class_name, images_dir, labels_dir, yolo_dir):
    for label_fn in file_helper.enumerate_files(labels_dir, recursive=False):
        try:
            print(label_fn, end="\r")
            name = os.path.basename(label_fn)
            image_fn = file_helper.path_join(images_dir, name.replace(".txt", ".jpg"))
            if os.path.isfile(image_fn):
                write_image_fn = file_helper.path_join(yolo_dir, name.replace(".txt", ".jpg"))
                write_fn_txt = file_helper.path_join(yolo_dir, name)
                if os.path.isfile(write_image_fn) and os.path.isfile(write_fn_txt):
                    continue

                mat = cv2.imread(image_fn)
                h, w = image_helper.image_h_w(mat)
                lines = []
                for line in file_helper.read_lines(label_fn):
                    line = line.replace("\t", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ")
                    arr0 = line.split(" ")
                    arr = [class_id]
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

                if len(lines) > 0:
                    # write_image_fn = file_helper.path_join(yolo_dir, name.replace(".txt", ".jpg"))
                    # cv2.imwrite(write_image_fn, mat)
                    file_helper.copy_file(image_fn, write_image_fn)

                    with contextlib.suppress(FileNotFoundError):
                        os.remove(write_fn_txt)
                    file_helper.write_lines(write_fn_txt, lines)
                else:
                    print("nok: " + label_fn)
            else:
                print("no image: " + image_fn)
        except Exception as e:
            print('Error - file:{} msg:{}'.format(label_fn, str(e)))

    print("finished: " + class_name)


def oidv6_to_yolo(yolo_dir, classes, images_dir_pattern, labels_dir_pattern):
    if not os.path.isdir(yolo_dir):
        file_helper.create_dir(yolo_dir)
    classes_txt_fn = file_helper.path_join(yolo_dir, "classes.txt")
    for class_name in classes:
        file_helper.append_line(classes_txt_fn, class_name)
    for class_id, class_name in enumerate(classes):
        images_dir = images_dir_pattern.format(class_name)
        labels_dir = labels_dir_pattern.format(class_name)

        _oidv6_to_yolo(class_id, class_name, images_dir, labels_dir, yolo_dir)


def run():
    # https://github.com/DmitryRyumin/OIDv6/blob/master/oidv6/classes.txt
    # oidv6 downloader en --dataset C:/_koray/train_datasets/oidv6/_download --type_data all --classes Motorcycle Truck "Seat belt" Car Bicycle Bus Van Person  --yes
    # oidv6 downloader en --dataset C:/_koray/train_datasets/oidv6/_download --type_data all --classes Vehicle Helmet "Bicycle helmet" "Football helmet" Taxi Telephone "Mobile phone" "Corded phone" Train "Human face" "Human arm" "Human body" "Human head" Man Woman Girl Boy Wheel --yes

    # classes = [
    #     (0, "seat_belt")
    #     (0, "person")
    # ]
    # output_dir = "C:/_koray/train_datasets/oidv6_yolo/seat_belt/"  C:/_koray/train_datasets/oidv6_yolo/vehicles

    classes = [
        "vehicle_registration_plate",
        "bicycle",
        "bus",
        "car",
        "motorcycle",
        "truck",
        "van"
    ]
    output_dir = "C:/_koray/train_datasets/oidv6_yolo/vehicles/"

    images_dir_pattern = "C:/_koray/train_datasets/oidv6/{}/"
    labels_dir_pattern = "C:/_koray/train_datasets/oidv6/{}/labels/"

    oidv6_to_yolo(output_dir, classes, images_dir_pattern, labels_dir_pattern)


run()
