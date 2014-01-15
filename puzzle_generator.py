import random
import string
from copy import deepcopy
from itertools import product
import numpy as np
from regex_finder import findregex

MAX_WIDTH = 13
chars = set(string.ascii_uppercase)

def main():

    grid = HexGrid()

    generateSolution(grid)
    print(generateRegexHints(grid))


class HexGrid:
    def __init__(self):
        self.grid = self.constructGrid()

    def iterXYZ(self):
        for row in self.iterXDirection():
            yield row
        for row in self.iterYDirection():
            yield row
        for row in self.iterZDirection():
            yield row

    def constructGrid(self):
        grid = []
        gridRow = [Cell(i) for i in range(1, MAX_WIDTH + 1)]
        frontBuffer = list(range(MAX_WIDTH // 2, 0, -1)) + [0] * (MAX_WIDTH // 2 + 1)
        backBuffer = list(reversed(frontBuffer))
        for i in range(MAX_WIDTH):
            rowLen = MAX_WIDTH - frontBuffer[i] - backBuffer[i]
            row = [None]*frontBuffer[i] + deepcopy(gridRow[:rowLen]) + [None]*backBuffer[i]
            grid.append(row)
        return grid

    def iterDirection(self, direction):
        if direction == 'X':
            for row in self.iterXDirection():
                yield row
        elif direction == 'Y':
            for row in self.iterYDirection():
                yield row
        elif direction == 'Z':
            for row in self.iterZDirection():
                yield row

    def iterXDirection(self):
        # SW->NE rows
        ar = np.array(self.grid)
        fromIdx = MAX_WIDTH // 2
        toIdx = -MAX_WIDTH // 2
        for i in range(fromIdx, toIdx, -1):
            cellRow = []
            for cell in reversed(np.fliplr(ar).diagonal(i)):
                cellRow.append(cell)
            yield cellRow

    def iterYDirection(self):
        # E->W rows
        for row in self.grid:
            cellRow = []
            for cell in row:
                if not cell:
                    continue
                else:
                    cellRow.append(cell)
            yield cellRow

    def iterZDirection(self):
        # NW->SE rows
        for col in range(MAX_WIDTH):
            cellRow = []
            for row in range(MAX_WIDTH):
                cell = self.grid[row][col]
                if not cell:
                    continue
                else:
                    cellRow.append(cell)
            yield cellRow


class Cell:
    def __init__(self, cid = 0):
        self.cid = cid
        self.allowed = set()
        self.notAllowed = set()

    def __repr__(self):
        return str(self.cid)

    def addConstraints(self, allowedChar = None, disallowedChar = None):
        if allowedChar == disallowedChar:
            raise ValueError('Allowed and not allowed characters must be different')
        if allowedChar in self.notAllowed:
            raise ValueError('Can\'t add allowed character')
        if disallowedChar in self.allowed:
            raise ValueError('Can\'t add disallowed character')
        if allowedChar:
            self.allowed.add(allowedChar)
        if disallowedChar:
            self.notAllowed.add(disallowedChar)


def generateSolution(grid, useSpecialSolution = True):
    for row in grid.iterYDirection():
        if useSpecialSolution and len(row) == MAX_WIDTH:
            insertSpecialSolution(row)
        else:
            for cell in row:
                goodCount = random.randint(1,1)
                goodCount = 1 if random.random() > 0.3 else 2
                badCount = random.randint(1,1)
                badCount = 1 if random.random() > 0.3 else 2
                for i in range(goodCount):
                    goodChar = random.sample(chars - cell.allowed - cell.notAllowed, 1)[0]
                    cell.addConstraints(allowedChar = goodChar)
                for i in range(badCount):
                    badChar = random.sample(chars - cell.allowed - cell.notAllowed, 1)[0]
                    cell.addConstraints(disallowedChar = badChar)



def insertSpecialSolution(row):
    hint = 'TEXTALGORITHM'
    badChars = set(string.ascii_uppercase)
    for cell, goodChar in zip(row, hint):
        cell.allowed.add(goodChar)
        badCount = random.randint(1,2)
        badCount = 1 if random.random() > 0.3 else 2
        for i in range(badCount):
            badChar = random.sample(chars - cell.allowed - cell.notAllowed, 1)[0]
            cell.addConstraints(disallowedChar = badChar)


def generateRegexHints(grid):
    hints = {'X':[], 'Y':[], 'Z':[]}
    for d in ('XYZ'):
        for row in grid.iterDirection(d):
            allowedStrings = getAllowedStrings(row)
            notAllowedStrings = getNotAllowedStrings(row)
            print('alowed', allowedStrings)
            print('not alowed', notAllowedStrings)
            print()
            hints[d].append(findregex(allowedStrings, notAllowedStrings))
    return hints


def getAllowedStrings(row):
    for cell in row:
        print('cell.allowed', cell.allowed)
    allowed = [cell.allowed for cell in row]
    strings = set(map(''.join, product(*allowed)))
    return set(strings)


def getNotAllowedStrings(row):
    for cell in row:
        print('cell.notAllowed', cell.notAllowed)
    notAllowed = [cell.notAllowed for cell in row]
    strings = set(map(''.join, product(*notAllowed)))
    return set(strings)

winners = {'DPGHGZM', 'DNGHGZM', 'DNGHVZM', 'DNOHGZM', 'DPOHGZM', 'PNOHVZM', 'PPOHGZM', 'PNGHGZM', 'PPGHVZM'}
losers = {'ELHAHRCD', 'ELHAHIVD', 'ELHAJICD', 'ELHAHICD', 'ELHAJIVD', 'ELHPHIVD'}
winners = set('''washington adams jefferson jefferson madison madison monroe
monroe adams jackson jackson vanburen harrison polk taylor pierce buchanan
lincoln lincoln grant grant hayes garfield cleveland harrison cleveland mckinley
 mckinley roosevelt taft wilson wilson harding coolidge hoover roosevelt
roosevelt roosevelt roosevelt truman eisenhower eisenhower kennedy johnson nixon
nixon carter reagan reagan bush clinton clinton bush bush obama obama'''.split())

losers = set('''clinton jefferson adams pinckney pinckney clinton king adams
jackson adams clay vanburen vanburen clay cass scott fremont breckinridge
mcclellan seymour greeley tilden hancock blaine cleveland harrison bryan bryan
parker bryan roosevelt hughes cox davis smith hoover landon wilkie dewey dewey
stevenson stevenson nixon goldwater humphrey mcgovern ford carter mondale
dukakis bush dole gore kerry mccain romney'''.split())
losers = losers - winners
print(findregex(winners, losers))


if __name__ == '__main__':
    pass#main()
