from unittest.mock import MagicMock
import pytest
import numpy as np

from codeplag.featurecache import serialize_feratures_to_dict, deserialize_feratures_from_dict
from codeplag.types import ASTFeatures
from codeplag.pyplag.utils import get_ast_from_filename, get_features_from_ast


CWD: Final[Path] = Path(os.path.dirname(os.path.abspath(__file__)))
FILEPATH1: Final[Path] = CWD / "./data/test1.py"


class TestSerialization:
    def test_serialize_deserialize_astfeatures(self):
        tree = get_ast_from_filename(FILEPATH1)
        assert tree
        features = get_features_from_ast(tree, FILEPATH1)
        unodes = 15
        features = ASTFeatures("example_path")
        serialized = serialize_feratures_to_dict(features)
        deserialized = deserialize_feratures_from_dict(serialized)


        assert features.count_of_nodes == 42
        assert features.operators == {"AugAssign": 2, "Add": 2, "AnnAssign": 1, "Assign": 1}
        assert features.keywords == {
            "FunctionDef": np.int64(1),
            "Return": np.int64(1),
            "If": np.int64(1),
        }
        assert features.literals == {
            # ast.Constant с python >= 3.8 use for all constants
            # before was NameConstant, Num and etc.
            "Constant": 6
        }
        assert len(features.unodes) == unodes
        assert len(features.from_num) == unodes
        assert features.count_unodes == np.int64(unodes)
        assert len(features.structure) == 42
        assert features.head_nodes == [
            "INT_CONST[1]",
            "INT_CONST[2]",
            "FLOAT_CONST[3]",
            "my_func[6]",
            "If[12]",
        ]
        assert features.sha256 == "f231b049ada761d534bb611cc7e92efdf8fd985d8092a72a132e79becff338d0"


        assert features.sha256 == deserialized.sha256
        assert features.count_of_nodes == deserialized.count_of_nodes
        assert features.head_nodes == deserialized.head_nodes
        assert features.operators == deserialized.operators
        assert features.keywords == deserialized.keywords
        assert features.literals == deserialized.literals
        assert features.unodes == deserialized.unodes
        assert features.from_num == deserialized.from_num
        assert features.count_unodes == deserialized.count_unodes
        assert features.structure == deserialized.structure
        assert features.tokens == deserialized.tokens
        assert features.tokens_pos == deserialized.tokens_pos