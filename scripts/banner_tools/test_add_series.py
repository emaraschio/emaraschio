"""python3 -m unittest discover -s scripts/banner_tools"""

import unittest

from add_series import place

STYLES = ["a", "b", "c", "d"]


def rotation(n):
    return [{"file": f"{STYLES[i % 4]}/{i:02d}.webp", "style": STYLES[i % 4]} for i in range(n)]


def new(count, style="new"):
    return [{"file": f"added/{style}-{i:02d}.webp", "style": style} for i in range(1, count + 1)]


class Place(unittest.TestCase):
    def test_what_was_already_shown_never_moves(self):
        items = rotation(40)
        result = place(items, new(6), today=9)
        self.assertEqual(result[:10], items[:10])
        self.assertEqual(len(result), 46)

    def test_one_new_banner_lands_in_the_middle_of_what_is_left_not_at_the_end(self):
        result = place(rotation(41), new(1), today=0)
        at = result.index(new(1)[0])
        self.assertTrue(18 <= at <= 23, at)

    def test_a_series_is_spread_evenly_and_does_not_end_the_rotation(self):
        result = place(rotation(101), new(4), today=0)
        at = [i for i, item in enumerate(result) if item["style"] == "new"]
        self.assertEqual(len(at), 4)
        gaps = [b - a for a, b in zip([0] + at, at + [len(result)])]
        self.assertTrue(max(gaps) - min(gaps) <= 3, gaps)
        self.assertNotEqual(at[-1], len(result) - 1)

    def test_no_two_banners_of_one_style_follow_each_other(self):
        result = place(rotation(60), new(8, style="a"), today=5)
        self.assertFalse([i for i in range(1, len(result)) if result[i]["style"] == result[i - 1]["style"]])

    def test_on_puts_it_on_that_day_and_later_banners_show_a_day_later(self):
        items = rotation(40)
        result = place(items, new(1), today=9, on=20)
        self.assertEqual(result[20]["style"], "new")
        self.assertEqual(result[:20], items[:20])
        self.assertEqual(result[21:], items[20:])

    def test_a_banner_not_shown_yet_can_be_moved_earlier(self):
        items = rotation(40) + new(1)
        result = place(items, new(1), today=9, on=15)
        self.assertEqual(len(result), 41)
        self.assertEqual(result[15]["style"], "new")
        self.assertEqual(result[-1], items[39])

    def test_a_banner_already_shown_is_not_moved(self):
        items = rotation(40)
        with self.assertRaises(SystemExit):
            place(items, [items[3]], today=9, on=20)

    def test_a_day_in_the_past_is_refused(self):
        with self.assertRaises(SystemExit):
            place(rotation(40), new(1), today=9, on=9)


if __name__ == "__main__":
    unittest.main()
