"""imggrayscale 核心 API（仅标准库）。

灰度化在**线性空间**按 Rec.709 系数加权（Y = 0.2126 R + 0.7152 G + 0.0722 B），
随后将 Y 从线性空间转回 sRGB。

- ``to_gray(rgb)``        -> 单个 sRGB 灰度值（float）
- ``desaturate(rgb)``     -> 亮度保持模式：保留 Y、替换 chroma，返回 (g, g, g)
- ``apply(image)``        -> 整图灰度，返回 行列表，每行是 float 列表
- ``apply_preserve(image)`` -> 整图亮度保持模式，返回 行列表，每行是 (g, g, g) 列表
- ``srgb_to_linear`` / ``linear_to_srgb`` -> 分量级转换函数
"""

import math

__all__ = ["Grayscale"]

# Rec.709 亮度系数
WR = 0.2126
WG = 0.7152
WB = 0.0722

# sRGB 分段转换常数
_A = 0.055
_LIN_THRESHOLD = 0.04045          # sRGB -> linear 的分段点（sRGB 侧）
_ENC_THRESHOLD = 0.0031308        # linear -> sRGB 的分段点（线性侧）
_GAMMA = 2.4
_INV_GAMMA = 1.0 / 2.4


def _srgb_to_linear(c):
    """sRGB 分量 [0,1] -> 线性分量 [0,1]"""
    if c <= _LIN_THRESHOLD:
        return c / 12.92
    return ((c + _A) / (1.0 + _A)) ** _GAMMA


def _linear_to_srgb(c):
    """线性分量 [0,1] -> sRGB 分量 [0,1]"""
    if c <= _ENC_THRESHOLD:
        return c * 12.92
    return (1.0 + _A) * c ** _INV_GAMMA - _A


def _validate(rgb):
    """校验像素：必须为 3 通道、有限、且在 [0, 1] 内，否则 ValueError。"""
    try:
        r, g, b = rgb
    except (TypeError, ValueError) as exc:
        raise ValueError("pixel must have exactly 3 channels") from exc
    for c in (r, g, b):
        if not isinstance(c, (int, float)) or isinstance(c, bool):
            raise ValueError("channel must be a real number")
        if not (0.0 <= c <= 1.0):  # NaN 使比较为 False，同样触发
            raise ValueError("channel out of range [0, 1]: %r" % (c,))
    return float(r), float(g), float(b)


class Grayscale:
    """灰度化器。``preserve_luminance=True`` 时 ``apply`` 使用亮度保持模式。"""

    def __init__(self, preserve_luminance=False):
        self.preserve_luminance = bool(preserve_luminance)

    # 分量级转换（公开，便于测试往返精度）
    srgb_to_linear = staticmethod(_srgb_to_linear)
    linear_to_srgb = staticmethod(_linear_to_srgb)

    def to_gray(self, rgb):
        """单像素灰度：线性空间 Rec.709 加权后回转 sRGB，返回 float。"""
        r, g, b = _validate(rgb)
        if r == g == b:  # 已是灰色：往返转换即原值（且满足 <=1e-6 往返约束）
            return r
        y = (WR * _srgb_to_linear(r)
             + WG * _srgb_to_linear(g)
             + WB * _srgb_to_linear(b))
        return _linear_to_srgb(y)

    def desaturate(self, rgb):
        """亮度保持模式：保留 Y、替换 chroma，返回 (g, g, g) 三元组。"""
        g = self.to_gray(rgb)
        return (g, g, g)

    def apply(self, image):
        """整图灰度化。

        image 为 行（可迭代）的列表，每行是 (r, g, b) 像素的列表。
        默认返回每行 float 灰度值的列表；构造时 preserve_luminance=True
        则返回每行 (g, g, g) 元组的列表。不修改输入。
        """
        if self.preserve_luminance:
            return self.apply_preserve(image)

        out = []
        out_append = out.append
        for row in image:
            orow = []
            orow_append = orow.append
            for px in row:
                r, g, b = _validate(px)
                if r == g == b:
                    orow_append(r)
                    continue
                # 内联 sRGB->linear（避免每通道一次函数调用）
                lr = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
                lg = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
                lb = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4
                y = WR * lr + WG * lg + WB * lb
                # 内联 linear->sRGB
                orow_append(y * 12.92 if y <= 0.0031308
                            else 1.055 * y ** (1.0 / 2.4) - 0.055)
            out_append(orow)
        return out

    def apply_preserve(self, image):
        """整图亮度保持模式：每像素替换为 (g, g, g)，保留原亮度 Y。"""
        out = []
        out_append = out.append
        for row in image:
            orow = []
            orow_append = orow.append
            for px in row:
                r, g, b = _validate(px)
                if r == g == b:
                    orow_append((r, r, r))
                    continue
                lr = r / 12.92 if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
                lg = g / 12.92 if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
                lb = b / 12.92 if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4
                y = WR * lr + WG * lg + WB * lb
                g8 = y * 12.92 if y <= 0.0031308 else 1.055 * y ** (1.0 / 2.4) - 0.055
                orow_append((g8, g8, g8))
            out_append(orow)
        return out
