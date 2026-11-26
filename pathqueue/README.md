# pathqueue

## 题面（可直接粘贴）

寻路请求队列与预算。约束：按优先级出队且同级按入队序（稳定）；每帧寻路预算受节点扩展数限制，超出则顺延；取消后不再返回结果；重复请求去重（同起终点合并）；10 万次入队不超过 300 ms；非法优先级可区分报错。 工作目录为仓库内的 pathqueue/。 验收：cd pathqueue && python -m pytest tests -q。 实现只允许使用 Python 标准库。

## 运行方式

```bash
cd pathqueue && python -m pytest tests -q
```

初始 15 failed（实现前）。仅使用 Python 标准库。

## 字段

- 所属领域：游戏、图形与多媒体
- 子方向：游戏开发
- 任务类型：Bugfix
- 语言/框架：Python 3, pytest
- 环境可复现等级：无外部依赖
