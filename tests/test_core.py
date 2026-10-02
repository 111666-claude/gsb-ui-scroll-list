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


class VisibleWindowTest(unittest.TestCase):
    def test_exact_rows_fit_viewport(self):
        view = ListView(20, 100, 6)
        view.set_items(["i-%d" % index for index in range(10)])
        self.assertEqual(len(view.visible()), 5)

    def test_partial_row_counts_as_full_row(self):
        view = ListView(20, 101, 8)
        view.set_items(["i-%d" % index for index in range(10)])
        self.assertEqual(len(view.visible()), 6)

    def test_window_starts_at_offset_div_row_height(self):
        view = ListView(20, 40, 4)
        view.set_items(["i-%d" % index for index in range(10)])
        view.scroll_to(45)
        self.assertEqual([index for index, _ in view.visible()], [2, 3])

    def test_visible_indices_strictly_increase(self):
        view = ListView(20, 50, 5)
        view.set_items(["i-%d" % index for index in range(100)])
        view.scroll_to(37)
        indices = [index for index, _ in view.visible()]
        self.assertTrue(all(a < b for a, b in zip(indices, indices[1:])))


class ClampTest(unittest.TestCase):
    def test_scroll_beyond_end_is_clamped(self):
        view = ListView(20, 100, 3)
        view.set_items(["a", "b", "c"])
        view.scroll_to(500)
        self.assertEqual(view.offset, 0)
        self.assertEqual(len(view.visible()), 3)

    def test_negative_scroll_is_clamped_to_zero(self):
        view = ListView(20, 100, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        view.scroll_to(-50)
        self.assertEqual(view.offset, 0)

    def test_scroll_clamped_to_max_offset(self):
        view = ListView(20, 100, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        view.scroll_to(10 ** 9)
        self.assertEqual(view.offset, 1900)

    def test_set_items_clamps_existing_offset(self):
        view = ListView(20, 100, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        view.scroll_to(1900)
        view.set_items(["a", "b"])
        self.assertEqual(view.offset, 0)


class PoolTest(unittest.TestCase):
    def test_active_rows_never_exceed_pool_size(self):
        view = ListView(20, 60, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        for offset in (0, 60, 120, 180, 40):
            view.scroll_to(offset)
            view.render()
            self.assertLessEqual(view.active_rows(), 3)
        self.assertEqual(view.active_rows(), 3)

    def test_scrolled_out_rows_are_reused(self):
        view = ListView(20, 60, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        view.scroll_to(0)
        view.render()
        self.assertEqual(view.reuse_count(), 0)
        view.scroll_to(60)
        view.render()
        self.assertEqual(view.reuse_count(), 3)

    def test_set_items_recycles_old_rows(self):
        view = ListView(20, 60, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        view.render()
        view.set_items(["x", "y"])
        self.assertEqual(view.active_rows(), 0)
        self.assertEqual(view.visible(), [(0, "x"), (1, "y")])


class InvariantTest(unittest.TestCase):
    def test_same_scroll_sequence_is_deterministic(self):
        def run():
            view = ListView(20, 60, 3)
            view.set_items(["i-%d" % index for index in range(50)])
            out = []
            for offset in (0, 25, 60, 13, 200, 0):
                view.scroll_to(offset)
                out.append(view.visible())
            return out

        self.assertEqual(run(), run())

    def test_scanned_does_not_grow_with_item_count(self):
        small = ListView(20, 60, 3)
        small.set_items(["i"] * 100)
        small.visible()
        big = ListView(20, 60, 3)
        big.set_items(["i"] * 100000)
        big.visible()
        self.assertEqual(small.scanned_count(), big.scanned_count())


if __name__ == "__main__":
    unittest.main()
