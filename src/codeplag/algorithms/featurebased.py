import numpy as np

DEFAULT_EMPTY_ARRAY = np.array([[[]]], dtype=np.int64)


def counter_metric(counter1, counter2):
    '''
        Function return how same operators or keywords or literals
        in two trees
        @param counter1 - dict object with counts of op or kw or list
        @param counter2 - dict object with counts of op or kw or list
    '''
    # if(type(counter1) is not dict or type(counter2) is not dict):
    #    return TypeError

    if len(counter1) == 0 and len(counter2) == 0:
        return 1.0

    percent_of_same = [0, 0]
    for key in counter1.keys():
        if key not in counter2:
            percent_of_same[1] += counter1[key]
            continue
        percent_of_same[0] += min(counter1[key],
                                  counter2[key])
        percent_of_same[1] += max(counter1[key],
                                  counter2[key])
    for key in counter2.keys():
        if key not in counter1:
            percent_of_same[1] += counter2[key]
            continue

    if percent_of_same[1] == 0:
        return 0.0

    return percent_of_same[0] / percent_of_same[1]


def op_shift_metric(ops1, ops2):
    '''
        Returns the maximum value of the operator match and the shift under
        this condition
        @param ops1 - sequence of operators of tree1
        @param ops2 - sequence of operators of tree2
    '''
    # if (type(ops1) is not list or type(ops2) is not list):
    #    return TypeError
    count_el_f = len(ops1)
    count_el_s = len(ops2)
    if count_el_f == 0 and count_el_s == 0:
        return 0, 1.0
    if count_el_f > count_el_s:
        ops1, ops2 = ops2, ops1
        count_el_f = len(ops1)
        count_el_s = len(ops2)

    y = np.zeros(count_el_s, dtype=np.float32)

    shift = 0
    while shift < count_el_s:
        counter = 0
        first_ind = 0
        second_ind = shift
        while first_ind < count_el_f and second_ind < count_el_s:
            if ops1[first_ind] == ops2[second_ind]:
                counter += 1
            first_ind += 1
            second_ind += 1
        count_all = count_el_f + count_el_s - counter
        if count_all != 0:
            y[shift] = counter / count_all

        shift += 1

    max_shift = 0
    for index in np.arange(1, len(y), 1):
        if y[index] > y[max_shift]:
            max_shift = index

    if len(y) > 0:
        return max_shift, y[max_shift]
    else:
        return 0, 0.0


def get_children_indexes(tree, count_of_nodes):
    """The function returns indexes of her children and their count.

    @param tree - a simple structure of the AST.
    @count_of_nodes - count of elements in the tree

    O(len(tree))
    """

    indexes = []
    count_of_children = 0

    if count_of_nodes != 0:
        current_level = tree[0][0]

    current_index = 0
    for node in tree:
        if current_level == node[0]:
            indexes.append(current_index)
            count_of_children += 1
        current_index += 1

    return indexes, count_of_children


def find_max_index(array):
    '''
        The function for finding index of max element in matrix
        @param array - matrix of compliance (np.ndarray object)

        rows = array.shape[0]
        columns = array.shpe[1]
        O(rows * columns)
    '''

    maximum = 0
    index = np.int64([0, 0])
    for i in np.arange(0, array.shape[0], 1):
        for j in np.arange(0, array.shape[1], 1):
            if array[i][j][1] == 0:
                continue
            value = array[i][j][0] / array[i][j][1]
            if value > maximum:
                maximum = value
                index[0] = i
                index[1] = j

    return index


def matrix_value(array):
    '''
        The function returns the value of the similarity of nodes
        from the compliance matrix.
        @param array - matrix of compliance (np.ndarray object)

        rows = array.shape[0]
        columns = array.shpe[1]
        O(min(rows, columns) * rows * columns)
    '''
    same_struct_metric = [1, 1]
    minimal = min(array.shape[0], array.shape[1])
    indexes = []
    for i in np.arange(0, minimal, 1):
        ind = find_max_index(array)
        indexes.append(ind)
        same_struct_metric[0] += array[ind[0]][ind[1]][0]
        same_struct_metric[1] += array[ind[0]][ind[1]][1]

        # Zeroing row
        for i in np.arange(0, array.shape[1], 1):
            array[ind[0]][i] = [0, 0]
        # Zeroing column
        for j in np.arange(0, array.shape[0], 1):
            array[j][ind[1]] = [0, 0]

    return same_struct_metric, indexes


def add_not_counted(tree, count_of_children, key_indexes, indexes, axis):
    """The function returns the count of nodes that didn't
    account in the previous step.

    @tree - part of structure
    @count_of_children - count of top-level nodes in the tree
    @key_indexes - indexes of top-level nodes in the tree
    @indexes - indexes of selected nodes which accounted in the metric
    @axis - 0 - row, 1 - column

    O(count_of_children * len(tree))
    """

    count = 0
    added = [index[axis] for index in indexes]
    for k in np.arange(0, count_of_children, 1):
        if k in added:
            continue
        else:
            part_of_tree = tree[key_indexes[k]:key_indexes[k + 1]]
            count += len(part_of_tree)

    return count


def struct_compare(tree1, tree2, matrix=DEFAULT_EMPTY_ARRAY):
    '''
        Function for compare structure of two trees
        @param tree1 - a simple structure of the first AST.
        @param tree2 - a simple structure of the second AST.
    '''

    count_of_nodes1 = len(tree1)
    count_of_nodes2 = len(tree2)

    if (count_of_nodes1 == 0 and count_of_nodes2 == 0):
        return [1, 1]
    elif (count_of_nodes1 == 0):
        return [1, (count_of_nodes2 + 1)]
    elif (count_of_nodes2 == 0):
        return [1, (count_of_nodes1 + 1)]

    # Add counting of nodes
    key_indexes1, count_of_children1 = get_children_indexes(tree1,
                                                            count_of_nodes1)
    key_indexes2, count_of_children2 = get_children_indexes(tree2,
                                                            count_of_nodes2)
    key_indexes1.append(count_of_nodes1)
    key_indexes2.append(count_of_nodes2)

    array = np.zeros((count_of_children1, count_of_children2, 2),
                     dtype=np.int64)

    for i in np.arange(0, count_of_children1, 1):
        for j in np.arange(0, count_of_children2, 1):
            section1 = tree1[key_indexes1[i] + 1:key_indexes1[i + 1]]
            section2 = tree2[key_indexes2[j] + 1:key_indexes2[j + 1]]
            array[i][j] = struct_compare(section1,
                                         section2)

    if matrix.size != 0:
        for i in np.arange(0, count_of_children1, 1):
            for j in np.arange(0, count_of_children2, 1):
                matrix[i][j] = array[i][j]

    same_struct_metric, indexes = matrix_value(array)
    if count_of_children1 > count_of_children2:
        same_struct_metric[1] += add_not_counted(tree1, count_of_children1,
                                                 key_indexes1, indexes,
                                                 axis=0)
    elif count_of_children2 > count_of_children1:
        same_struct_metric[1] += add_not_counted(tree2, count_of_children2,
                                                 key_indexes2, indexes,
                                                 axis=1)

    return same_struct_metric
