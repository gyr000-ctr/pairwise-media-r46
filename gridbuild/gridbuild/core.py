"""gridbuild 核心 API（初始未实现，仅标准库）。"""


class GridBuild:
    def __init__(self, w, h, require_support):
        """构造"""
        raise NotImplementedError

    def place(self, x, y, w, h):
        """放置"""
        raise NotImplementedError

    def remove(self, x, y):
        """移除"""
        raise NotImplementedError

    def occupied(self):
        """占用格数"""
        raise NotImplementedError
