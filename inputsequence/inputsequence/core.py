"""inputsequence 核心实现（仅标准库）。

按时间窗匹配按键序列：
- 序列必须在窗口内完成（首末按键时间差 <= window），否则不成立；
- 允许序列间前缀重叠，同一按键事件可完成多条序列时最长匹配优先；
- 同帧（相同时间戳）多键按 feed 调用顺序处理；
- 所有实例共享同一输入总线（全局按键流），matched() 返回并清空
  自上次调用以来匹配到的序列（事件消费语义）；
- 未完成的序列超时可通过 check_timeout()/expired() 以
  SequenceTimeoutError 区分；非法窗口以 InvalidWindowError 区分。
  所有错误均为 ValueError 的子类，但类型互不相同，可分别捕获。
"""

import math
from collections import deque

__all__ = [
    "InputSeq",
    "InputSeqError",
    "InvalidWindowError",
    "InvalidKeyError",
    "InvalidTimeError",
    "SequenceTimeoutError",
    "DEFAULT_SEQUENCES",
]

#: 默认识别的指令序列（可通过构造参数 sequences 覆盖）。
DEFAULT_SEQUENCES = ("pk", "kp")


class InputSeqError(ValueError):
    """InputSeq 所有错误的基类（ValueError 子类，便于区分捕获）。"""


class InvalidWindowError(InputSeqError):
    """非法时间窗（非正数、非数值或非有限值）。"""


class InvalidKeyError(InputSeqError):
    """非法按键（空串或非字符串）。"""


class InvalidTimeError(InputSeqError):
    """非法时间戳（非数值、NaN 或无穷）。"""


class SequenceTimeoutError(InputSeqError):
    """进行中的序列未在窗口内完成而超时。"""

    def __init__(self, pending, started, deadline, now):
        self.pending = pending
        self.started = started
        self.deadline = deadline
        self.now = now
        super().__init__(
            "序列 %r 未在窗口内完成：开始于 %.6f，截止 %.6f，当前 %.6f"
            % (pending, started, deadline, now)
        )


def _check_window(window):
    if (
        isinstance(window, bool)
        or not isinstance(window, (int, float))
        or not math.isfinite(window)
        or window <= 0
    ):
        raise InvalidWindowError("非法时间窗: %r（需为正有限数）" % (window,))
    return float(window)


def _check_t(t):
    if (
        isinstance(t, bool)
        or not isinstance(t, (int, float))
        or not math.isfinite(t)
    ):
        raise InvalidTimeError("非法时间戳: %r（需为有限数值，NaN 不允许）" % (t,))
    return float(t)


class InputSeq:
    """时间窗按键序列识别器。

    所有实例共享同一输入总线状态（构造新实例不会清空按键流）。
    feed(key, t) 返回本次输入新匹配到的序列列表（通常 0 或 1 个）；
    matched() 返回并清空至今待消费的匹配结果；reset() 清空共享的
    输入缓冲与待消费结果。
    """

    # 共享输入总线：按键流缓冲与待消费匹配结果。
    _buf = deque()      # 窗口内的 (key, t)，按输入先后排列
    _pending = []       # 已匹配但未被 matched() 消费的序列

    def __init__(self, window, sequences=None):
        self._window = _check_window(window)
        seqs = DEFAULT_SEQUENCES if sequences is None else tuple(sequences)
        for s in seqs:
            if not isinstance(s, str) or not s:
                raise InvalidKeyError("非法序列: %r（需为非空字符串）" % (s,))
        # 按末键索引，同末键时最长优先（前缀重叠时最长匹配优先）。
        self._by_last = {}
        for s in sorted(set(seqs), key=len, reverse=True):
            self._by_last.setdefault(s[-1], []).append(s)
        self._max_len = max((len(s) for s in seqs), default=0)

    @property
    def window(self):
        return self._window

    def feed(self, key, t):
        """输入一个按键。同帧多键按调用顺序处理。返回新匹配的序列列表。"""
        # 先校验，非法输入不改变任何状态。
        if not isinstance(key, str) or not key:
            raise InvalidKeyError("非法按键: %r（需为非空字符串）" % (key,))
        t = _check_t(t)
        buf = self._buf
        # 只保留落在当前窗口 [t-window, t] 内的输入：
        # 过旧的输入（其未完成序列随之超时失效）与相对当前时间
        # 处于“未来”的输入（时间回退，视为新会话）都丢弃。
        lo = t - self._window
        while buf and (buf[0][1] < lo or buf[0][1] > t):
            buf.popleft()
        while buf and (buf[-1][1] < lo or buf[-1][1] > t):
            buf.pop()
        buf.append((key, t))
        new = []
        for cand in self._by_last.get(key, ()):  # 已按长度降序
            n = len(cand)
            if n > len(buf):
                continue
            for i in range(1, n + 1):
                if buf[-i][0] != cand[n - i]:
                    break
            else:
                new.append(cand)
                self._pending.append(cand)
                for _ in range(n):
                    buf.pop()
                break  # 最长匹配优先，每个按键事件至多完成一条序列
        return new

    def matched(self):
        """返回并清空至今匹配到、尚未消费的序列列表（按匹配先后）。"""
        out = self._pending[:]
        del self._pending[:]
        return out

    def reset(self):
        """清空共享的输入缓冲与待消费匹配结果。"""
        self._buf.clear()
        del self._pending[:]

    def expired(self, t):
        """若缓冲中存在在时刻 t 已超时的未完成序列，返回对应错误，否则 None。"""
        t = _check_t(t)
        if self._buf and self._buf[0][1] < t - self._window:
            pending = "".join(k for k, _ in self._buf)
            started = self._buf[0][1]
            return SequenceTimeoutError(
                pending, started, started + self._window, t
            )
        return None

    def check_timeout(self, t):
        """在时刻 t 检查超时；存在超时的未完成序列时抛出 SequenceTimeoutError。"""
        err = self.expired(t)
        if err is not None:
            raise err
