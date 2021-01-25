import contextlib
import os

import cv2

import file_helper
import image_helper
import string_helper

end_txt = "                   \r"


def save_images_with_cv(source_dir_name, target_dir_name, max_dim=None):
    if not os.path.isdir(target_dir_name):
        file_helper.create_dir(target_dir_name)
    i = 0
    for fn in file_helper.enumerate_files(source_dir_name):
        try:
            i += 1
            print("{} - {}".format(i, fn), end=end_txt)
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
            print(class_counts, end=end_txt)
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
            print("{} - {}".format(i, fn), end=end_txt)
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
            print("{} - {}".format(i, fn_label), end=end_txt)
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
    change_class_id(labels_dir, [class_id_from], class_id_to)


def change_class_id_list(labels_dir, class_id_from_list, class_id_to):
    if not os.path.isdir(labels_dir):
        raise Exception("bad dir: " + labels_dir)
    i = 0
    for fn in file_helper.enumerate_files(labels_dir):
        try:
            i += 1
            print("{} - {}".format(i, fn), end=end_txt)
            dir_name, name, extension = file_helper.get_file_name_extension(fn)
            if string_helper.equals_case_insensitive(extension, ".txt"):
                if name == "classes" and extension == ".txt":
                    continue

                lines = []
                changed = False
                for line in file_helper.read_lines(fn):
                    lst = line.split(" ")
                    if int(lst[0]) in class_id_from_list:
                        changed = True
                        lst[0] = str(class_id_to)
                    new_line = string_helper.join(lst, " ")
                    lines.append(new_line)
                if changed:
                    file_helper.delete_file(fn)
                    file_helper.write_lines(fn, lines)
        except Exception as e:
            print("error - change_class_id: {}".format(fn))

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
    for fn in file_helper.enumerate_files(labels_dir, recursive=False):
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
            print("{} - {}".format(i, fn), end=end_txt)
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
            print(label_fn, end=end_txt)
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


def oidv6_to_yolo2(input_images_dir, input_labels_dir, output_labels_and_images_dir, class_id):
    i = 0
    if not os.path.isdir(output_labels_and_images_dir):
        file_helper.create_dir(output_labels_and_images_dir)
    for label_fn in file_helper.enumerate_files(input_labels_dir, recursive=False, wildcard_pattern="*.txt"):
        try:
            i += 1
            print("{} - {}".format(i, label_fn), end=end_txt)
            dir_name, name, extension = file_helper.get_file_name_extension(label_fn)
            image_fn = file_helper.path_join(input_images_dir, name + ".jpg")
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

                out_img_fn = file_helper.path_join(output_labels_and_images_dir, name + ".jpg")
                out_lbl_fn = file_helper.path_join(output_labels_and_images_dir, name + ".txt")
                if os.path.isfile(out_img_fn):
                    os.remove(out_img_fn)
                if os.path.isfile(out_lbl_fn):
                    os.remove(out_lbl_fn)

                file_helper.write_lines(out_lbl_fn, lines)
                file_helper.copy_file(image_fn, out_img_fn)
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
                print("{} - {}".format(i, fn), end=end_txt)
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
                        print('Merged: {}'.format(fn_output_txt), end=end_txt)
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
                    print("{} - {} EDITED".format(i, fn), end=end_txt)
                else:
                    print("{} - {} DELETED".format(i, fn), end=end_txt)
            else:
                print("{} - {}".format(i, fn), end=end_txt)
        except Exception as e:
            print('Error - merge_single_classes - file: {} msg: {}'.format(fn, str(e)))
    check_single_files(images_dir)


def coco_separate_classes(input_dir, output_dir):
    classes_fn = file_helper.path_join(input_dir, "_classes.txt")
    classes = []
    for line in file_helper.read_lines(classes_fn):
        classes.append(line)

    i = 0
    ann_fn = file_helper.path_join(input_dir, "_annotations.txt")
    img_fn = None
    for line in file_helper.read_lines(ann_fn):
        try:
            items = line.split(" ")
            img_fn = file_helper.path_join(input_dir, items[0])
            dir_name, name, extension = file_helper.get_file_name_extension(img_fn)
            i += 1
            print("{} - {}".format(i, img_fn), end=end_txt)

            mat = cv2.imread(img_fn)
            h, w = image_helper.image_h_w(mat)

            for j in range(1, len(items)):
                item = items[j]
                values_str = item.split(",")
                values = []
                for v in values_str:
                    values.append(int(v))
                class_name = classes[values[4]]
                write_dir = file_helper.path_join(output_dir, class_name)
                if not os.path.isdir(write_dir):
                    file_helper.create_dir(write_dir)

                write_img_fn = file_helper.path_join(write_dir, name + extension)
                if not os.path.isfile(write_img_fn):
                    file_helper.copy_file(img_fn, write_img_fn)

                x1, y1, x2, y2 = list(values[:4])
                w_ = (x2 - x1)
                h_ = (y2 - y1)
                cx = (x1 + w_ * 0.5) / w
                cy = (y1 + h_ * 0.5) / h
                line = "0 {} {} {} {}".format(cx, cy, w_ / w, h_ / h)

                write_lbl_fn = file_helper.path_join(write_dir, name + ".txt")
                if os.path.isfile(write_lbl_fn):
                    file_helper.append_line(write_lbl_fn, line)
                else:
                    file_helper.write_lines(write_lbl_fn, [line])


        except Exception as e:
            print('Error - file:{} msg:{}'.format(img_fn, str(e)))


