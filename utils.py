import pandas as pd
import math
import numpy as np


class Parser:
    def __init__(self, constraints, obj_function):
        self.minimize = "min" in obj_function
        self.object = obj_function
        self.constraints = constraints

    # Выведем матрицы задачи лп: Ax <= b, cx -> extr
    def get_matrixes(self):
        A = []
        b = []
        expression_lines = self.constraints.split(',')
        for line in expression_lines:
            coefficients, value = self.get_coefficients(line)
            A.append(coefficients)
            b.append(value)
        coefficients, value = self.get_coefficients(self.object)
        c = coefficients
        return A, b, c, self.minimize

    def get_coefficients(self, constr):
        if '>=' in constr:
            sp = constr.split('>=')
            return self.parse_exp(sp[0], True), -float(sp[1])
        if '<=' in constr:
            sp = constr.split('<=')
            return self.parse_exp(sp[0], False), float(sp[1])
        if '=' in constr:
            sp = constr.split('=')
            return self.parse_exp(sp[0], False), float(sp[1])
        return self.parse_exp(constr, False), 0

    @staticmethod
    def parse_exp(exp, transform):
        sp = exp.split('+')
        coefficients = []
        for s in sp:
            coefficients.append(float(s.split('x')[0]))
        if transform:
            return [coeff * -1 for coeff in coefficients]
        return coefficients


class TableauUtils:
    # Приводим к удобному для вычислений виду
    # Получаем матрицу со столбцами: базис, b, A
    # 1 строка матрицы - оптимизируемая функция tableau[0, 0] = None, tableau[0, 1] = 0
    def get_initial_tableau(self, A, b, c, minimize):
        base_vars = len(c)
        artificial_vars = len(A)

        objective = np.hstack(([None], [0], [0] * base_vars, [0] * artificial_vars))

        basis = [base_vars + i + 1 for i in range(artificial_vars)]

        if artificial_vars + base_vars != len(A[0]):
            B = np.identity(artificial_vars)
            A = np.hstack((A, B))

        body = np.hstack((np.transpose([basis]), np.transpose([b]), A))

        tableau = np.vstack((objective, body))

        for i in range(1, len(tableau[0]) - artificial_vars):
            for j in range(1, len(tableau)):
                if minimize:
                    tableau[0, i] -= tableau[j, i]
                else:
                    tableau[0, i] += tableau[j, i]

        tableau = np.array(tableau, dtype='float')
        return tableau, base_vars

    # Выводим искуственные переменные из таблички
    def remove_redundant_variables(self, tableau, base_vars):
        artificial_idx = []
        tableau = np.delete(tableau, obj=np.s_[2 + base_vars:], axis=1)
        for i in range(1, len(tableau)):
            if tableau[i, 0] >= base_vars:

                redundant = True
                for j in range(2, base_vars + 2):
                    if tableau[i, j] != 0:
                        redundant = False
                        break
                artificial_idx.append([i, redundant])

        for key in artificial_idx:
            index, redundant = key
            if redundant:
                tableau = np.delete(tableau, obj=index, axis=0)
                artificial_idx.remove(key)
            else:
                n = -1
                for i in range(2, len(tableau[0]) - 1):
                    if tableau[index, i] != 0:
                        n = i
                        break
                tableau = pivot(tableau, index, n)

        return tableau

    # Восстанавливаем оптимизируемую функцию в табличке
    def restore_tableau(self, tableau, base_vars, minimize):
        for i in range(0, base_vars - 1):
            tableau[0, i + 2] = base_vars
        tableau[0, 1] = 0
        a = np.empty(0)
        for value in tableau[0, 1:]:
            a = np.append(a, value)

        for j in range(1, len(tableau)):
            for i in range(1, len(tableau[0])):
                if minimize:
                    a[i - 1] -= tableau[0, int(tableau[j, 0] + 2)] * tableau[j, i]
                else:
                    a[i - 1] += tableau[0, int(tableau[j, 0] + 2)] * tableau[j, i]

        tableau[0, 1:] = a
        return tableau


# Пересчитываем табличку
def pivot(tableau, r, n):
    pivot = tableau[r, n]
    tableau[r, 1:] = tableau[r, 1:] / pivot
    for i in range(0, len(tableau)):
        if i != r:
            tableau[i, 1:] = tableau[i, 1:] - tableau[i, n] / tableau[r, n] * tableau[r, 1:]
    return tableau