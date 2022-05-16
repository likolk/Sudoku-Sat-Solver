#!/usr/bin/env python3
from subprocess import Popen
from subprocess import PIPE
import os

gbi = 0
varToStr = ["invalid"]

def printClause(cl):
    print(map(lambda x: "%s%s" % (x < 0 and eval("'-'") or eval("''"), varToStr[abs(x)]), cl))

def rowColNum(var_name):
    vars = var_name.split('(')[1][:-1].split(',')
    return int(vars[0]), int(vars[1]), int(vars[2])

def varName(row, column, number):
    return "inCell({},{},{})".format(row, column, number)

def gvi(name):
    global gbi
    global varToStr
    gbi += 1
    varToStr.append(name)
    return gbi

def gen_vars():
    varMap = {}
    # Insert here the code to add mapping from variable numbers to readable variable names.
    for row in range(1, 10):
        for column in range(1, 10):
            for number in range(1, 10):
                name = varName(row, column, number)
                varMap[name] = gvi(name)
    return varMap


def gen_box_constraints(vars, clauses, row, column):
    cells = [(row, column),   (row, column+1),   (row, column+2),
             (row+1, column), (row+1, column+1), (row+1, column+2),
             (row+2, column), (row+2, column+1), (row+2, column+2)]
    for n in range(1, 10):
        for i in range(9):
            for j in range(i+1, 9):
                clauses.append(
                    [-vars[varName(cells[i][0], cells[i][1], n)], -vars[varName(cells[j][0], cells[j][1], n)]]
                )


def gen_starting_sudoku_contraints(vars, clauses, sudoku):
    for i in range(9):
        for j in range(9):
            if 1 <= sudoku[i][j] <= 9:
                clauses.append([vars[varName(i+1, j+1, sudoku[i][j])]])


def read_sudoku(sudoku_file_name, print_sudoku=False):
    sudoku = []
    with open(sudoku_file_name, "r") as f:
        lines = f.readlines()
        assert len(lines) == 9
        for i in range(9):
            cells = lines[i].split(', ')
            assert len(cells) == 9
            row = []
            for j in range(9):
                if print_sudoku:
                    print(cells[j].strip(), end='  ')
                if cells[j].strip() == '_':
                    row.append(-1)
                    continue
                v = int(cells[j])
                assert 1 <= v <= 9
                row.append(v)
            if print_sudoku:
                print()
            sudoku.append(row)
    return sudoku


# sudoku must have -1 where the cell is empty
def gen_constraints(vars, sudoku_file_name='', sudoku=None):
    clauses = []
    # Each number cannot stay in the same row
    for n in range(1, 10):
        for r in range(1, 10):
            for c1 in range(1, 10):
                for c2 in range(c1+1, 10):
                    # number n cannot stay in cell (r, c1) and (r, c2) at the same time
                    clauses.append(
                        [-vars[varName(r, c1, n)], -vars[varName(r, c2, n)]]
                    )

    # Each number cannot stay in the same column
    for n in range(1, 10):
        for c in range(1, 10):
            for r1 in range(1, 10):
                for r2 in range(r1+1, 10):
                    clauses.append(
                        [-vars[varName(r1, c, n)], -vars[varName(r2, c, n)]]
                    )

    # Each number cannot stay in the same 3x3 box
    for i in range(3):
        for j in range(3):
            gen_box_constraints(vars, clauses, i*3+1, j*3+1)

    # Each cell must have a number in it
    for r in range(1, 10):
        for c in range(1, 10):
            clause = []
            for n in range(1, 10):
                clause.append(vars[varName(r, c, n)])
                # inCell(1, 1, 1) or inCell(1, 1, 2) or ... or inCell(1, 1, 9)
            clauses.append(clause)

    # The starting configuration is used to set constraints
    if sudoku is None:
        sudoku = read_sudoku(sudoku_file_name, print_sudoku=True)
    gen_starting_sudoku_contraints(vars, clauses, sudoku)
    return clauses

# A helper function to print the cnf header
def printHeader(n):
    global gbi
    return "p cnf {} {}".format(gbi, n)

# A helper function to print a set of clauses cls
def printCnf(cls):
    return "\n".join(map(lambda x: "%s 0" % " ".join(map(str, x)), cls))

# A helper function to print the sudoku solution
def printSolution(sol):
    print("######## Solution ########")
    assert len(sol) == 9
    for r in range(9):
        assert len(sol[r]) == 9
        for c in range(9):
            print(sol[r][c], end='  ')
        print()


def solve(sudoku=None):
    variables = gen_vars()

    if sudoku is None:
        rules = gen_constraints(variables, sudoku_file_name='./sudoku.txt')
    else:
        rules = gen_constraints(variables, sudoku=sudoku)

    head = printHeader(len(rules))
    rls = printCnf(rules)

    # here we create the cnf file for SATsolver
    fl = open("tmp_prob.cnf", "w")
    fl.write("\n".join([head, rls]))
    fl.close()

    # this is for runing SATsolver
    ms_out = Popen(["z3 tmp_prob.cnf"], stdout=PIPE, shell=True).communicate()[0]

    res = ms_out.decode('utf-8')
    # Print output
    res = res.strip().split('\n')

    # delete tmp_prob.cnf
    os.remove("tmp_prob.cnf")

    sudoku_solution = None

    # if it was satisfiable, we want to have the assignment printed out
    if res[0] == "s SATISFIABLE":
        # First get the assignment, which is on the second line of the file, and split it on spaces
        # Read the solution
        asgn = map(int, res[1].split()[1:])
        # Then get the variables that are positive, and get their names.
        # This way we know that everything not printed is false.
        # The last element in asgn is the trailing zero and we can ignore it

        # Convert the solution to our names
        facts = map(lambda x: varToStr[abs(x)], filter(lambda x: x > 0, asgn))

        sudoku_solution = [[-1 for _ in range(9)] for _ in range(9)]
        # Print the solution
        for f in facts:
            r, c, n = rowColNum(f)
            sudoku_solution[r - 1][c - 1] = n
    else:
        print("sudoku not solvable")
    return sudoku_solution


if __name__ == '__main__':
    # This is for reading in the arguments.
    solution = solve()
    printSolution(solution)
