# imgtint

## 题面（可直接粘贴）

着色（HSL 与乘法双路径）。约束：HSL 色相旋转不改变饱和度与亮度（≤1e-6）；乘法着色保持亮度比，与解析式 ≤1e-9；两条路径可切换且强度 0 恒等（≤1e-12）、1 完全着色；越界钳制到 [0,1]；100 万像素不超过 500 ms；非法强度可区分报错。 工作目录为仓库内的 imgtint/。 验收：cd imgtint && python -m pytest tests -q。 实现只允许使用 Python 标准库。

## 运行方式

```bash
cd imgtint && python -m pytest tests -q
```

初始 15 failed（实现前）。仅使用 Python 标准库。

## 字段

- 所属领域：游戏、图形与多媒体
- 子方向：图像处理
- 任务类型：Bugfix
- 语言/框架：Python 3, pytest
- 环境可复现等级：无外部依赖
