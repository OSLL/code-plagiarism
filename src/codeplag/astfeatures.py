from numba.typed import List, Dict
from numba.core import types


class ASTFeatures:
    def __init__(self, filepath=''):
        self.filepath = filepath

        self.count_of_nodes = 0
        self.head_nodes = List(['tmp'])
        self.head_nodes.clear()
        self.operators = Dict.empty(key_type=types.unicode_type,
                                    value_type=types.int64)
        self.keywords = Dict.empty(key_type=types.unicode_type,
                                   value_type=types.int64)
        self.literals = Dict.empty(key_type=types.unicode_type,
                                   value_type=types.int64)

        # unique nodes
        self.unodes = Dict.empty(key_type=types.unicode_type,
                                 value_type=types.int64)
        self.from_num = Dict.empty(key_type=types.int64,
                                   value_type=types.unicode_type)
        self.count_unodes = 0

        self.structure = List([(1, 2)])
        self.structure.clear()
        self.tokens = List([1])
        self.tokens.clear()
