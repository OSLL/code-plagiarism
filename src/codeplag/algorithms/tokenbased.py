import binascii


def generate_unique_ngrams(tokens, n=3):
    """The function returns a set of N-grams
    and may use to generate shingles.

    @param tokens - list of tokens
    @param n - count of elements in sequences
    """

    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def generate_ngrams(tokens, n=3):
    """The function returns a list of N-grams
    and may use to generate shingles.

    @param tokens - list of tokens
    @param n - count of elements in sequences
    """

    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def generate_ngrams_and_hashit(tokens, n=3):
    """The function generates and hashes ngrams
    which gets from the tokens sequence.

    @param tokens - list of tokens
    @param n - count of elements in sequences
    """

    return [binascii.crc32(bytearray(tokens[i:i + n]))
            for i in range(len(tokens) - n + 1)]


def hashes_compair(hashed_sequence1, hashed_sequence2):
    """The function does a simple check how the same
    two sequences of hashes.

    @param - the first sequence of hashes
    @param - the second sequence of hashes
    """

    same = 0
    fcount = len(hashed_sequence1)
    scount = len(hashed_sequence2)
    if fcount * scount == 0:
        return 0.0

    for i in range(fcount):
        if hashed_sequence1[i] in hashed_sequence2:
            same += 1

    return same * 2 / float(fcount + scount) * 100


def value_jakkar_coef(tokens_first, tokens_second, ngrams_length=3):
    '''
        The function returns the value of the Jakkar coefficient
        @param tokens_first - list of tokens of the first program
        @param tokens_second - list of tokens of the second program
    '''
    ngrams_first = generate_unique_ngrams(tokens_first, ngrams_length)
    ngrams_second = generate_unique_ngrams(tokens_second, ngrams_length)

    intersection = len(ngrams_first.intersection(ngrams_second))
    union = len(ngrams_first | ngrams_second)

    if union == 0:
        return 0.0

    return intersection / union


def lcs(X, Y):
    '''
        The function returns the length of the longest common subsequence
        of two sequences X and Y.
        @param X - list of tokens of the first program
        @param Y - list of tokens of the second program
    '''
    m = len(X)
    n = len(Y)

    if m == 0 or n == 0:
        return 0

    # m + 1 rows
    # n + 1 columns
    L = [[0] * (n + 1) for i in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1] + 1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])

    return L[m][n]


def lcs_based_coeff(tokens1, tokens2):
    """The function returns coefficient based on the length
    of the longest common subsequence of tokens.
    This coefficient describes how same two sequences of tokens.

    @param tokens1 - the first sequence of tokens
    @param tokens2 - the second sequnce of tokens
    """

    count_tokens1 = len(tokens1)
    count_tokens2 = len(tokens2)

    if (count_tokens1 * count_tokens2) == 0:
        return 0.0

    return ((2 * lcs(tokens1, tokens2)) / (count_tokens1 + count_tokens2))
