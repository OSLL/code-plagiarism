from pathlib import Path

from clang.cindex import Cursor, TokenKind

from codeplag.cplag.const import IGNORE, OPERATORS
from codeplag.getfeatures import set_sha256
from codeplag.types import ASTFeatures, NodeStructurePlace


def get_not_ignored(tree: Cursor, src: Path | str) -> list[Cursor]:
    """Function helps to discard unnecessary nodes such as imports."""
    parsed_nodes = []
    for child in tree.get_children():
        loc = child.location.file
        last_loc_part = str(loc).rsplit("/", maxsplit=1)[-1]
        last_src_part = str(src).rsplit("/", maxsplit=1)[-1]
        if last_loc_part == last_src_part and child.kind not in IGNORE:
            parsed_nodes.append(child)

    return parsed_nodes


def generic_visit(node: Cursor, features: ASTFeatures, curr_depth: int = 0) -> None:
    if curr_depth == 0:
        children = get_not_ignored(node, features.filepath)
    else:
        __add_node_to_structure(features, repr(node.kind), curr_depth)
        children = list(node.get_children())
        if curr_depth == 1:
            features.head_nodes.append(node.spelling)

    if len(children) == 0 and curr_depth == 1:
        for token in node.get_tokens():
            token_name = repr(token.kind)
            __add_node_to_structure(features, token_name, curr_depth)
            features.head_nodes.append(token_name)
    else:
        for child in children:
            features.tokens.append(child.kind.value)
            generic_visit(child, features, curr_depth + 1)


@set_sha256
def get_features(tree: Cursor, filepath: Path | str = "") -> ASTFeatures:
    features = ASTFeatures(filepath or tree.displayname)
    for token in tree.get_tokens():
        if token.kind == TokenKind.PUNCTUATION and token.spelling in OPERATORS:
            features.operators[token.spelling] += 1
        if token.kind == TokenKind.KEYWORD:
            features.keywords[token.spelling] += 1
        if token.kind == TokenKind.LITERAL:
            features.literals[token.spelling] += 1

    generic_visit(tree, features)

    return features


def __add_node_to_structure(
    features: ASTFeatures, node_name: str, curr_depth: int
) -> None:
    if node_name not in features.unodes:
        features.unodes[node_name] = features.count_unodes
        features.from_num[features.count_unodes] = node_name
        features.count_unodes += 1
    features.structure.append(
        NodeStructurePlace(curr_depth, features.unodes[node_name])
    )
