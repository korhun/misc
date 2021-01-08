from os import path
import cv2
from vidgear.gears import CamGear
#pip install vidgear==0.1.9 --upgrade

from image_helper import resize_if_larger


class YoutubeVideoSource():
    def __init__(self, main_win_name, url=None, max_dim=1600):
        if url is None:
            # url = "https://youtu.be/MNn9qKG2UFI"  # highway
            url = "https://www.youtube.com/watch?v=8Ts9M2f11HE"  # drag
            # url = "https://www.youtube.com/watch?v=ho1QG2OEMFs&t=26s"  # TR
        # max_dim = None

        self.__url = url

        self.__cam_gear_options = {"CAP_PROP_FRAME_WIDTH ": 320, "CAP_PROP_FRAME_HEIGHT": 240, "CAP_PROP_FPS ": 1}

        self.__stream = None
        self._set_capture()
        self._max_dim = max_dim
        self._main_win_name = main_win_name

    def get_frames(self):
        # count = 0
        self.__stream.start()
        try:
            skip = 0
            while True:
                frame = self.__stream.read()
                if frame is None:
                    break
                if self._max_dim is not None:
                    frame = resize_if_larger(frame, self._max_dim)

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
            self.stop()

    def reset(self):
        self.__stream.stop()
        self._set_capture()

    def stop(self):
        self.__stream.stop()

    def _set_capture(self):
        self.__stream = CamGear(source=self.__url, y_tube=True, time_delay=1, logging=True, **self.__cam_gear_options)


vid = YoutubeVideoSource("https://www.youtube.com/watch?v=ho1QG2OEMFs&t=26s")
i=0
for frame in vid.get_frames():
    cv2.imshow("deneme", frame)
    i+=1
    if i % 30:
        cv2.imwrite("C:/_koray/temp/frame{}.jpg".format(i), frame)
