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
    def test_exact_rows_when_viewport_aligns(self):
        view = ListView(20, 100, 6)
        view.set_items(["i-%d" % index for index in range(10)])
        self.assertEqual(len(view.visible()), 5)

    def test_partial_row_counts_as_a_row(self):
        view = ListView(20, 101, 8)
        view.set_items(["i-%d" % index for index in range(10)])
        self.assertEqual(len(view.visible()), 6)

    def test_no_extra_row_beyond_viewport(self):
        view = ListView(20, 100, 8)
        view.set_items(["i-%d" % index for index in range(10)])
        self.assertEqual([index for index, _ in view.visible()], [0, 1, 2, 3, 4])

    def test_unaligned_offset_covers_viewport(self):
        view = ListView(20, 100, 8)
        view.set_items(["i-%d" % index for index in range(50)])
        view.scroll_to(10)
        self.assertEqual([index for index, _ in view.visible()],
                         [0, 1, 2, 3, 4, 5])

    def test_indices_strictly_increasing(self):
        view = ListView(20, 100, 8)
        view.set_items(["i-%d" % index for index in range(50)])
        view.scroll_to(37)
        indices = [index for index, _ in view.visible()]
        self.assertEqual(indices, sorted(indices))
        self.assertEqual(len(indices), len(set(indices)))

    def test_window_stops_at_end_of_items(self):
        view = ListView(20, 100, 8)
        view.set_items(["a", "b", "c"])
        self.assertEqual([index for index, _ in view.visible()], [0, 1, 2])


class ClampTest(unittest.TestCase):
    def test_scroll_beyond_end_clamps_to_zero_when_list_short(self):
        view = ListView(20, 100, 3)
        view.set_items(["a", "b", "c"])
        view.scroll_to(500)
        self.assertEqual(view.offset, 0)
        self.assertEqual(len(view.visible()), 3)

    def test_scroll_negative_clamps_to_zero(self):
        view = ListView(20, 100, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        view.scroll_to(-50)
        self.assertEqual(view.offset, 0)

    def test_scroll_clamps_to_max_offset(self):
        view = ListView(20, 100, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        view.scroll_to(10 ** 9)
        self.assertEqual(view.offset, 100 * 20 - 100)

    def test_set_items_clamps_existing_offset(self):
        view = ListView(20, 100, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        view.scroll_to(1000)
        view.set_items(["a", "b"])
        self.assertEqual(view.offset, 0)


class PoolTest(unittest.TestCase):
    def test_active_never_exceeds_pool_size(self):
        view = ListView(20, 60, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        for offset in (0, 60, 120, 180, 240):
            view.scroll_to(offset)
            view.render()
            self.assertLessEqual(view.active_rows(), 3)

    def test_scrolled_out_rows_are_reused(self):
        view = ListView(20, 60, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        view.scroll_to(0)
        view.render()
        view.scroll_to(60)
        view.render()
        self.assertEqual(view.active_rows(), 3)
        self.assertEqual(view.reuse_count(), 3)

    def test_set_items_recycles_all_old_rows(self):
        view = ListView(20, 60, 3)
        view.set_items(["i-%d" % index for index in range(100)])
        view.render()
        view.set_items(["x", "y"])
        self.assertEqual(view.active_rows(), 0)
        self.assertEqual([index for index, _ in view.visible()], [0, 1])
        view.render()
        self.assertLessEqual(view.active_rows(), 3)


class InvariantTest(unittest.TestCase):
    def test_same_scroll_sequence_gives_same_result(self):
        def run():
            view = ListView(20, 60, 3)
            view.set_items(["i-%d" % index for index in range(100)])
            out = []
            for offset in (0, 40, 80, 20, 0, 100):
                view.scroll_to(offset)
                out.append(view.visible())
            return out

        self.assertEqual(run(), run())

    def test_scanned_does_not_grow_with_item_count(self):
        small = ListView(20, 60, 3)
        small.set_items(["i-%d" % index for index in range(100)])
        big = ListView(20, 60, 3)
        big.set_items(["i-%d" % index for index in range(100000)])
        for _ in range(100):
            small.visible()
            big.visible()
        self.assertEqual(small.scanned_count(), big.scanned_count())

    def test_visible_at_scale_stays_window_sized(self):
        view = ListView(20, 60, 3)
        view.set_items(["i-%d" % index for index in range(100000)])
        for _ in range(100000):
            view.scroll_to(view.offset + 20 if view.offset < view.max_offset() else 0)
            self.assertLessEqual(len(view.visible()), 3)


if __name__ == "__main__":
    unittest.main()
