"""imgtint 核心 API（仅标准库）。

着色（Tint）支持两条可切换路径：

- ``multiply``：逐通道乘法着色，解析式为 ``out = rgb * color``，
  保持亮度比；``amount`` 在原色与完全着色结果之间线性插值。
- ``hsl``：HSL 色相旋转，将像素色相沿最短弧转向着色色相，
  饱和度与亮度保持不变；``amount`` 控制旋转比例。

共同约定：``amount`` 为 0 时恒等、为 1 时完全着色；输入分量越界
钳制到 [0, 1]；非法 ``amount`` 抛出可区分的异常（非数值为
``TypeError``，NaN/Inf 或超出 [0, 1] 为 ``ValueError``）。
"""

import colorsys
import math
from numbers import Real

__all__ = ["Tint"]

_MODES = ("multiply", "hsl")


def _is_number(x):
    return isinstance(x, Real) and not isinstance(x, bool)


def _clamp01(v):
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _coerce_rgb(rgb, name):
    """校验并转换为 3 元 float 元组；不合法时抛出 ValueError。"""
    if isinstance(rgb, (str, bytes)):
        raise ValueError("%s 必须是含 3 个数值的序列" % name)
    try:
        vals = tuple(rgb)
    except TypeError:
        raise ValueError("%s 必须是含 3 个数值的序列" % name) from None
    if len(vals) != 3:
        raise ValueError("%s 长度必须为 3，实际为 %d" % (name, len(vals)))
    out = []
    for v in vals:
        if not _is_number(v):
            raise ValueError("%s 分量必须是数值，得到 %r" % (name, v))
        f = float(v)
        if not math.isfinite(f):
            raise ValueError("%s 分量必须是有限数值，得到 %r" % (name, v))
        out.append(f)
    return tuple(out)


def _check_amount(amount):
    """校验着色强度；非数值抛 TypeError，越界/非有限抛 ValueError。"""
    if not _is_number(amount):
        raise TypeError(
            "amount 必须是数值，得到 %s" % type(amount).__name__
        )
    a = float(amount)
    if not math.isfinite(a):
        raise ValueError("amount 必须是有限数值，得到 %r" % (amount,))
    if a < 0.0 or a > 1.0:
        raise ValueError("amount 必须位于 [0, 1]，得到 %r" % (amount,))
    return a


class Tint:
    """着色器：构造时给定着色颜色与路径模式。"""

    def __init__(self, color, mode="multiply"):
        vals = _coerce_rgb(color, "color")
        for v in vals:
            if v < 0.0 or v > 1.0:
                raise ValueError("color 分量必须位于 [0, 1]，得到 %r" % (v,))
        if mode not in _MODES:
            raise ValueError(
                "mode 必须是 %s 之一，得到 %r" % ("/".join(_MODES), mode)
            )
        self._color = vals
        self._mode = mode
        # HSL 路径只需着色颜色的色相。
        self._tint_hue = colorsys.rgb_to_hls(*vals)[0]

    @property
    def color(self):
        return self._color

    @property
    def mode(self):
        return self._mode

    def multiply(self, rgb):
        """乘法路径的完全着色：out = clamp(rgb) * color（逐通道）。"""
        vals = _coerce_rgb(rgb, "rgb")
        c = self._color
        return (
            _clamp01(vals[0] * c[0]),
            _clamp01(vals[1] * c[1]),
            _clamp01(vals[2] * c[2]),
        )

    def apply(self, rgb, amount):
        """按当前模式以强度 amount 对单个像素着色。"""
        a = _check_amount(amount)
        vals = _coerce_rgb(rgb, "rgb")
        r = _clamp01(vals[0])
        g = _clamp01(vals[1])
        b = _clamp01(vals[2])
        if a == 0.0:
            return (r, g, b)
        if self._mode == "hsl":
            return self._apply_hsl(r, g, b, a)
        c = self._color
        # out = v * ((1-a) + a*color)，强度 1 时即解析式 v*color。
        return (
            r * (1.0 - a + a * c[0]),
            g * (1.0 - a + a * c[1]),
            b * (1.0 - a + a * c[2]),
        )

    def apply_batch(self, pixels, amount):
        """批量着色；乘法路径预计算每通道增益以保证吞吐量。

        快速路径对分量做有限性校验（NaN/Inf 抛 ValueError）并钳制到
        [0, 1]；序列结构非法（长度不为 3、分量非数值）时回退到逐像素
        严格校验，抛出与 apply 一致的异常。
        """
        a = _check_amount(amount)
        if self._mode == "hsl":
            return [self.apply(p, a) for p in pixels]
        c = self._color
        g0 = 1.0 - a + a * c[0]
        g1 = 1.0 - a + a * c[1]
        g2 = 1.0 - a + a * c[2]
        try:
            return [
                (_clamp01(r * g0), _clamp01(g * g1), _clamp01(b * g2))
                if r - r == g - g == b - b == 0.0
                else self._reject_pixel((r, g, b))
                for r, g, b in pixels
            ]
        except (TypeError, ValueError):
            # 结构非法或分量非有限：逐像素严格校验，抛出一致的异常。
            return [self.apply(p, a) for p in pixels]

    @staticmethod
    def _reject_pixel(p):
        raise ValueError("rgb 分量必须是有限数值，得到 %r" % (p,))

    def _apply_hsl(self, r, g, b, a):
        """HSL 路径：仅旋转色相，饱和度与亮度保持不变。"""
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        # 沿最短弧插值色相。
        delta = (self._tint_hue - h + 0.5) % 1.0 - 0.5
        h2 = (h + a * delta) % 1.0
        rr, gg, bb = colorsys.hls_to_rgb(h2, l, s)
        return (_clamp01(rr), _clamp01(gg), _clamp01(bb))
