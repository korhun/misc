from os import path
import cv2
import time
from vidgear.gears import CamGear

class YoutubeVideoSource():
    def __init__(self, url):
        """

        :param source_config:
        """
        super().__init__()
        self.__url = url

        self.__cam_gear_options = {"CAP_PROP_FRAME_WIDTH ": 320, "CAP_PROP_FRAME_HEIGHT": 240, "CAP_PROP_FPS ": 1}

        self.__stream = None
        self._set_capture()

    def get_frames(self):
        count = 0
        self.__stream.start()
        try:
            while True:
                frame = self.__stream.read()
                if frame is None:
                    break
                yield count, frame
                count += 1

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




# İmaj boyutlarından birisi max_dim'den daha büyükse küçültür, değilse aynen döner.
def resize_if_larger(image, max_dim, interpolation=None):
    h, w = image.shape[:2]
    if w > h:
        if w > max_dim:
            return resize(image, width=max_dim)
        else:
            return image
    else:
        if h > max_dim:
            return resize(image, height=max_dim)
        else:
            return image

# 'width' veya 'height yoksa en-boy oranını koruyarak resize eder. İkisi de varsa normal resize eder.
# 'interpolation' yoksa en uygununu seçer.
def resize(image, width=None, height=None, interpolation=None):
    if width is None and height is None:
        return image

    h, w = image.shape[:2]
    dim = None
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    elif height is None:
        r = width / float(w)
        dim = (width, int(h * r))
    else:
        dim = (width, height)

    if interpolation is None:
        return resize_best_quality(image, dim)
    else:
        return cv2.resize(image, dim, interpolation=interpolation)

# Boyut değişikliğine en uygun interpolation yöntemi ile resize eder.
def resize_best_quality(image, size):
    size0 = max(image.shape[0], image.shape[1])
    size1 = max(size[0], size[1])
    if size0 > size1:
        return cv2.resize(image, size, interpolation=cv2.INTER_LANCZOS4)
    else:
        return cv2.resize(image, size, interpolation=cv2.INTER_CUBIC)