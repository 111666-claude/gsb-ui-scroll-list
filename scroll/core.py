"""列表虚拟化：可见区间、滚动钳制、行复用池与数据变更。

缺陷：可见区间多算一行、滚动偏移不钳制、每次渲染都新建行不复用、
换数据不清旧行、可见区间计算扫描全部条目。
"""


class ListView:
    """虚拟列表。"""

    def __init__(self, row_height, viewport_height, pool_size):
        self.row_height = row_height
        self.viewport_height = viewport_height
        self.pool_size = pool_size
        self.items = []
        self.offset = 0
        self.rows = {}
        self.live = []
        self.active = 0
        self.reuses = 0
        self.scanned = 0

    def set_items(self, items):
        self.items = list(items)
        self.rows = {}
        self.live = []
        self.active = 0

    def max_offset(self):
        total = len(self.items) * self.row_height
        return max(0, total - self.viewport_height)

    def scroll_to(self, offset):
        self.offset = offset

    def visible(self):
        """当前可见的 (下标, 条目) 列表。"""
        self.scanned += len(self.items)
        first = self.offset // self.row_height
        count = self.viewport_height // self.row_height + 1
        out = []
        for index in range(first, first + count):
            if 0 <= index < len(self.items):
                out.append((index, self.items[index]))
        return out

    def render(self):
        """渲染一帧，返回可见条目。"""
        rows = self.visible()
        for index, _ in rows:
            if index not in self.rows:
                self.rows[index] = {"index": index}
        self.active = len(self.rows)
        return rows

    def active_rows(self):
        return self.active

    def reuse_count(self):
        return self.reuses

    def scanned_count(self):
        return self.scanned
