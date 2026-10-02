# ui-scroll-list

列表虚拟化：可见区间、滚动钳制、行复用池与数据变更，只用 Python 标准库。

```
python3 -m scroll.cli --sample window
python3 -m scroll.cli --sample clamp
python3 -m scroll.cli --sample pool
python3 -m scroll.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **可见区间**：从 `offset // row_height` 开始，覆盖高度 `viewport_height`
  所需的行数（不足一行也占一行），不加额外的行。
- **钳制**：`scroll_to` 与 `set_items` 之后偏移都必须落在
  `[0, max(0, 条目数 * row_height - viewport_height)]`。
- **复用池**：同时活跃的行对象不超过 `pool_size`；滚出视口的行回收给新
  滚入的行使用，`active_rows` 不超过池子大小，`reuse_count` 记录复用次数。
- **数据变更**：`set_items` 之后旧的行对象全部回收，`visible` 只反映新数据。
- **不变量**：同一串滚动序列重复执行结果相同；`visible` 的下标严格递增。
- **查询代价**：`visible` 不许遍历全部条目，`scanned_count` 不随条目数线性增长。
- **规模**：10 万条目、每秒 10 万次取可见区间，单次摊还 O(可见行数)。

## 输出契约（不改格式）

```
visible=..
offset=.. visible=..
active=..
scanned=..
```

## 目录

```
scroll/core.py   可见区间、钳制与复用池
scroll/cli.py    命令行入口
tests/           unittest 用例
```
