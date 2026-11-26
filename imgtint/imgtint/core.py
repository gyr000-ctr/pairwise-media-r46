"""imgtint 核心 API（初始未实现，仅标准库）。"""


class Tint:
    def __init__(self, color):
        """构造"""
        raise NotImplementedError

    def apply(self, rgb, amount):
        """着色"""
        raise NotImplementedError
