from os import path
import cv2

from image_helper import resize_if_larger


class CameraVideo():
    def __init__(self, capture, max_dim=1600, mirror=False):
        self._capture = capture
        self._mirror = mirror
        self._max_dim = max_dim

    def get_frames(self):
        # count = 0
        try:
            skip = 0
            while self._capture.isOpened():
                ok, frame = self._capture.read()
                if frame is None:
                    break
                if self._max_dim is not None and self._max_dim > 0:
                    frame = resize_if_larger(frame, self._max_dim)
                if self._mirror:
                    frame = cv2.flip(frame, 1)
                if skip > 0:
                    skip = skip - 1
                else:
                    yield frame

                k = cv2.waitKey(1) & 0xFF
                if k == ord("q"):
                    break
                elif k == ord("s"):
                    skip = 10

        except StopIteration:
            pass
        finally:
            cv2.destroyAllWindows()


def _find_video_capture():
    index = -1
    cap = cv2.VideoCapture(index)
    r, fr = cap.read()
    while fr is None:
        index += 1
        if index > 100:
            raise Exception('Cannot capture camera video')
        try:
            cap = cv2.VideoCapture(index)
            r, fr = cap.read()
        except:
            fr = None
    return cap


if __name__ == '__main__':
    # # use camera:
    # cap = _find_video_capture()
    # vid = CameraVideo(cap, max_dim=1600, mirror=True)

    # use video file:
    cap = cv2.VideoCapture("C:/_koray/test_data/fabrika/1_sosyal_mesafe_ihlali.mp4")
    vid = CameraVideo(cap, max_dim=0, mirror=False)

    i = 0
    for frame1 in vid.get_frames():
        cv2.imshow("deneme", frame1)
        cv2.waitKey(1)
        i += 1
        if i % 30 == 0:
            cv2.imwrite("C:/_koray/temp/frame{}.jpg".format(i), frame1)
