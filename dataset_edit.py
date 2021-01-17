import contextlib
import os

import cv2

import file_helper
import image_helper
import string_helper


def save_images_with_cv(source_dir_name, target_dir_name, max_dim =None):
    if not os.path.isdir(target_dir_name):
        file_helper.create_dir(target_dir_name)
    i = 0
    for fn in file_helper.enumerate_files(source_dir_name):
        try:
            i += 1
            print("{} - {}".format(i, fn), end="\r")
            dir_name, name, extension = file_helper.get_file_name_extension(fn)
            if string_helper.equals_case_insensitive(extension, ".txt"):
                new_fn = file_helper.path_join(target_dir_name, name + extension)
                file_helper.copy_file(fn, new_fn)
            else:
                mat = cv2.imread(fn)
                if max_dim is not None:
                    mat = image_helper.resize_if_larger(mat, max_dim)
                new_fn = file_helper.path_join(target_dir_name, name + ".jpg")
                cv2.imwrite(new_fn, mat)
        except Exception as e:
            print("error - save_images_with_cv: {}".format(fn))

    print("save_images_with_cv finished")


def class_info_yolo(labels_dir, classes_txt_fn):
    class_names = file_helper.read_lines(classes_txt_fn)
    class_counts = {}
    for name in class_names:
        class_counts[name] = 0
    for fn in file_helper.enumerate_files(labels_dir, wildcard_pattern="*.txt"):
        try:
            for line in file_helper.read_lines(fn):
                class_id = int(line.split(" ")[0])
                name = class_names[class_id]
                class_counts[name] += 1
            print(class_counts, end="                                  \r")
        except Exception as e:
            print("error - class_info_yolo: {}".format(fn))

    print(class_counts)


def class_info_names(classes_txt_fn):
    class_names = file_helper.read_lines(classes_txt_fn)
    print(class_names)
    return class_names


def mirror_images(source_dir_name, target_dir_name):
    if not os.path.isdir(target_dir_name):
        file_helper.create_dir(target_dir_name)
    i = 0
    for fn in file_helper.enumerate_files(source_dir_name):
        try:
            i += 1
            print("{} - {}".format(i, fn), end="\r")
            dir_name, name, extension = file_helper.get_file_name_extension(fn)
            if string_helper.equals_case_insensitive(extension, ".txt"):
                if name == "classes" and extension == ".txt":
                    new_fn = file_helper.path_join(target_dir_name, name + extension)
                    if not os.path.isfile(new_fn):
                        file_helper.copy_file(fn, new_fn)
                    continue

                new_fn = file_helper.path_join(target_dir_name, name + "_mirror" + extension)
                if os.path.isfile(new_fn):
                    raise Exception()
                for line in file_helper.read_lines(fn):
                    lst = line.split(" ")
                    lst[1] = str(1 - float(lst[1]))
                    new_line = string_helper.join(lst, " ")
                    file_helper.append_line(new_fn, new_line)
            else:
                mat = cv2.imread(fn)
                new_fn = file_helper.path_join(target_dir_name, name + "_mirror" + ".jpg")
                mat = cv2.flip(mat, 1)
                cv2.imwrite(new_fn, mat)
        except Exception as e:
            print("error - mirror_images: {}".format(fn))

    print("mirror_images finished")