def crop_rect(mat, cx_norm, cy_norm, w_norm, h_norm, crop_size):
    img_h0, img_w0 = image_helper.image_h_w(mat)
    cx0 = cx_norm * img_w0
    cy0 = cy_norm * img_h0
    w0 = w_norm * img_w0
    h0 = h_norm * img_h0

    r0_x1 = int(min(max(0, cx0 - w0 * 0.5), img_w0))
    r0_y1 = int(min(max(0, cy0 - h0 * 0.5), img_h0))
    # r0_x2 = int(min(max(0, cx0 + w0 * 0.5), img_w0))
    # r0_y2 = int(min(max(0, cy0 + h0 * 0.5), img_h0))

    crop_w = crop_size[0] * 0.5
    crop_h = crop_size[1] * 0.5
    crop_x1 = int(min(max(0, cx0 - crop_w), img_w0))
    crop_y1 = int(min(max(0, cy0 - crop_h), img_h0))
    crop_x2 = int(min(max(0, cx0 + crop_w), img_w0))
    crop_y2 = int(min(max(0, cy0 + crop_h), img_h0))

    img = image_helper.crop(mat, [crop_y1, crop_x1, crop_y2, crop_x2])
    img_h1, img_w1 = image_helper.image_h_w(img)

    r1_x1 = min(max(r0_x1 - crop_x1, 0), img_w1)
    r1_y1 = min(max(r0_y1 - crop_y1, 0), img_h1)
    r1_x2 = min(r1_x1 + w0, img_w1)
    r1_y2 = min(r1_y1 + h0, img_h1)

    w = (r1_x2 - r1_x1)
    h = (r1_y2 - r1_y1)
    cx = r1_x1 + w * 0.5
    cy = r1_y1 + h * 0.5

    return img, cx / img_w1, cy / img_h1, w / img_w1, h / img_h1


def find_image_file(images_dir, name_without_extension):
    fn = file_helper.path_join(images_dir, name_without_extension)
    if os.path.isfile(fn + ".jpg"):
        return fn + ".jpg"
    elif os.path.isfile(fn + ".jpeg"):
        return fn + ".jpeg"
    elif os.path.isfile(fn + ".png"):
        return fn + ".png"
    else:
        return None


