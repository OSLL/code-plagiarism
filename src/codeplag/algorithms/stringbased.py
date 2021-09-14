import numpy as np


class LevenshteinDistance:
    def __init__(self, sequence1, sequence2):
        self.sequence1 = sequence1
        self.sequence2 = sequence2
        self.s1_length = len(sequence1)
        self.s2_length = len(sequence2)
        self.distance = -1
        self.distance_matrix = np.zeros((self.s1_length + 1,
                                         self.s2_length + 1),
                                        dtype=np.int64)

    @staticmethod
    def m(symbol1, symbol2):
        '''
            The function returns 0 if symbol1 is equal symbol2
            else returns 1
        '''
        return 0 if symbol1 == symbol2 else 1

    def calculate_distance_matrix(self):
        '''
            The function calculates the Levenshtein matrix and sets
            in the distance atribute minimal count of operations
            needed for converting the first sequence to the second.
        '''
        for i in range(self.s1_length + 1):
            self.distance_matrix[i][0] = i
        for j in range(self.s2_length + 1):
            self.distance_matrix[0][j] = j

        for row in np.arange(1, self.s1_length + 1):
            for column in np.arange(1, self.s2_length + 1):
                symbol1 = self.sequence1[row - 1]
                symbol2 = self.sequence2[column - 1]
                minimum = min(self.distance_matrix[row - 1][column] + 1,
                              self.distance_matrix[row][column - 1] + 1,
                              self.distance_matrix[row - 1][column - 1]
                              + self.m(symbol1, symbol2))
                self.distance_matrix[row][column] = minimum

        self.distance = self.distance_matrix[self.s1_length][self.s2_length]

    def get_similarity_value(self):
        '''
            If the distance attribute had been calculated in the calculate
            method then the function returns similarity of two sequences
            else returns -1
        '''
        if self.distance == -1:
            self.calculate_distance_matrix()

        return 1.0 - self.distance / max(self.s1_length, self.s2_length)