def mirror_images_of_classes(input_images_dir, input_labels_dir, output_dir, class_ids, copy_other_classes=True):
    out_images_dir = file_helper.path_join(output_dir, "images")
    out_labels_dir = file_helper.path_join(output_dir, "labels")
    for dir_name in [out_images_dir, out_labels_dir]:
        if not os.path.isdir(dir_name):
            file_helper.create_dir(dir_name)

    i = 0
    for fn_label in file_helper.enumerate_files(input_labels_dir, recursive=False, wildcard_pattern="*.txt"):
        try:
            i += 1
            print("{} - {}".format(i, fn_label), end="                        \r")
            dir_name, name, extension = file_helper.get_file_name_extension(fn_label)
            mirror = False
            for line in file_helper.read_lines(fn_label):
                class_id = int(line.split(" ")[0])
                if class_id in class_ids:
                    mirror = True
                    break

            if mirror:
                fn_image = file_helper.path_join(input_images_dir, name + ".jpg")
                if not os.path.isfile(fn_image):
                    print("No image: {}".format(fn_image))
                else:
                    new_image_fn = file_helper.path_join(out_images_dir, name + "_mirror" + ".jpg")
                    cv2.imwrite(new_image_fn, image_helper.mirror(cv2.imread(fn_image)))

                    new_label_fn1 = file_helper.path_join(out_labels_dir, name + "_mirror" + ".txt")
                    new_label_fn2 = file_helper.path_join(out_images_dir, name + "_mirror" + ".txt")
                    new_label_file_names = [new_label_fn1, new_label_fn2]
                    for new_label_fn in new_label_file_names:
                        if os.path.isfile(new_label_fn):
                            raise Exception()
                        for line in file_helper.read_lines(fn_label):
                            lst = line.split(" ")
                            lst[1] = str(1 - float(lst[1]))
                            new_line = string_helper.join(lst, " ")
                            file_helper.append_line(new_label_fn, new_line)
            if mirror or copy_other_classes:
                fn_image = file_helper.path_join(input_images_dir, name + ".jpg")
                if not os.path.isfile(fn_image):
                    print("No image: {}".format(fn_image))
                else:
                    new_image_fn = file_helper.path_join(out_images_dir, name + ".jpg")
                    cv2.imwrite(new_image_fn, cv2.imread(fn_image))

                    new_label_fn1 = file_helper.path_join(out_labels_dir, name + ".txt")
                    new_label_fn2 = file_helper.path_join(out_images_dir, name + ".txt")
                    new_label_file_names = [new_label_fn1, new_label_fn2]
                    for new_label_fn in new_label_file_names:
                        if os.path.isfile(new_label_fn):
                            raise Exception()
                        file_helper.copy_file(fn_label, new_label_fn)

        except Exception as e:
            print("error - mirror_images_of_classes: {}".format(fn_label))

    print("mirror_images_of_classes {} finished".format(class_ids))


def change_class_id(labels_dir, class_id_from, class_id_to):
    if not os.path.isdir(labels_dir):
        raise Exception("bad dir: " + labels_dir)
    i = 0
    for fn in file_helper.enumerate_files(labels_dir):
        try:
            i += 1
            print("{} - {}".format(i, fn), end="\r")
            dir_name, name, extension = file_helper.get_file_name_extension(fn)
            if string_helper.equals_case_insensitive(extension, ".txt"):
                if name == "classes" and extension == ".txt":
                    continue

                lines = []
                changed = False
                for line in file_helper.read_lines(fn):
                    lst = line.split(" ")
                    if int(lst[0]) == class_id_from:
                        changed = True
                        lst[0] = str(class_id_to)
                    new_line = string_helper.join(lst, " ")
                    lines.append(new_line)
                if changed:
                    file_helper.delete_file(fn)
                    file_helper.write_lines(fn, lines)
        except Exception as e:
            print("error - mirror_images: {}".format(fn))

    print("change_class_id finished")