def combine_classes(class_items, out_images_dir, out_labels_dir, out_classes_txt_fn, out_style="yolo"):
    # a typical class_item
    # {
    #     "class_name": "vehicle license plate",
    #     "dirs":
    #         [
    #             {
    #                 "images": "C:/_koray/train_datasets/yolo_oidv6_class0/vehicle_registration_plate",
    #                 "labels": "C:/_koray/train_datasets/yolo_oidv6_class0/vehicle_registration_plate"
    #             },
    #             {
    #                 "images": "C:/_koray/train_datasets/yolo_misc/vehicle_registration_plate/class0",
    #                 "labels": "C:/_koray/train_datasets/yolo_misc/vehicle_registration_plate/class0"
    #             }
    #         ],
    #     "resize_style": None, "if_larger" or "crop" - if "crop" -> make the image unique, don't combine, other combine with other classes
    #     "image_size": 640, - if None no resize, combine all
    #     "style": "yolo"
    # }

    class_names = []
    if out_style == "yolo":
        if not os.path.isdir(out_images_dir):
            file_helper.create_dir(out_images_dir)

        if not os.path.isdir(out_labels_dir):
            file_helper.create_dir(out_labels_dir)

        if os.path.isfile(out_classes_txt_fn):
            for class_name in file_helper.read_lines(out_classes_txt_fn):
                class_names.append(class_name)
    else:
        raise Exception("Bad out_style: " + out_style)

    for class_item in class_items:
        class_name = class_item["class_name"]
        resize_style = class_item["resize_style"]
        image_size = class_item["image_size"]
        if image_size is not None:
            image_size_txt = "{}_{}".format(image_size[0], image_size[1])
        else:
            image_size_txt = None
        input_style = class_item["input_style"]

        if class_name in class_names:
            class_index = class_names.index(class_name)
        else:
            class_index = len(class_names)
            class_names.append(class_name)
            file_helper.append_line(out_classes_txt_fn, class_name)

        i = 0
        for dir_item in class_item["dirs"]:
            images_dir = dir_item["images"]
            labels_dir = dir_item["labels"]

            if input_style == "yolo":
                for label_fn in file_helper.enumerate_files(labels_dir, wildcard_pattern="*.txt"):
                    try:
                        _dir_name, name, _extension = file_helper.get_file_name_extension(label_fn)

                        i += 1
                        print("{} - {}".format(i, label_fn), end=end_txt)

                        for line in file_helper.read_lines(label_fn):
                            line_items = line.split(" ")
                            cx_norm = float(line_items[1])
                            cy_norm = float(line_items[2])
                            w_norm = float(line_items[3])
                            h_norm = float(line_items[4])
                            line_items[0] = str(class_index)

                            out_lbl_fn = None
                            out_img_fn = None
                            mat = None
                            # for image_fn in file_helper.enumerate_files(images_dir, wildcard_pattern=name + ".*"):
                            image_fn = find_image_file(images_dir, name)
                            if image_fn is not None:
                                _dir_name, _name, extension = file_helper.get_file_name_extension(image_fn)
                                if extension != ".txt":
                                    try:
                                        mat = cv2.imread(image_fn)
                                    except Exception as e:
                                        print('Error reading image file: {} msg:{}'.format(image_fn, str(e)))
                                    if mat is not None:
                                        if resize_style is None:
                                            out_img_fn = file_helper.path_join(out_images_dir, name + ".jpg")
                                            out_lbl_fn = file_helper.path_join(out_labels_dir, name + ".txt")
                                        elif resize_style == "if_larger":
                                            out_img_fn = file_helper.path_join(out_images_dir, name + "_" + image_size_txt + ".jpg")
                                            out_lbl_fn = file_helper.path_join(out_labels_dir, name + "_" + image_size_txt + ".txt")
                                            mat = image_helper.resize_if_larger(mat, max(image_size[0], image_size[1]))
                                        elif resize_style == "crop":
                                            new_name = file_helper.get_unique_file_name()
                                            out_img_fn = file_helper.path_join(out_images_dir, name + "_crop_" + new_name + ".jpg")
                                            out_lbl_fn = file_helper.path_join(out_labels_dir, name + "_crop_" + new_name + ".txt")
                                            mat, cx, cy, w, h = crop_rect(mat, cx_norm, cy_norm, w_norm, h_norm, image_size)
                                            line_items[1] = str(cx)
                                            line_items[2] = str(cy)
                                            line_items[3] = str(w)
                                            line_items[4] = str(h)
                                        else:
                                            raise Exception("Bad resize_style: " + resize_style)
                            else:
                                raise Exception("Cannot find image file")

                            if out_lbl_fn is not None:
                                line = string_helper.join(line_items, " ")
                                if os.path.isfile(out_lbl_fn):
                                    file_helper.append_line(out_lbl_fn, line)
                                else:
                                    file_helper.write_lines(out_lbl_fn, [line])
                            if out_img_fn is not None and mat is not None:
                                if not os.path.isfile(out_img_fn):
                                    cv2.imwrite(out_img_fn, mat)
                    except Exception as e:
                        print('Error - file:{} msg:{}'.format(label_fn, str(e)))
            else:
                raise Exception("Bad input_style: " + out_style)


