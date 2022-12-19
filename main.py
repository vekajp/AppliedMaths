from simplex import *

input_file = open("src/input.txt")
output_file = open("src/out.txt", 'w')
while input_file.readline():
    obj_func = input_file.readline()
    constraints = input_file.readline()
    simplex = Simplex(constraints, obj_func)
    x, ans = simplex.optimize()
    output_file.write(str(x) + '\n')
    output_file.write(str(ans) + '\n\n')
