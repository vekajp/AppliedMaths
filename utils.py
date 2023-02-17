import json

import numpy as np
import pandas as pd


class Parser:
    def __init__(self, path):
        file = open(path)
        self.data = json.load(file)

    def get_tables(self):
        tables = []
        for i, task in enumerate(self.data):
            fun, minimize, constraints, start_point = task["objective_function"], task["minimize"], task["constraints"], \
                                                      task["start_point"]
            tables.append(Tableau(constraints, fun, start_point, minimize))
        return tables


class Tableau:
    def __init__(self, constraints, function, start_point, minimize):
        self.table = []
        self.start_point = start_point
        self.minimize = minimize
        self.__init_table(constraints, function)
        self.__reverse_constraints(constraints)
        self.__append_basis(constraints)
        self.__reverse_negative_right()
        self.row_n = len(self.table)
        self.col_n = len(self.table[0])
        self.args = len(function) - 1
        self.fun_coefficients = function[:-1]
        self.solvable = self.can_be_solved()

    def __init_table(self, constraints, fun):
        self.table = [[0] * (len(constraints[0]) - 1) for _ in range(len(constraints) + 1)]
        self.table[len(constraints)] = list(fun)
        for i in range(len(constraints)):
            for j in range(len(constraints[0]) - 1):
                if j < len(constraints[0]) - 2:
                    self.table[i][j] = constraints[i][j]
                elif j == len(constraints[0]) - 2:
                    self.table[i][j] = constraints[i][j + 1]

    def __reverse_constraints(self, constraints):
        for i in range(len(constraints)):
            if constraints[i][len(constraints[0]) - 2] == ">=":
                self.table[i] = list(np.array(self.table[i]) * (-1))

    def __append_basis(self, constraints):
        b = [self.table[i][-1] for i in range(len(constraints) + 1)]
        table = np.delete(self.table, -1, 1)
        count = 0
        for i in range(len(constraints)):
            if constraints[i][len(constraints[0]) - 2] != "=":
                count += 1
                new_column = np.zeros(len(constraints) + 1)
                new_column[i] = 1
                self.table = np.column_stack((table, new_column))

        if count != 0:
            self.table = np.column_stack((self.table, b))

    def __reverse_negative_right(self):
        for i in range(len(self.table)):
            if self.table[i][-1] < 0:
                self.table[i] = list(np.array(self.table[i]) * (-1))

    def print(self):
        index = [str(i + 1) for i in range(self.row_n - 1)] + ['z']
        columns = ['x_' + str(i + 1) for i in range(self.col_n - 1)] + ['y']
        df = pd.DataFrame(data=self.table, index=index, columns=columns)
        print(df)

    def make_step(self, row, col):
        new_table = [[0] * self.col_n for _ in range(self.row_n)]

        for j in range(self.col_n):
            new_table[row][j] = self.table[row][j] / self.table[row][col]

        for i in range(self.row_n):
            if i == row:
                continue

            for j in range(self.col_n):
                new_table[i][j] = self.table[i][j] - (self.table[row][j] / self.table[row][col]) * self.table[i][col]

        self.table = new_table

    def make_steps(self, rows, cols):
        for i in range(len(rows)):
            self.make_step(rows[i], cols[i])

    def find_main_column(self, basis):
        main_col = 0
        for j in range(self.col_n - 1):
            if list(basis.values()).count(j + 1) == 0 and self.table[self.row_n - 1][j] <= self.table[self.row_n - 1][main_col]:
                main_col = j
        return main_col

    def find_main_row(self, main_col, eps):
        main_row = -1
        for i in range(self.row_n - 1):
            if self.table[i][main_col] > eps:
                main_row = i
                break

        if main_row == -1:
            return -1

        for i in range(main_row + 1, self.row_n - 1):
            if self.table[i][main_col] > 0 and (
                    self.table[i][-1] / self.table[i][main_col] <
                    self.table[main_row][-1] / self.table[main_row][main_col]):
                main_row = i

        return main_row

    def can_be_solved(self):
        for i in range(self.row_n - 1):
            solvable = False
            for j in range(self.col_n - 1):
                if self.table[i][j] > 0:
                    solvable = True
                    break
            if not solvable:
                return False
        return True



