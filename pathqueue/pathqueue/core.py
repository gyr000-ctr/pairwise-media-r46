"""pathqueue 核心 API（初始未实现，仅标准库）。"""


class PathQueue:
    def __init__(self, budget):
        """构造"""
        raise NotImplementedError

    def push(self, key, priority):
        """入队"""
        raise NotImplementedError

    def step(self, expansions):
        """执行一步"""
        raise NotImplementedError

    def results(self):
        """结果"""
        raise NotImplementedError
