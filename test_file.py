from file_helper import *

fn = ".data/dictionary/Turkish.dic"
fn1 = ".data/dictionary/Turkish.txt"

txts = []
for line in read_lines(fn):
    # print(line)
    arr = line.split("/")
    if len(arr) > 0:
        txt = arr[0]
        txts.append(txt)
write_lines(fn1, txts)

