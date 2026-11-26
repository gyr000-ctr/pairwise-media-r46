"""imggrayscale 核心 API（初始未实现，仅标准库）。"""


class Grayscale:
    def to_gray(self, rgb):
        """单像素灰度"""
        raise NotImplementedError

    def apply(self, image):
        """整图"""
        raise NotImplementedError
