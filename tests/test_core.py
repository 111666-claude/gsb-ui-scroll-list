import unittest

from scroll.core import ListView


class BasicTest(unittest.TestCase):
    def test_empty_list_has_no_rows(self):
        self.assertEqual(ListView(20, 100, 3).visible(), [])

    def test_single_item_is_visible(self):
        view = ListView(20, 100, 3)
        view.set_items(["a"])
        self.assertEqual(view.visible(), [(0, "a")])

    def test_max_offset_when_list_is_short(self):
        view = ListView(20, 100, 3)
        view.set_items(["a", "b"])
        self.assertEqual(view.max_offset(), 0)

    def test_pool_size_is_stored(self):
        self.assertEqual(ListView(20, 100, 4).pool_size, 4)

    def test_scanned_starts_at_zero(self):
        self.assertEqual(ListView(20, 100, 3).scanned_count(), 0)


if __name__ == "__main__":
    unittest.main()
