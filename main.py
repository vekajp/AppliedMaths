from simplex import *
from utils import *

parser = Parser("src/input.txt")
tables = parser.get_tables()
solver = SimplexSolver(verbose=False)
count = 1
for table in tables:
    print("Task no", count)
    print("+++++++++++++++++++++++++++")
    result = solver.solve(table)
    if result is not None:
        print("f =", round(result[0], 3))
        print("X = " + str(np.round(result[1], 3)) + ".T")
    print("+++++++++++++++++++++++++++\n")
    count += 1
