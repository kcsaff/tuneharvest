from collections import namedtuple

Link = namedtuple('Link', ('media', 'context', 'service', 'itemid'))
Link.__new__.__defaults__ = (None,) * len(Link._fields)
