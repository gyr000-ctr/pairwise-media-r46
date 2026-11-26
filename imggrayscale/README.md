# imggrayscale

## 题面（可直接粘贴）

灰度化（亮度保持 + 线性空间）。约束：线性空间按 Rec.709 加权后回转 sRGB，与解析式 ≤1e-9；纯色输入与系数加权一致（≤1e-12）；必须支持亮度保持模式（保留 Y 而替换 chroma），与解析式 ≤1e-9；sRGB↔线性往返 ≤1e-6；通道越界报错；100 万像素不超过 500 ms。 工作目录为仓库内的 imggrayscale/。 验收：cd imggrayscale && python -m pytest tests -q。 实现只允许使用 Python 标准库。

## 运行方式

```bash
cd imggrayscale && python -m pytest tests -q
```

初始 15 failed（实现前）。仅使用 Python 标准库。

## 字段

- 所属领域：游戏、图形与多媒体
- 子方向：图像处理
- 任务类型：Bugfix
- 语言/框架：Python 3, pytest
- 环境可复现等级：无外部依赖
