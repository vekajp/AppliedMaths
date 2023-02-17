from utils import *
import itertools


class SimplexSolver:
    def __init__(self, eps=1e-8, max_iter=1000, verbose=False):
        self.eps = eps
        self.max_iter = max_iter
        self.verbose = verbose
        self.basis = None
        self.tableau = None

    def solve(self, table: Tableau):
        if not table.solvable:
            print("No solution")
            return [None, None]

        self.tableau = table
        self.get_first_plan(table.start_point)

        if self.basis is None:
            return None

        return self.find_solution()

    def get_first_plan(self, start_point):
        if self.verbose:
            print("Try to get first plan:")

        if start_point is None:
            self.basis = self.find_first_basis()
        else:
            self.basis = self.compose_basis(start_point)

    def find_first_basis(self):
        basis = {}
        for i in range(self.tableau.row_n - 1):
            try:
                idx = list(self.tableau.table[i][:-1]).index(1) + 1
            except ValueError:
                idx = 0
            if idx == 0 or list(basis.values()).count(idx) > 0:
                idx = 0
                for j in range(self.tableau.col_n - 1):
                    el = self.tableau.table[i][j]
                    if el > 0 and list(basis.values()).count(j + 1) == 0:
                        idx = j + 1
                        break
            basis[i] = idx
            self.adjust_table_to_basis(i, idx - 1)
        return basis

    def compose_basis(self, start_point):
        basis = {}
        basis_pos = {}
        for i in range(len(start_point)):
            col = i
            if start_point[i] > 0:
                basis_pos[i] = set()
                for j in range(self.tableau.row_n - 1):
                    if list(basis.keys()).count(j) == 0 and self.tableau.table[j][col] > 0:
                        basis_pos[i].add(j)
                if len(basis_pos[i]) == 0:
                    print("No solution")
                    return None

        return self.select_basis(basis_pos)

    def select_basis(self, basis_pos):
        product = itertools.product(*basis_pos.values())
        columns = list(basis_pos.keys())
        basis_pos = []
        for basis in product:
            if self.basis_is_fine(basis):
                basis_pos.append(basis)

        for pos in basis_pos:
            rows = list(pos)
            basis = {}
            for i in range(len(columns)):
                basis[rows[i]] = columns[i] + 1
            if self.basis_is_valid(basis):
                return basis

        return None

    def adjust_table_to_basis(self, row, col, value=1):
        el = self.tableau.table[row][col]
        if el != 1 and col != -1:
            self.tableau.table[row] = [j / el / value for j in self.tableau.table[row]]

        if col != -1:
            for j in range(self.tableau.row_n - 1):
                if j == row:
                    continue
                if self.tableau.table[j][col] != 0:
                    div = self.tableau.table[j][col] / el
                    sustr = [k * div for k in self.tableau.table[row]]
                    res = [self.tableau.table[j][k] - sustr[k] for k in range(len(sustr))]
                    self.tableau.table[j] = res
                    self.tableau.table[j][col] = 0

    def find_solution(self):
        if self.verbose:
            print("Initial table:")
            self.tableau.print()
        iteration = 0
        while not self.time_to_stop(iteration):
            iteration += 1
            col = self.tableau.find_main_column(self.basis)
            row = self.tableau.find_main_row(col, self.eps)

            if row == -1:
                print("No solution")
                return [None, None]

            if self.verbose:
                print("Pivot element: (" + str(row + 1) + ";" + str(col + 1) + ")")

            self.basis[row] = col + 1

            self.tableau.make_step(row, col)
            if self.verbose:
                self.tableau.print()

        result = [0 for _ in range(self.tableau.args)]
        result_fun = 0
        for i in range(len(self.basis)):
            if self.basis[i] - 1 < self.tableau.args:
                result[self.basis[i] - 1] = self.tableau.table[i][-1]

        for i in range(len(result)):
            result_fun += self.tableau.fun_coefficients[i] * result[i]

        return [result_fun, np.round(result, 4)]

    def time_to_stop(self, iteration):
        if self.tableau.minimize:
            flag = np.min(self.tableau.table[-1][:-1]) >= 0
        else:
            flag = np.max(self.tableau.table[-1][:-1]) <= 0
        return flag or iteration >= self.max_iter

    @staticmethod
    def basis_is_fine(basis):
        for i in basis:
            if list(basis).count(i) != 1:
                return False
        return True

    def basis_is_valid(self, basis):
        table: Tableau = self.tableau
        columns = [x - 1 for x in list(basis.values())]
        table.make_steps(list(basis.keys()), columns)
        for i in basis.keys():
            if table.table[i][basis[i] - 1] <= 0:
                return False
        return True
