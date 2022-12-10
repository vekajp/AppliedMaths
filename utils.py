import pandas as pd
import math
import numpy as np


class ParserTaskToTable:
    def __init__(self, constraints, obj_function):
        self.table = self.parse_to_table(constraints, obj_function.split('->')[0])
        self.vars = len(self.table[0])
        self.eq = len(self.table)
        self.minimize = "min" in obj_function

    def parse_to_table(self, constraints, obj_function):
        expression_lines = constraints.split(',')
        constraint_expressions_eq = []
        constraint_expressions_not_eq = []
        coefficients, value, equals = self.get_coefficients(obj_function)
        obj_func = Expression(coefficients, value, equals)
        base_vars = len(obj_func.coefficients)
        additional = 0
        for line in expression_lines:
            coefficients, value, equals = self.get_coefficients(line)
            coefficients = [c * math.copysign(1, value) for c in coefficients]
            value = value * math.copysign(1, value)
            if not equals:
                additional += 1
                constraint_expressions_not_eq.append(Expression(coefficients, value, equals))
            else:
                constraint_expressions_eq.append(Expression(coefficients, value, equals))
        table = []
        i = base_vars + 1
        for exp in constraint_expressions_eq:
            table.append(exp.coefficients + [0] * additional + [exp.value] + [i])
            i += 1
        var_n = base_vars
        for exp in constraint_expressions_not_eq:
            tmp = exp.coefficients + [0] * additional + [exp.value] + [i]
            i += 1
            if var_n < len(tmp):
                tmp[var_n] = 1
                var_n += 1
            table.append(tmp)

        table.append(obj_func.coefficients + [0] * additional + [obj_func.value] + [None])
        return table

    def get_coefficients(self, constr):
        if '>=' in constr:
            sp = constr.split('>=')
            return self.parse_exp(sp[0], True), -float(sp[1]), False
        if '<=' in constr:
            sp = constr.split('<=')
            return self.parse_exp(sp[0], False), float(sp[1]), False
        if '=' in constr:
            sp = constr.split('=')
            return self.parse_exp(sp[0], False), float(sp[1]), True
        return self.parse_exp(constr, False), 0, True

    @staticmethod
    def parse_exp(exp, transform):
        sp = exp.split('+')
        coefficients = []
        for s in sp:
            coefficients.append(float(s.split('x')[0]))
        if transform:
            return [coeff * -1 for coeff in coefficients]
        return coefficients

    def to_dataframe(self):
        columns = ["x_" + str(i + 1) for i in range(self.vars -2)] + ["z"] + ["basis"]
        return pd.DataFrame(self.table, columns=columns)


class Expression:
    def __init__(self, coefficients, value, equality):
        self.coefficients = coefficients
        self.value = value
        self.equality = equality