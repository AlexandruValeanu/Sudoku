import copy
import pycosat


def var(i, j, d):
    """
    :param i: row
    :param j: column
    :param d: digit in (row, column)
    :return: encoding of (i, j, d) - number in [1..729]
    """
    return 81 * (i - 1) + 9 * (j - 1) + d


def sudoku_clauses():
    """
    :return: 3240 Sudoku clauses (in CNF) as a list, independent of any particular puzzle
    """
    result = []

    # for all cells, ensure that each cell:
    for i in range(1, 10):
        for j in range(1, 10):
            # denotes (at least) one of the 9 digits (1 clause)
            result.append([var(i, j, d) for d in range(1, 10)])

            # doesn't contain two digits (36 clauses)
            for d1 in range(1, 10):
                for d2 in range(d1 + 1, 10):
                    result.append([-var(i, j, d1), -var(i, j, d2)])

    # all 3x3 regions contain all digits once (81 clauses)
    for k in range(1, 10):
        for u in range(0, 3):
            for v in range(0, 3):
                clause = []
                for i in range(1, 4):
                    for j in range(1, 4):
                        clause.append(var(3 * u + i, 3 * v + j, k))

                result.append(clause)

    # each number appears in each row (81 clauses)
    for i in range(1, 10):
        for k in range(1, 10):
            result.append([var(i, j, k) for j in range(1, 10)])

    # each number appears in each column (81 clauses)
    for j in range(1, 10):
        for k in range(1, 10):
            result.append([var(i, j, k) for i in range(1, 10)])

    return result


def solve(grid):
    """
    :param grid: sudoku grid - with 0s for unknown values
    :return: completed sudoku grid
    """
    clauses = sudoku_clauses()

    for row, line in enumerate(grid):
        for col, digit in enumerate(line):
            if digit != 0:
                clauses.append([var(row + 1, col + 1, digit)])

    solution = set(pycosat.solve(clauses))

    new_grid = copy.deepcopy(grid)

    for i in range(1, 10):
        for j in range(1, 10):
            for d in range(1, 10):
                if var(i, j, d) in solution:
                    new_grid[i - 1][j - 1] = d

    assert check_solution(new_grid)
    return new_grid


def all_solutions(grid):
    """
    :param grid: sudoku grid - with 0s for unknown values
    :return: list of completed sudoku grids
    """
    clauses = sudoku_clauses()

    for row, line in enumerate(grid):
        for col, digit in enumerate(line):
            if digit != 0:
                clauses.append([var(row + 1, col + 1, digit)])

    solutions = []

    for sol in pycosat.itersolve(clauses):
        solution = set(sol)
        new_grid = copy.deepcopy(grid)

        for i in range(1, 10):
            for j in range(1, 10):
                for d in range(1, 10):
                    if var(i, j, d) in solution:
                        new_grid[i - 1][j - 1] = d

        assert check_solution(new_grid)
        solutions.append(new_grid)

    return solutions


def check_solution(grid):
    """
    :param grid: completed sudoku grid
    :return: true if grid is correctly filled in or false otherwise
    """
    rows = [[] for _ in range(0, 9)]
    cols = [[] for _ in range(0, 9)]

    for i, row in enumerate(grid):
        for j, val in enumerate(row):
            rows[i].append(val)
            cols[j].append(val)

            # wrong value in current cell
            if val < 1 or val > 9:
                return False

    # test for number of digits in each row and column
    for i in range(0, 9):
        if len(set(rows[i])) != 9 or len(set(cols[i])) != 9:
            return False

    # test for number of digits in each 3x3 square
    for k in range(1, 10):
        for u in range(0, 3):
            for v in range(0, 3):
                square = set()
                for i in range(1, 4):
                    for j in range(1, 4):
                        square.add(grid[3 * u + i - 1][3 * v + j - 1])

                if len(square) != 9:
                    return False

    return True