def check_single_files(images_dir):
    bad_dir = images_dir + "/bad"

    counts = {}
    fnames = {}
    names = {}
    for file_full_name in file_helper.enumerate_files(images_dir):
        dir_name, name, extension = file_helper.get_file_name_extension(file_full_name)
        if name not in counts:
            counts[name] = 1
            fnames[name] = file_full_name
            names[name] = name + extension
        else:
            counts[name] += 1
    fn = None
    for name, count in counts.items():
        if count == 1:
            try:
                fn = fnames[name]
                if name == ".DS_Store":
                    os.remove(fn)
                else:
                    name_with_ext = names[name]
                    if name_with_ext == "classes.txt":
                        continue
                    if not os.path.isdir(bad_dir):
                        file_helper.create_dir(bad_dir)
                    new_fn = file_helper.path_join(bad_dir, name_with_ext)
                    os.rename(fn, new_fn)
                    print("check_single_files - bad file: " + fn)
            except Exception as e:
                print(f'ERROR:{fn} - {str(e)} ')
        elif count != 2:
            print(name)
        else:
            name_with_ext = names[name]
            name, ext = os.path.splitext(name_with_ext)
            if ext != ".txt":
                txt_fn = os.path.join(images_dir, name + ".txt")
                if not os.path.isfile(txt_fn):
                    if not os.path.isdir(bad_dir):
                        file_helper.create_dir(bad_dir)
                    new_fn = os.path.join(bad_dir, name_with_ext)
                    fn = fnames[name]
                    os.rename(fn, new_fn)
                    print("check_single_files - bad file: " + fn)

    print("check_single_files finished")


def generate_train_txt(output_dir, model_name, class_names, images_dir, ratio_train=0.7, ratio_val=0.2, ratio_test=0.1):
    yaml = file_helper.path_join(output_dir, model_name + ".yaml")
    if os.path.isfile(yaml):
        os.remove(yaml)
    with open(yaml, "a") as file:
        train_fn = file_helper.path_join(output_dir, model_name + "_train.txt")
        file.write(f"train: {train_fn}\n")
        val_fn = file_helper.path_join(output_dir, model_name + "_val.txt")
        file.write(f"val: {val_fn}\n")
        if ratio_test > 0:
            test_fn = file_helper.path_join(output_dir, model_name + "_test.txt")
            file.write(f"test: {test_fn}\n")
        file.write(f"nc: {str(len(class_names))}" + "\n")
        file.write("names: " + str(class_names))

    all_data = file_helper.path_join(output_dir, model_name + "_all_data.txt")
    train = file_helper.path_join(output_dir, model_name + "_train.txt")
    val = file_helper.path_join(output_dir, model_name + "_val.txt")
    test = file_helper.path_join(output_dir, model_name, "_test.txt")
    if os.path.isfile(all_data):
        os.remove(all_data)
    if os.path.isfile(train):
        os.remove(train)
    if os.path.isfile(val):
        os.remove(val)
    if os.path.isfile(test):
        os.remove(test)

    labels_dir = os.path.join(os.path.abspath(os.path.join(images_dir, os.pardir)), "labels")
    if not os.path.isdir(labels_dir):
        file_helper.create_dir(labels_dir)
    for fn in file_helper.enumerate_files(labels_dir, recursive=True):
        if str.endswith(fn, ".txt"):
            os.remove(fn)
    with open(all_data, "a") as file:
        for file_full_name in file_helper.enumerate_files(images_dir):
            dir_name, name, extension = file_helper.get_file_name_extension(file_full_name)
            if extension != ".txt":
                file.write(file_full_name + "\n")
            else:
                new_file_name = file_helper.path_join(labels_dir, name + extension)
                file_helper.copy_file(file_full_name, new_file_name)

    with open(all_data) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    from random import shuffle
    shuffle(content)

    train_count = int(len(content) * ratio_train)
    val_count = train_count + int(len(content) * ratio_val)
    # test %10
    if ratio_test > 0:
        i = 0
        for line in content:
            i += 1
            if i < train_count:
                fn = train
            elif i < val_count:
                fn = val
            else:
                fn = test
            with open(fn, "a") as file:
                file.write(line + "\n")
            # print(line)
    else:
        i = 0
        for line in content:
            i += 1
            if i < train_count:
                fn = train
            else:
                fn = val
            with open(fn, "a") as file:
                file.write(line + "\n")
            # print(line)

    print("generate_train_txt finished")


