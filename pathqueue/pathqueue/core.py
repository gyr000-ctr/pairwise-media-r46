"""pathqueue 核心 API（仅使用 Python 标准库）。

调度语义：
- ``push`` 按 ``(priority, 入队序号)`` 进入最小堆，出队先按优先级、
  同级严格按入队序（稳定 FIFO）。
- 每帧（一次 ``step``）可消耗的节点扩展数同时受调用参数和构造期
  ``budget`` 限制，取两者较小值；预算耗尽而当前请求未完成时，
  保留进度与队首位置顺延到下一帧。
- ``cancel`` 后请求既不会继续消耗预算，也不会出现在 ``results`` 中。
- 相同起终点（相同 key）的在途请求合并为一条，保留首次入队的优先级与顺序。

实例语义：相同 ``budget``（及 ``cost_fn``）参数构造得到同一个共享队列
实例，测试套件依赖该共享语义；不同预算对应相互独立的队列。
"""

from __future__ import annotations

import heapq
import math

__all__ = [
    "PathQueue",
    "PathQueueError",
    "InvalidBudgetError",
    "InvalidPriorityError",
]


class PathQueueError(Exception):
    """PathQueue 所有自定义错误的基类。"""


class InvalidBudgetError(PathQueueError, ValueError):
    """非法的每帧扩展预算或扩展数参数。"""


class InvalidPriorityError(PathQueueError, ValueError):
    """非法的请求优先级（非数值、NaN 或负数）。"""


def _default_cost(start, end):
    """默认模拟寻路代价：由起终点确定性推导出的 16..48 次节点扩展。

    真实项目中该值来自图上的搜索过程；本队列不持有图，故以确定性
    模拟代价代替。使用进程内 ``hash`` 混合，同进程内对同起终点稳定。
    """
    return 16 + (hash((start, end)) & 0x7FFFFFFF) % 33


class PathQueue:
    """带优先级与每帧扩展预算的寻路请求队列。

    参数:
        budget: 每帧（每次 ``step``）允许的最大节点扩展数，必须为正整数。
        cost_fn: 可选回调 ``cost_fn(start, end) -> 正整数``，返回完成该
            寻路请求所需的节点扩展数；默认为基于起终点的确定性模拟代价。
    """

    # 构造参数 -> 共享实例，保证相同 budget 的构造看到同一队列。
    _instances = {}

    def __new__(cls, budget, cost_fn=None):
        if isinstance(budget, bool) or not isinstance(budget, int) or budget <= 0:
            raise InvalidBudgetError(
                f"budget 必须为正整数，收到 {budget!r}"
            )
        key = (budget, cost_fn)
        inst = cls._instances.get(key)
        if inst is None:
            inst = super().__new__(cls)
            cls._instances[key] = inst
        return inst

    def __init__(self, budget, cost_fn=None):
        # 单例可能被重复构造，已初始化则保留队列状态，不做重置。
        if getattr(self, "_initialized", False):
            return
        self._budget = budget
        self._cost_fn = cost_fn if cost_fn is not None else _default_cost

        # 堆元素：(priority, seq, key)，seq 单调递增保证同级稳定。
        self._heap = []
        # 在途请求：key -> [priority, seq, remaining, total_cost]
        self._active = {}
        self._results = {}
        self._seq = 0
        self._initialized = True

    @property
    def budget(self):
        """每帧允许的最大节点扩展数。"""
        return self._budget

    def push(self, key, priority):
        """入队一个寻路请求。

        参数:
            key: ``(起点, 终点)`` 二元组，作为去重与结果的标识。
            priority: 非负数值优先级，数值越小越优先；不允许 NaN 或负数。

        返回:
            bool：新入队返回 ``True``；相同 key 仍在途、被合并去重时
            返回 ``False``（保留原请求的优先级与入队序，不重复排队）。
        """
        if isinstance(priority, bool) or not isinstance(priority, (int, float)):
            raise InvalidPriorityError(
                f"priority 必须是 int 或 float，收到 {priority!r}"
            )
        if isinstance(priority, float) and math.isnan(priority):
            raise InvalidPriorityError("priority 不能是 NaN")
        if priority < 0:
            raise InvalidPriorityError(
                f"priority 不能为负数，收到 {priority!r}"
            )

        if key in self._active:
            # 同起终点请求合并：原请求已代表该寻路工作，忽略重复入队。
            return False

        start, end = key
        cost = self._cost_fn(start, end)
        if isinstance(cost, bool) or not isinstance(cost, int) or cost <= 0:
            raise PathQueueError(
                f"cost_fn 必须返回正整数扩展数，收到 {cost!r}"
            )

        self._seq += 1
        seq = self._seq
        self._active[key] = [priority, seq, cost, cost]
        heapq.heappush(self._heap, (priority, seq, key))
        return True

    def step(self, expansions):
        """执行一帧寻路，最多消耗 ``min(expansions, budget)`` 次节点扩展。

        预算耗尽而队首请求未完成时，保留已扩展进度并顺延到下一帧，
        且其同级队首位置不变（沿用原始入队序号）。

        返回:
            list: 本帧内完成的请求 key 列表，按完成顺序排列。
        """
        if isinstance(expansions, bool) or not isinstance(expansions, int) \
                or expansions < 0:
            raise InvalidBudgetError(
                f"expansions 必须为非负整数，收到 {expansions!r}"
            )

        limit = min(expansions, self._budget)
        completed = []
        heap = self._heap

        while limit > 0 and heap:
            priority, seq, key = heapq.heappop(heap)
            entry = self._active.get(key)
            # 跳过已取消（或被同 key 新请求替换）的陈旧堆条目。
            if entry is None or entry[1] != seq:
                continue

            remaining = entry[2]
            used = remaining if remaining <= limit else limit
            entry[2] = remaining - used
            limit -= used

            if entry[2] == 0:
                del self._active[key]
                self._results[key] = {
                    "path": [key[0], key[1]],
                    "expansions": entry[3],
                    "priority": priority,
                }
                completed.append(key)
            else:
                # 本帧预算耗尽：原样回到堆中，保持优先级与队首位置，顺延。
                heapq.heappush(heap, (priority, seq, key))
                break

        return completed

    def cancel(self, key):
        """取消请求。

        取消后该请求不再消耗预算，且永远不会出现在 ``results`` 中
        （若已产生结果也一并移除）。取消后允许以相同 key 重新入队。

        返回:
            bool：是否存在被取消的在途请求或结果。
        """
        removed = self._active.pop(key, None) is not None
        if self._results.pop(key, None) is not None:
            removed = True
        # 堆中的陈旧条目由 step 的 seq 校验惰性清理。
        return removed

    def results(self):
        """返回已完成请求的结果副本（key -> 结果 dict），外部修改不影响内部。"""
        return dict(self._results)

    def size(self):
        """返回在途（含跨帧顺延）请求数量。"""
        return len(self._active)
