# gridbuild

## 题面（可直接粘贴）

建造网格吸附与合法性。约束：物体按锚点吸附到整格（吸附误差 ≤1e-12）；占用冲突与越界报错可区分；必须校验支撑（下方有支撑或允许悬空），悬空非法时返回可区分原因；撤销后占用释放且可再次放置；1 万次放置不超过 400 ms；非法尺寸可区分报错。 工作目录为仓库内的 gridbuild/。 验收：cd gridbuild && python -m pytest tests -q。 实现只允许使用 Python 标准库。

## 运行方式

```bash
cd gridbuild && python -m pytest tests -q
```

初始 15 failed（实现前）。仅使用 Python 标准库。

## 字段

- 所属领域：游戏、图形与多媒体
- 子方向：游戏开发
- 任务类型：Bugfix
- 语言/框架：Python 3, pytest
- 环境可复现等级：无外部依赖
