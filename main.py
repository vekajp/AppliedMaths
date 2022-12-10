from utils import ParserTaskToTable

file = open("src/input.txt")
obj_func = file.readline()
constraints = file.readline()

parser = ParserTaskToTable(constraints, obj_func)
print(parser.to_dataframe())