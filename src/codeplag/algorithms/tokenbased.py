from numba import njit


def generate_unique_ngrams(tokens, n=3):
    '''
        The function returns a set of N-grams.
        @param tokens - list of tokens
        @param n - count of elements in sequences
    '''
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def value_jakkar_coef(tokens_first, tokens_second):
    '''
        The function returns the value of the Jakkar coefficient
        @param tokens_first - list of tokens of the first program
        @param tokens_second - list of tokens of the second program
    '''
    ngrams_first = generate_unique_ngrams(tokens_first, 3)
    ngrams_second = generate_unique_ngrams(tokens_second, 3)

    intersection = len(ngrams_first.intersection(ngrams_second))
    union = len(ngrams_first | ngrams_second)

    if union == 0:
        return 0.0

    return intersection / union


@njit(fastmath=True)
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


@njit(fastmath=True)
def lcs_based_coeff(tokens1, tokens2):
    return ((2 * lcs(tokens1, tokens2)) / (len(tokens1) + len(tokens2)))