def run_combine_classes():
    out_style = "yolo"
    image_size = [640, 640]
    model_name = "lp_" + str(image_size[0])
    out_base_dir = "C:/_koray/train_datasets/active"

    images_dir = file_helper.path_join(out_base_dir, model_name, "images")
    labels_dir = file_helper.path_join(out_base_dir, model_name, "images")
    classes_txt_fn = file_helper.path_join(out_base_dir, "classes.txt")

    class_items = [
        {
            "class_name": "vehicle license plate",
            "dirs":
                [
                    {
                        "images": "C:/_koray/train_datasets/yolo_misc/vehicle_registration_plate/class0",
                        "labels": "C:/_koray/train_datasets/yolo_misc/vehicle_registration_plate/class0"
                    }
                ],
            "resize_style": "crop",
            "image_size": image_size,
            "input_style": "yolo"
        },
        {
            "class_name": "bicycle",
            "dirs":
                [
                    {
                        "images": "C:/_koray/train_datasets/yolo_oidv6_class0/bicycle",
                        "labels": "C:/_koray/train_datasets/yolo_oidv6_class0/bicycle"
                    },
                    {
                        "images": "C:/_koray/train_datasets/yolo_coco_class0/bicycle",
                        "labels": "C:/_koray/train_datasets/yolo_coco_class0/bicycle"
                    }
                ],
            "resize_style": "if_larger",
            "image_size": image_size,
            "input_style": "yolo"
        },
        {
            "class_name": "bus",
            "dirs":
                [
                    {
                        "images": "C:/_koray/train_datasets/yolo_oidv6_class0/bus",
                        "labels": "C:/_koray/train_datasets/yolo_oidv6_class0/bus"
                    },
                    {
                        "images": "C:/_koray/train_datasets/yolo_coco_class0/bus",
                        "labels": "C:/_koray/train_datasets/yolo_coco_class0/bus"
                    }
                ],
            "resize_style": "if_larger",
            "image_size": image_size,
            "input_style": "yolo"
        },
        {
            "class_name": "car",
            "dirs":
                [
                    {
                        "images": "C:/_koray/train_datasets/yolo_oidv6_class0/car",
                        "labels": "C:/_koray/train_datasets/yolo_oidv6_class0/car"
                    },
                    {
                        "images": "C:/_koray/train_datasets/yolo_coco_class0/car",
                        "labels": "C:/_koray/train_datasets/yolo_coco_class0/car"
                    }
                ],
            "resize_style": "if_larger",
            "image_size": image_size,
            "input_style": "yolo"
        },
        {
            "class_name": "motorcycle",
            "dirs":
                [
                    {
                        "images": "C:/_koray/train_datasets/yolo_oidv6_class0/motorcycle",
                        "labels": "C:/_koray/train_datasets/yolo_oidv6_class0/motorcycle"
                    },
                    {
                        "images": "C:/_koray/train_datasets/yolo_coco_class0/motorbike",
                        "labels": "C:/_koray/train_datasets/yolo_coco_class0/motorbike"
                    }
                ],
            "resize_style": "if_larger",
            "image_size": image_size,
            "input_style": "yolo"
        },
        {
            "class_name": "truck",
            "dirs":
                [
                    {
                        "images": "C:/_koray/train_datasets/yolo_oidv6_class0/truck",
                        "labels": "C:/_koray/train_datasets/yolo_oidv6_class0/truck"
                    },
                    {
                        "images": "C:/_koray/train_datasets/yolo_coco_class0/truck",
                        "labels": "C:/_koray/train_datasets/yolo_coco_class0/truck"
                    }
                ],
            "resize_style": "if_larger",
            "image_size": image_size,
            "input_style": "yolo"
        },
        {
            "class_name": "van",
            "dirs":
                [
                    {
                        "images": "C:/_koray/train_datasets/yolo_oidv6_class0/van",
                        "labels": "C:/_koray/train_datasets/yolo_oidv6_class0/van"
                    }
                ],
            "resize_style": "if_larger",
            "image_size": image_size,
            "input_style": "yolo"
        }
    ]

    # combine_classes(class_items, images_dir, labels_dir, classes_txt_fn, out_style)

    train_files_dir = "C:/_koray/git/yolov5/data"
    class_names = []
    for item in class_items:
        class_names.append(item["class_name"])

    generate_train_txt(train_files_dir, model_name, class_names, images_dir, ratio_train=0.7, ratio_val=0.3, ratio_test=0)
    check_class_ids(train_files_dir, class_names, model_name)


run_combine_classes()

# def run_lp_test():
#     dir_captured = "C:/_koray/train_datasets/lp_test/captured"
#     dir_captured_416 = "C:/_koray/train_datasets/lp_test/captured_416"
#
#     save_images_with_cv(dir_captured, dir_captured_416, 416)
#
#     train_files_dir = "C:/_koray/git/yolov5/data"
#     model_name = "lp_test_416"
#     images_dir = dir_captured_416
#     class_names = [
#         "lp"
#     ]
#
#     generate_train_txt(train_files_dir, model_name, class_names, images_dir, ratio_train=0.7, ratio_val=0.3, ratio_test=0)
#     check_class_ids(train_files_dir, class_names, model_name)
#
#
# run_lp_test()

# def run_vehicles_lp_416():
#     dir0 = "C:/_koray/train_datasets/vehicles_lp/images"
#     dir416 = "C:/_koray/train_datasets/vehicles_lp_416/images"
#     # save_images_with_cv(dir0, dir416, 416)
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
