import numpy as np
import pandas as pd
from utils import *


class Simplex:
    def __init__(self, constraints, objective):
        self.constraints = constraints
        self.objective = objective
        self.minimize = "min" in objective
        # Предполагаем что задача не решена, но может быть решенной.
        self.bounded = True
        self.feasible = False

    def optimize(self):
        # Получаем матрицы из ввода
        A, b, c, minimize = Parser(self.constraints, self.objective).get_matrixes()
        # Соединяем матрицы в табличку для вычислений
        tableau, base_vars = TableauUtils().get_initial_tableau(A, b, c, self.minimize)
        # Оптимизируем
        try:
            tableau = self.simplex(tableau)
        except Exception as e:
            print(e.args)
            return None, []

        # Убираем переменные, которые добавили для приведения задачи к каноническому ввиду
        tableau = TableauUtils().remove_redundant_variables(tableau, base_vars)

        # Восстанавливаем оптимизируемую функцию в абличке
        tableau = TableauUtils().restore_tableau(tableau, base_vars, minimize)

        # Снова оптимизируем
        try:
            tableau = self.simplex(tableau)
        except Exception as e:
            print(e.args)
            return None, []

        # Собираем ответ
        x = np.array([0] * len(c), dtype=float)
        for key in range(1, (len(tableau))):
            if tableau[key, 0] < len(c):
                x[int(tableau[key, 0])] = tableau[key, 1]

        ans = round(x.dot(c), 3)
        return x, ans

    def simplex(self, tableau):
        while True:
            optimal = self.optimal(tableau)
            if optimal:
                break
            row, column = self.pivot_index(tableau)
            for element in tableau[1:, column]:
                if element != 0:
                    self.bounded = True
            if not self.bounded:
                raise Exception("Unbounded")

            tableau = pivot(tableau, row, column)
            tableau[row, 0] = column - 2
        return tableau

    # Оптимальный элемент для ввода в базис
    def pivot_index(self, tableau):
        if self.minimize:
            column = tableau[0, 2:].tolist().index(np.amin(tableau[0, 2:])) + 2
        else:
            column = tableau[0, 2:].tolist().index(np.amax(tableau[0, 2:])) + 2
        minimum = 1000000
        row = -1
        for i in range(1, len(tableau)):
            if tableau[i, column] > 0:
                val = tableau[i, 1] / tableau[i, column]
                if val < minimum:
                    minimum = val
                    row = i
        return row, column

    # Проверяем, можно ли еще оптимизировать
    def optimal(self, tableau):
        if not self.minimize:
            return np.max(tableau[0, 2:]) <= 0
        else:
            return np.min(tableau[0, 2:]) >= 0
