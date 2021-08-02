import os
import time

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


def oidv6_to_yolo_multi(input_multi_oidv6_dir, output_yolo_dir):
    if not os.path.isdir(output_yolo_dir):
        file_helper.create_dir(output_yolo_dir)

    output_images_dir = file_helper.path_join(output_yolo_dir, "images")
    if not os.path.isdir(output_images_dir):
        file_helper.create_dir(output_images_dir)

    output_labels_dir = file_helper.path_join(output_yolo_dir, "labels")
    if not os.path.isdir(output_labels_dir):
        file_helper.create_dir(output_labels_dir)

    classes = []

    print("started.... oidv6_to_yolo_multi - {}".format(input_multi_oidv6_dir))
    i = 0
    for sub_dir in ["test", "train", "validation"]:
        images_dir = file_helper.path_join(input_multi_oidv6_dir, sub_dir)
        labels_dir = file_helper.path_join(images_dir, "labels")
        for image_fn in file_helper.enumerate_files(images_dir, recursive=False):
            try:
                dir_name, name, extension = file_helper.get_file_name_extension(image_fn)
                label_fn = file_helper.path_join(labels_dir, name + ".txt")
                if not os.path.isfile(label_fn):
                    print("!!! File has no label: {}".format(image_fn))
                else:
                    i += 1
                    print("processing {} - {}".format(str(i), image_fn), end="                                    \r")

                    key_name = name[name.rfind("_") + 1:]

                    out_image_fn = file_helper.path_join(output_yolo_dir, "images", key_name + extension)
                    out_label_fn_1 = file_helper.path_join(output_yolo_dir, "images", key_name + ".txt")
                    out_label_fn_2 = file_helper.path_join(output_yolo_dir, "labels", key_name + ".txt")

                    class_name = name[: name.rfind("_")]
                    if class_name not in classes:
                        classes.append(class_name)
                        print(class_name)

                    class_id = classes.index(class_name)

                    if os.path.isfile(out_image_fn) and os.path.isfile(out_label_fn_2):
                        exists = False
                        for line in file_helper.read_lines(out_label_fn_2):
                            line = line.replace("\t", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ")
                            if class_id == int(line.split(" ")[0]):
                                exists = True
                                break
                        if exists:
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
                        cv2.imwrite(out_image_fn, mat)
                        # file_helper.copy_file(image_fn, out_image_fn)

                        # if os.path.isfile(out_label_fn_2):
                        #     print("merged: " + out_label_fn_2)

                        for line in lines:
                            file_helper.append_line(out_label_fn_1, line)
                            file_helper.append_line(out_label_fn_2, line)
                    else:
                        print("nok: " + label_fn)
            except Exception as e:
                print('Error - file:{} msg:{}'.format(image_fn, str(e)))

    classes_txt_fn = file_helper.path_join(output_yolo_dir, "classes.txt")
    file_helper.write_lines(classes_txt_fn, classes)
    print("finished: oidv6_to_yolo_multi")


def run():
    # https://github.com/DmitryRyumin/OIDv6/blob/master/oidv6/classes.txt

    # single
    # oidv6 downloader en --dataset C:/_koray/train_datasets/oidv6/_download --type_data all --classes Motorcycle Truck "Seat belt" Car Bicycle Bus Van Person  --yes
    # oidv6 downloader en --dataset C:/_koray/train_datasets/oidv6/_download --type_data all --classes Vehicle Helmet "Bicycle helmet" "Football helmet" Taxi Telephone "Mobile phone" "Corded phone" Train "Human face" "Human arm" "Human body" "Human head" Man Woman Girl Boy Wheel --yes

    # multi
    # oidv6 downloader en --dataset C:/_koray/train_datasets/oidv6/_download --type_data all --classes Bicycle Bus Car Motorcycle Truck Van "Vehicle registration plate" --multi_classes --yes

    input_multi_oidv6_dir = "C:/_koray/train_datasets/oidv6/_download/multidata"
    output_yolo_dir = "C:/_koray/train_datasets/oidv6_yolo/vehicles_multi"

    oidv6_to_yolo_multi(input_multi_oidv6_dir, output_yolo_dir)


run()