def check_class_ids(train_files_dir, class_names, model_name):
    max_class_id = len(class_names)
    # all_data = f"{train_files_dir}/data/{model_name}_all_data.txt"
    all_data = file_helper.path_join(train_files_dir, model_name + "_all_data.txt")
    with open(all_data) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    bad_files = []
    for fn1 in content:
        name, ext = os.path.splitext(fn1)
        fn2 = name + ".txt"
        with open(fn2) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            for c in content:
                id_ = int(c.split(" ")[0])
                if id_ >= max_class_id:
                    bad_files.append(fn2)
            # print(str(content) + " " + fn2)

    for bad in bad_files:
        print("bad: " + bad)

    print("check_files finished")


def check_labels(labels_dir):
    if not os.path.isdir(labels_dir):
        raise Exception("bad dir: " + labels_dir)
    i = 0
    for fn in file_helper.enumerate_files(labels_dir):
        try:
            i += 1
            print("{} - {}".format(i, fn), end="\r")
            dir_name, name, extension = file_helper.get_file_name_extension(fn)
            if string_helper.equals_case_insensitive(extension, ".txt"):
                if name == "classes" and extension == ".txt":
                    continue

                lines = []
                changed = False
                for line in file_helper.read_lines(fn):
                    lst = line.split(" ")
                    for j in range(1, len(lst)):
                        val = float(lst[j])
                        if val < 0:
                            changed = True
                            lst[j] = "0"
                        elif val > 1:
                            changed = True
                            lst[j] = "1"
                    new_line = string_helper.join(lst, " ")
                    lines.append(new_line)
                if changed:
                    file_helper.delete_file(fn)
                    file_helper.write_lines(fn, lines)
        except Exception as e:
            print("error - mirror_images: {}".format(fn))

    print("change_class_id finished")


def oidv6_to_yolo(images_and_labels_dir, class_id):
    for label_fn in file_helper.enumerate_files(images_and_labels_dir, recursive=False, wildcard_pattern="*.txt"):
        try:
            print(label_fn, end="\r")
            name = os.path.basename(label_fn)
            image_fn = file_helper.path_join(images_and_labels_dir, name.replace(".txt", ".jpg"))
            if os.path.isfile(image_fn):
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

                with contextlib.suppress(FileNotFoundError):
                    os.remove(label_fn)
                file_helper.write_lines(label_fn, lines)
            else:
                print("no image: " + image_fn)
        except Exception as e:
            print('Error - file:{} msg:{}'.format(label_fn, str(e)))


def merge_single_classes(input_dirs, merge_dir):
    i = 0
    for input_dir in input_dirs:
        for fn in file_helper.enumerate_files(input_dir):
            try:
                i += 1
                print("{} - {}".format(i, fn), end="\r")
                dir_name, name, extension = file_helper.get_file_name_extension(fn)
                if extension != ".txt":
                    fn_input_txt = file_helper.path_join(input_dir, name + ".txt")
                    if not os.path.isfile(fn_input_txt):
                        raise Exception("no label file!")
                    fn_output_txt = file_helper.path_join(merge_dir, name + ".txt")

                    fn_input_img = fn
                    fn_output_img = file_helper.path_join(merge_dir, name + ".jpg")
                    if not os.path.isfile(fn_output_img):
                        mat = cv2.imread(fn_input_img)
                        cv2.imwrite(fn_output_img, mat)

                    if not os.path.isfile(fn_output_txt):
                        file_helper.copy_file(fn_input_txt, fn_output_txt)
                    else:
                        file_helper.append_lines(fn_output_txt, file_helper.read_lines(fn_input_txt))
                        print('Merged: {}'.format(fn_output_txt), end="\r")
            except Exception as e:
                print('Error - merge_single_classes - file: {} msg: {}'.format(fn, str(e)))


