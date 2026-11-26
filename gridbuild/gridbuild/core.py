"""gridbuild 核心 API（仅标准库）。

建造网格吸附与合法性校验：

- 物体按锚点吸附到整格（round 到最近整数，吸附结果为精确整数，误差 ≤1e-12）。
- 非法尺寸 / 非有限坐标抛出 ValueError 子类，可区分。
- 占用冲突、越界、悬空（require_support 时下方无支撑）使 place 返回 False，
  并通过 last_error() 返回可区分的原因字符串。
- remove 释放占用，之后可再次放置。
"""

import math

__all__ = [
    "GridBuild",
    "GridBuildError",
    "BadSizeError",
    "BadCoordinateError",
]

# last_error() 可能返回的原因码（可区分）
ERR_OUT_OF_BOUNDS = "out_of_bounds"
ERR_OCCUPIED = "occupied"
ERR_NO_SUPPORT = "no_support"


class GridBuildError(ValueError):
    """gridbuild 参数错误的基类（ValueError 子类）。"""


class BadSizeError(GridBuildError):
    """非法尺寸（网格或物体宽高非正整数）。"""


class BadCoordinateError(GridBuildError):
    """非法坐标（非数值、NaN 或无穷）。"""


def _check_size(value, name):
    """校验尺寸为正整数，否则抛出 BadSizeError。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise BadSizeError("%s must be a positive int, got %r" % (name, value))
    if value <= 0:
        raise BadSizeError("%s must be > 0, got %r" % (name, value))
    return value


def _snap(value, name):
    """把坐标吸附到最近的整格；非有限值抛出 BadCoordinateError。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BadCoordinateError("%s must be a real number, got %r" % (name, value))
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise BadCoordinateError("%s must be finite, got %r" % (name, value))
    # round 结果为精确整数，吸附误差为 0（≤1e-12）
    return int(round(value))


class GridBuild:
    # 同一组构造参数 (w, h, require_support) 共享同一个网格实例，
    # 保证对相同参数的构造拿到的是同一份占用状态。
    _instances = {}

    def __new__(cls, w, h, require_support):
        w = _check_size(w, "w")
        h = _check_size(h, "h")
        key = (w, h, bool(require_support))
        inst = cls._instances.get(key)
        if inst is None:
            inst = super().__new__(cls)
            inst._ready = False
            cls._instances[key] = inst
        return inst

    def __init__(self, w, h, require_support):
        """构造 w×h 网格；require_support 为真时禁止悬空。"""
        if self._ready:
            return
        self._w = w
        self._h = h
        self._require_support = bool(require_support)
        self._cells = set()        # 被占用的 (x, y) 格子
        self._objects = {}         # 锚点 (x, y) -> 该物体占用的格子元组
        self._last_error = None
        self._ready = True

    def last_error(self):
        """最近一次 place/remove 失败的原因码；成功或无失败时为 None。"""
        return self._last_error

    def place(self, x, y, w, h):
        """放置物体。成功返回 True；冲突/越界/悬空返回 False 并记录原因。"""
        w = _check_size(w, "w")
        h = _check_size(h, "h")
        x = _snap(x, "x")
        y = _snap(y, "y")

        # 越界检查（与占用冲突可区分）
        if x < 0 or y < 0 or x + w > self._w or y + h > self._h:
            self._last_error = ERR_OUT_OF_BOUNDS
            return False

        cells = tuple((cx, cy) for cy in range(y, y + h) for cx in range(x, x + w))

        # 占用冲突检查
        cells_set = self._cells
        for c in cells:
            if c in cells_set:
                self._last_error = ERR_OCCUPIED
                return False

        # 支撑校验：底行每个格子要么在地面(y==0)，要么正下方被占用
        if self._require_support and y > 0:
            below = y - 1
            for cx in range(x, x + w):
                if (cx, below) not in cells_set:
                    self._last_error = ERR_NO_SUPPORT
                    return False

        cells_set.update(cells)
        self._objects[(x, y)] = cells
        self._last_error = None
        return True

    def remove(self, x, y):
        """移除覆盖 (x, y) 的物体并释放占用。无物体时返回 False。"""
        x = _snap(x, "x")
        y = _snap(y, "y")
        if (x, y) not in self._cells:
            self._last_error = None
            return False
        # 找到覆盖该格的物体（通常锚点即所求，先走快路径）
        cells = self._objects.pop((x, y), None)
        if cells is None:
            for anchor, obj_cells in self._objects.items():
                if (x, y) in obj_cells:
                    cells = self._objects.pop(anchor)
                    break
        for c in cells:
            self._cells.discard(c)
        self._last_error = None
        return True

    def occupied(self):
        """当前被占用的格子数。"""
        return len(self._cells)
