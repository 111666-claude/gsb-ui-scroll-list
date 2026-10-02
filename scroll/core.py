"""列表虚拟化：可见区间、滚动钳制、行复用池与数据变更。"""


class ListView:
    """虚拟列表。"""

    def __init__(self, row_height, viewport_height, pool_size):
        self.row_height = row_height
        self.viewport_height = viewport_height
        self.pool_size = pool_size
        self.items = []
        self.offset = 0
        self.rows = {}
        self.free = []
        self.active = 0
        self.reuses = 0
        self.scanned = 0

    def set_items(self, items):
        self.items = list(items)
        self.free.extend(self.rows.values())
        self.rows = {}
        self.active = 0
        self.offset = min(max(self.offset, 0), self.max_offset())

    def max_offset(self):
        total = len(self.items) * self.row_height
        return max(0, total - self.viewport_height)

    def scroll_to(self, offset):
        self.offset = min(max(offset, 0), self.max_offset())

    def visible(self):
        """当前可见的 (下标, 条目) 列表。

        用下标算术直接定位窗口，每次查询只记一次 scanned，
        不遍历全部条目，下标严格递增。
        """
        self.scanned += 1
        if self.row_height <= 0 or self.viewport_height <= 0:
            return []
        first = self.offset // self.row_height
        last = (self.offset + self.viewport_height - 1) // self.row_height
        end = min(last + 1, len(self.items))
        return [(index, self.items[index]) for index in range(first, end)]

    def render(self):
        """渲染一帧，返回可见条目；滚出视口的行回收给滚入的行。"""
        rows = self.visible()
        wanted = set(index for index, _ in rows)
        for index in [index for index in self.rows if index not in wanted]:
            self.free.append(self.rows.pop(index))
        for index, _ in rows:
            if index in self.rows:
                continue
            if self.free:
                row = self.free.pop()
                row["index"] = index
                self.reuses += 1
            elif len(self.rows) + len(self.free) >= self.pool_size:
                break
            else:
                row = {"index": index}
            self.rows[index] = row
        self.active = len(self.rows)
        return rows

    def active_rows(self):
        return self.active

    def reuse_count(self):
        return self.reuses

    def scanned_count(self):
        return self.scanned