def delete_classes(images_dir, classes_old, classes_new):
    class_id_map = {}
    for old_name in classes_old:
        old_id = str(classes_old.index(old_name))
        if old_name in classes_new:
            class_id_map[old_id] = str(classes_new.index(old_name))
        else:
            class_id_map[old_id] = None

    i = 0
    for fn in file_helper.enumerate_files(images_dir, wildcard_pattern="*.txt"):
        try:
            i += 1
            lines = []
            changed = False
            for line in file_helper.read_lines(fn):
                items = line.split(" ")
                old_id = items[0]
                new_id = class_id_map[old_id]
                if new_id is not None:
                    if new_id != old_id:
                        changed = True
                        items[0] = new_id
                    lines.append(string_helper.join(items, " "))
                else:
                    changed = True
            if changed:
                file_helper.delete_file(fn)
                if len(lines) > 0:
                    # print("changed - {}".format(fn))
                    file_helper.write_lines(fn, lines)
                    print("{} - {} EDITED".format(i, fn), end="\r")
                else:
                    print("{} - {} DELETED".format(i, fn), end="\r")
            else:
                print("{} - {}".format(i, fn), end="\r")
        except Exception as e:
            print('Error - merge_single_classes - file: {} msg: {}'.format(fn, str(e)))
    check_single_files(images_dir)


# def run_vehicles_lp_416():
#     dir0 = "C:/_koray/train_datasets/vehicles_lp/images"
#     dir416 = "C:/_koray/train_datasets/vehicles_lp_416/images"
#     save_images_with_cv(dir0, dir416, 416)
#
#     train_files_dir = "C:/_koray/git/yolov5/data"
#     model_name = "vehicles_lp_416"
#     images_dir = dir416
#     class_names = [
#         "vehicle_registration_plate",
#         "bicycle",
#         "bus",
#         "car",
#         "motorcycle",
#         "truck",
#         "van"
#     ]
#
#     generate_train_txt(train_files_dir, model_name, class_names, images_dir, ratio_train=0.7, ratio_val=0.3, ratio_test=0)
#     check_class_ids(train_files_dir, class_names, model_name)
#
# run_vehicles_lp_416()

#
# def run_ls_single():
#     dir0 = "C:/_koray/train_datasets/vehicle_registration_plate/lp_single_large/images"
#     dir416 = "C:/_koray/train_datasets/vehicle_registration_plate/lp_single_416/images"
#     # save_images_with_cv(dir0, dir416, 416)
#
#
#     train_files_dir = "C:/_koray/git/yolov5/data"
#
#     model_name = "lp_single_416"
#     images_dir = dir416
#     class_names = ["plaka"]
#
#     generate_train_txt(train_files_dir, model_name, class_names, images_dir, ratio_train=0.7, ratio_val=0.3, ratio_test=0)
#     check_class_ids(train_files_dir, class_names, model_name)
#
# run_ls_single()

#
# def run_vehicles():
#     images_dir = "C:/_koray/train_datasets/vehicles/images"
#     model_name = "vehicles"
#
#     # classes_old = [
#     #     "vehicle_registration_plate",
#     #     "bicycle",
#     #     "bus",
#     #     "car",
#     #     "motorcycle",
#     #     "truck",
#     #     "van"
#     # ]
#     # classes_new = [
#     #     "bicycle",
#     #     "bus",
#     #     "car",
#     #     "motorcycle",
#     #     "truck",
#     #     "van"
#     # ]
#     # delete_classes(images_dir, classes_old, classes_new)
#
#     class_names = [
#         "bicycle",
#         "bus",
#         "car",
#         "motorcycle",
#         "truck",
#         "van"
#     ]
#     train_files_dir = "C:/_koray/git/yolov5/data"
#
#     generate_train_txt(train_files_dir, model_name, class_names, images_dir, ratio_train=0.7, ratio_val=0.3, ratio_test=0)
#     check_class_ids(train_files_dir, class_names, model_name)
#
#
# run_vehicles()

