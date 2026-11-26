"""inputsequence 核心 API（初始未实现，仅标准库）。"""


class InputSeq:
    def __init__(self, window):
        """构造"""
        raise NotImplementedError

    def feed(self, key, t):
        """输入"""
        raise NotImplementedError

    def matched(self):
        """已匹配序列"""
        raise NotImplementedError
