from PIL import ImageGrab
import numpy as np
import cv2


class ScreenCapturer():
    def __init__(self, bbox=(0, 0, 1000, 800)):
        self._bbox = bbox

    def get_frames(self):
        skip = 0
        while True:
            img = ImageGrab.grab(bbox=self._bbox)  # bbox specifies specific region (bbox= x,y,width,height *starts top-left)
            frame = np.array(img)  # this is the array obtained from conversion

            if skip > 0:
                skip = skip - 1
            else:
                yield frame

            k = cv2.waitKey(1) & 0xFF
            if k == ord("q"):
                break
            elif k == ord("s"):
                skip = 10

#
# if __name__ == '__main__':
#     vid = ScreenCapturer()
#     i = 0
#     for frame in vid.get_frames():
#         cv2.imshow("deneme", frame)
#         cv2.waitKey(1)
#         # i += 1
#         # if i % 30 == 0:
#         #     cv2.imwrite("C:/_koray/temp/frame{}.jpg".format(i), frame)