# def run_e_scooter():
#     train_files_dir = "C:/_koray/git/yolov5/data"
#
#     model_name = "e_scooter"
#     images_dir0 = "C:/_koray/train_datasets/e_scooter/images0"
#     images_dir = "C:/_koray/train_datasets/e_scooter/images"
#     class_names = ["electric scooter"]
#
#     # save_images_with_cv(images_dir0, images_dir)
#     # mirror_images(images_dir, images_dir)
#     # check_single_files(images_dir)
#
#     ## change_class_id(images_dir, 1, 0)
#
#     generate_train_txt(train_files_dir, model_name, class_names, images_dir, ratio_train=0.7, ratio_val=0.3, ratio_test=0)
#     check_class_ids(train_files_dir, class_names, model_name)
#
#     # yolov4 -> C:\_koray\git\darknet\build\darknet\x64
#     pass

# run_e_scooter()

# def run_e_scooter():
#     train_files_dir = "C:/_koray/git/yolov5/data"
#
#     model_name = "e_scooter"
#     images_dir0 = "C:/_koray/train_datasets/e_scooter/images0"
#     images_dir = "C:/_koray/train_datasets/e_scooter/images"
#     class_names = ["electric scooter"]
#
#     # save_images_with_cv(images_dir0, images_dir)
#     # mirror_images(images_dir, images_dir)
#     # check_single_files(images_dir)
#
#     ## change_class_id(images_dir, 1, 0)
#
#     generate_train_txt(train_files_dir, model_name, class_names, images_dir, ratio_train=0.7, ratio_val=0.3, ratio_test=0)
#     check_class_ids(train_files_dir, class_names, model_name)
#
#     # yolov4 -> C:\_koray\git\darknet\build\darknet\x64
#     pass
#
#
# # run_e_scooter()
#
# def run_vehicles_multi():
#     ###############
#     # images_dir = "C:/_koray/train_datasets/oidv6_yolo/vehicles_multi/images"
#     #     # labels_dir1 = "C:/_koray/train_datasets/oidv6_yolo/vehicles_multi/images"
#     #     # labels_dir2 = "C:/_koray/train_datasets/oidv6_yolo/vehicles_multi/labels"
#     #     # classes_txt_fn = "C:/_koray/train_datasets/oidv6_yolo/vehicles_multi/classes.txt"
#     #
#     #     # class_info_yolo(labels_dir1, classes_txt_fn)
#     #     # 0: {'bicycle': 41788, 'bus': 12416, 'car': 288152, 'motorcycle': 14297, 'truck': 13561, 'van': 8553, 'vehicle_registration_plate': 11682}
#     #
#     #     # class_names = class_info_names(classes_txt_fn)
#     #     # # ['bicycle', 'bus', 'car', 'motorcycle', 'truck', 'van', 'vehicle_registration_plate']
#     #     #
#     #     # mirror_to = "C:/_koray/train_datasets/oidv6_yolo/vehicles_multi_mirror"
#     # mirror_images_of_classes(images_dir, labels_dir1, mirror_to, [class_names.index("van"), class_names.index("vehicle_registration_plate")])
#
#     ###############
#     images_dir = "C:/_koray/train_datasets/oidv6_yolo/vehicles_multi_mirror/images"
#     labels_dir1 = "C:/_koray/train_datasets/oidv6_yolo/vehicles_multi_mirror/images"
#     labels_dir2 = "C:/_koray/train_datasets/oidv6_yolo/vehicles_multi_mirror/labels"
#     classes_txt_fn = "C:/_koray/train_datasets/oidv6_yolo/vehicles_multi_mirror/classes.txt"
#
#     class_info_yolo(labels_dir1, classes_txt_fn)
#     # vehicles 6 class multi + capture edilen + mirrorları burada birleştirildi
#
#
# # run_vehicles_multi()
#
#
# def run_vehicles_capture():
#     input_dir = "C:/_koray/train_datasets/vehicle_registration_plate/captured_class6"
#     output_dir = "C:/_koray/train_datasets/vehicle_registration_plate/captured_class6_mirror"
#     mirror_images(input_dir, output_dir)
#
# # run_vehicles_capture()
