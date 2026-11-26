# inputsequence

## 题面（可直接粘贴）

指令序列识别。约束：按时间窗匹配按键序列且必须在窗口内完成；允许前缀重叠（最长匹配优先）；未完成序列超时报错可区分；同帧多键按序处理；10 万次输入不超过 400 ms；非法窗口可区分报错。 工作目录为仓库内的 inputsequence/。 验收：cd inputsequence && python -m pytest tests -q。 实现只允许使用 Python 标准库。

## 运行方式

```bash
cd inputsequence && python -m pytest tests -q
```

初始 15 failed（实现前）。仅使用 Python 标准库。

## 字段

- 所属领域：游戏、图形与多媒体
- 子方向：游戏开发
- 任务类型：Bugfix
- 语言/框架：Python 3, pytest
- 环境可复现等级：无外部依赖
