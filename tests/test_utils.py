from tuneharvest.utils import longest_common_subsequence, make_lists_equal
import unittest


class TestUtils(unittest.TestCase):

    def test_longest_common_subsequence(self):
        result = longest_common_subsequence(
            [1, 2, 3, 5, 6, 8, 9],
            [2, 3, 4, 5, 7, 8]
        )
        goal = [(1, 0), (2, 1), (3, 3), (5, 5)]
        self.assertEquals(goal, result)

    def test_make_lists_equal_with_append(self):
        a = [1, 2, 3, 5, 6, 8, 9]
        b = [2, 3, 4, 5, 7, 8]
        result = make_lists_equal(
            a, b, insert=b.insert, delete=(lambda i, v: b.__delitem__(i)), append=b.append
        )
        self.assertEquals(a, b)

        def test_make_lists_equal_without_append(self):
            a = [1, 2, 3, 5, 6, 8, 9]
            b = [2, 3, 4, 5, 7, 8]
            result = make_lists_equal(
                a, b, insert=b.insert, delete=(lambda i, v: b.__delitem__(i)), append=None
            )
            self.assertEquals(a, b)

if __name__ == '__main__':
    unittest.main()
