import os
from clang.cindex import Cursor, TokenKind
from codeplag.cplag.const import IGNORE, OPERATORS
from codeplag.astfeatures import ASTFeatures


# Tested
def get_not_ignored(tree, src):
    '''
        Function helps to discard unnecessary nodes such as imports
        @param tree - clang.cindex.Cursor object
        @param src - str path to file
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


# Tested
def get_count_of_nodes(tree):
    '''
        Get count of nodes of tree without head
        @param tree - clang.cindex.Cursor object
    '''
    if(not hasattr(tree, 'get_children')):
        return TypeError

    count = 0
    children = list(tree.get_children())
    length = len(children)
    count += length
    for i in range(length):
        count += get_count_of_nodes(children[i])

    return count


def getn_count_nodes(len_min, len_max, indexes, axis, children):
    '''
        Function return count of not accounted nodes
        @param len_min - length of less node
        @param len_max - length of longer node
        @param indexes - indexes of metrics taken into account list of tuples
        @param axis - if 0 then iteration on row
        if 1 then iteration on column
        @param children - list of nodes of type clang.cindex.Cursor object
    '''
    add = [indexes[i][axis] for i in range(len_min)]

    count = 0
    for i in range(len_max):
        if i not in add:
            count += get_count_of_nodes(children[i]) + 1

    return count


def generic_visit(node, features, curr_depth=0):
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

    if len(children) == 0:
        for token in node.get_tokens():
            token_name = repr(token.kind)
            if token_name not in features.unodes:
                features.unodes[token_name] = features.count_unodes
                features.from_num[features.count_unodes] = token_name
                features.count_unodes += 1
            features.structure.append((curr_depth,
                                       features.unodes[token_name]))
    else:
        for child in children:
            features.tokens.append(child.kind.value)
            generic_visit(child, features, curr_depth + 1)


def get_features(tree, filepath=''):
    features = ASTFeatures(filepath)
    for token in tree.get_tokens():
        if (token.kind == TokenKind.PUNCTUATION and
            token.spelling in OPERATORS):
            if token.spelling not in features.operators:
                features.operators[token.spelling] = 1
            else:
                features.operators[token.spelling] += 1
            features.operators_sequence.append(token.spelling)
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
