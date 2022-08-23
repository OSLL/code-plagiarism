from typing import List

from clang.cindex import Cursor, TokenKind

from codeplag.astfeatures import ASTFeatures
from codeplag.cplag.const import IGNORE, OPERATORS


# TODO: iterate by iterotor retruned by tree.get_children()
def get_not_ignored(tree: Cursor, src: str) -> List[Cursor]:
    '''
        Function helps to discard unnecessary nodes such as imports
    '''

    children = list(tree.get_children())
    length = len(children)
    parsed_nodes = []
    for i in range(length):
        loc = children[i].location.file
        if (str(loc).split('/')[-1] == src.split('/')[-1]
           and children[i].kind not in IGNORE):
            parsed_nodes.append(children[i])

    return parsed_nodes


def generic_visit(node, features: ASTFeatures, curr_depth: int = 0) -> None:
    if curr_depth == 0:
        children = get_not_ignored(node, features.filepath)
    else:
        node_name = repr(node.kind)
        if node_name not in features.unodes:
            features.unodes[node_name] = features.count_unodes
            features.from_num[features.count_unodes] = node_name
            features.count_unodes += 1
        features.structure.append((curr_depth,
                                   features.unodes[node_name]))
        children = list(node.get_children())

        if curr_depth == 1:
            features.head_nodes.append(node.spelling)

    if len(children) == 0:
        for token in node.get_tokens():
            token_name = repr(token.kind)
            if token_name not in features.unodes:
                features.unodes[token_name] = features.count_unodes
                features.from_num[features.count_unodes] = token_name
                features.count_unodes += 1
            features.structure.append((curr_depth,
                                       features.unodes[token_name]))

            if curr_depth == 1:
                features.head_nodes.append(token_name)

    else:
        for child in children:
            features.tokens.append(child.kind.value)
            generic_visit(child, features, curr_depth + 1)


def get_features(tree: Cursor, filepath: str = '') -> ASTFeatures:
    features = ASTFeatures(filepath)
    for token in tree.get_tokens():
        if (token.kind == TokenKind.PUNCTUATION and
           token.spelling in OPERATORS):
            if token.spelling not in features.operators:
                features.operators[token.spelling] = 1
            else:
                features.operators[token.spelling] += 1
        if (token.kind == TokenKind.KEYWORD):
            if token.spelling not in features.keywords:
                features.keywords[token.spelling] = 1
            else:
                features.keywords[token.spelling] += 1
        if (token.kind == TokenKind.LITERAL):
            if token.spelling not in features.literals:
                features.literals[token.spelling] = 1
            else:
                features.literals[token.spelling] += 1

    generic_visit(tree, features)

    return features
