from os import path
import cv2
from vidgear.gears import CamGear
# pip install vidgear==0.1.9 --upgrade

from image_helper import resize_if_larger


class YoutubeVideoSource():
    def __init__(self, url=None, max_dim=1600):
        self.__url = url
        # self.__url = "https://www.youtube.com/watch?v=ho1QG2OEMFs&t=26s"

        self.__cam_gear_options = {"CAP_PROP_FRAME_WIDTH ": 320, "CAP_PROP_FRAME_HEIGHT": 240, "CAP_PROP_FPS ": 1}

        self.__stream = None
        self._set_capture()
        self._max_dim = max_dim

    def get_frames1(self):
        # import required libraries
        from vidgear.gears import CamGear
        import cv2

        # Add YouTube Video URL as input source (for e.g https://youtu.be/bvetuLwJIkA)
        # and enable Stream Mode (`stream_mode = True`)
        stream = CamGear(
            source=self.__url, stream_mode=True, logging=True
        ).start()

        skip = 0
        # loop over
        while True:

            # read frames from stream
            frame = stream.read()

            # check for frame if Nonetype
            if frame is None:
                break

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

        # close output window
        cv2.destroyAllWindows()

        # safely close video stream
        stream.stop()

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


if __name__ == '__main__':
    vid = YoutubeVideoSource("https://www.youtube.com/watch?v=ho1QG2OEMFs&t=26s")
    i = 0
    for frame in vid.get_frames():
        cv2.imshow("deneme", frame)
        cv2.waitKey(1)
        i += 1
        if i % 30 == 0:
            cv2.imwrite("C:/_koray/temp/frame{}.jpg".format(i), frame)
