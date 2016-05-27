from collections import namedtuple
import operator


class LcsEmptyNode(object):
    __slots__ = ()
    @property
    def value(self):
        raise AttributeError

    @property
    def parent(self):
        return None

    @property
    def length(self):
        return 0

    def __bool__(self):
        return False

    def iter_reversed(self):
        return ()

LcsEmptyNode.INSTANCE = LcsEmptyNode()


class LcsNode(object):
    __slots__ = ('value', 'parent', 'length')

    def __init__(self, value, *parents):
        self.value = value
        self.parent = self.best(*parents)
        self.length = self.parent.length + 1 if self.parent else 1

    @classmethod
    def best(cls, *parents):
        best = None
        for parent in parents:
            if parent and (not best or parent.length > best.length):
                best = parent
        return best

    def iter_reversed(self):
        node = self
        while node:
            yield node.value
            node = node.parent


def longest_common_subsequence(a, b, equals=operator.eq):
    """Longest common subsequence of two sequences

    Finds the longest common subsequence of sequences ``a`` and ``b``,
    then returns index pairs of identical elements in each sequence.

    :param a: First sequence
    :param b: Second sequence
    :return: List of pairs of indices to equal elements

    >>> longest_common_subsequence(
    ... [1, 2, 3,    5, 6,    8, 9,],
    ... [   2, 3, 4, 5,    7, 8,   ])
    [(1, 0), (2, 1), (3, 3), (5, 5)]
    """
    # Adapted from http://stackoverflow.com/a/24547864/1115497

    table = [[LcsEmptyNode.INSTANCE] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            table[i+1][j+1] = (
                LcsNode((i, j), table[i][j]) if equals(ca, cb) else
                LcsNode.best(table[i+1][j], table[i][j+1])
            )

    best = list(table[-1][-1].iter_reversed())
    best.reverse()
    return best


def make_lists_equal(
        goal, current,
        equals=operator.eq,
        insert=None, delete=None, append=None,
        failure={},
):
    """Attempts to make two lists equal by performing the minimal number of operations.

    This takes two lists, and then tries to perform the minimal number of atomic
    operations to make them the "same".  The point of this method is that one of the
    "lists" may actually represent a remote resource and we want to minimize number
    of API calls to make it equal to the goal list.

    :param goal: goal list
    :param current: list that needs to change
    :param equals: if a value == b value
    :param insert: (index, a value) -> inserts into b
    :param delete: (index, b value) -> deletes from b
    :param append: (a value) -> appends to end of b

    >>> a = [1, 2, 3,    5, 6,    8, 9,]
    >>> b = [   2, 3, 4, 5,    7, 8,   ]
    >>> make_lists_equal(a, b, insert=b.insert, delete=(lambda i, v: b.__delitem__(i)), append=b.append)
    >>> b
    [1, 2, 3, 5, 6, 8, 9]

    >>> c = [   2, 3, 4, 5,    7, 8,   ]
    >>> make_lists_equal(a, c, insert=c.insert, delete=(lambda i, v: c.__delitem__(i)), append=None)
    >>> c
    [1, 2, 3, 5, 6, 8, 9]
    """
    a, b = goal, current
    lcs = longest_common_subsequence(a, b, equals)
    len_b = len(b)

    # First insert & delete anything before the last shared item
    # (in reverse order, so indices are preserved)
    if lcs:
        lcs.reverse()
        li, lj = lcs[0]
        for i, j in lcs[1:] + [(-1, -1)]:
            for dj in range(lj-1, j, -1):
                if delete(dj, b[dj]) is not failure:
                    len_b -= 1
            for ii in range(li-1, i, -1):
                if insert(j+1, a[ii]) is not failure:
                    len_b += 1
            li, lj = i, j
    else:
        for dj in range(len_b-1, -1, -1):
            if delete(dj, b[dj]) is not failure:
                len_b -= 1

    # Now append to end
    first = lcs[0][0]+1 if lcs else 0  # First new index on a
    for i in range(first, len(a)):
        result = append(a[i]) if append else insert(len_b, a[i])
        if result is not failure:
            len_b += 1


def unique(objs, key=None):
    """Yields unique values from an iterable."""
    hashable_objs = set()
    unhashable_objs = list()
    for obj in objs:
        objkey = key(obj) if key else obj
        try:
            hash(objkey)
        except TypeError:  # Unhashable type
            if objkey not in unhashable_objs:
                unhashable_objs.append(objkey)
                yield obj
        else:  # Hashable type
            if objkey not in hashable_objs:
                hashable_objs.add(objkey)
                yield obj


if __name__ == "__main__":
    import doctest
    doctest.testmod()
