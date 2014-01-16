import random
import string
from copy import copy, deepcopy
import json
from time import time
from pprint import pprint
import re
import numpy as np
from regex_finder import findregex

MAX_WIDTH = 13
X, Y, Z = 'x', 'y', 'z'

def main():
    for i in range(30):

        chars = set(random.sample(string.ascii_uppercase, random.randint(8, 26)))
        grid = HexGrid(chars)
        useSpecialHint = random.choice([True, False])
        generateSolution(grid, useSpecialHint)

        hints = generateRegexHints(grid)
        name = str(round(time() * 1000000))
        board_data = {'size':MAX_WIDTH, 'name':name, 'x':hints[X], 'y':hints[Y], 'z':hints[Z]}
        solution = {'rows':getSampleSolution(grid)}
        pprint(board_data)
        pprint(solution)
        puzzlename = 'puzzles/' + board_data['name'] + '.json'
        solutionName = 'puzzles/' + board_data['name'] + '_solution.json'
        with open(puzzlename, 'w') as f:
            json.dump(board_data, f)
        with open(solutionName, 'w') as f:
            json.dump(solution, f)



class HexGrid:
    def __init__(self, chars):
        self.grid = self.constructGrid()
        self.chars = chars

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
        if direction == X:
            for row in self.iterXDirection():
                yield row
        elif direction == Y:
            for row in self.iterYDirection():
                yield row
        elif direction == Z:
            for row in self.iterZDirection():
                yield row

    def iterXDirection(self):
        # rows going SW->NE
        ar = np.array(self.grid)
        fromIdx = MAX_WIDTH // 2
        toIdx = -MAX_WIDTH // 2
        for i in range(fromIdx, toIdx, -1):
            cellRow = []
            for cell in reversed(np.fliplr(ar).diagonal(i)):
                cellRow.append(cell)
            yield cellRow

    def iterYDirection(self):
        # rows going E->W
        for row in self.grid:
            cellRow = []
            for cell in row:
                if not cell:
                    continue
                else:
                    cellRow.append(cell)
            yield cellRow

    def iterZDirection(self):
        # rows going NW->SE
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
        if allowedChar:
            self.allowed.add(allowedChar)
        if disallowedChar:
            self.notAllowed.add(disallowedChar)


def generateSolution(grid, useSpecialSolution = True):
    for row in grid.iterYDirection():
        if useSpecialSolution and len(row) == MAX_WIDTH:
            insertSpecialSolution(row, grid.chars)
        else:
            for cell in row:
                goodCount = random.randint(1,4)
                #goodCount = 1 if random.random() > 0.3 else 2
                badCount = random.randint(1,4)
                #badCount = 1 if random.random() > 0.3 else 2
                for i in range(goodCount):
                    goodChar = random.sample(grid.chars - cell.allowed - cell.notAllowed, 1)[0]
                    cell.addConstraints(allowedChar = goodChar)
                for i in range(badCount):
                    badChar = random.sample(grid.chars - cell.allowed - cell.notAllowed, 1)[0]
                    cell.addConstraints(disallowedChar = badChar)



def insertSpecialSolution(row, chars):
    hint = 'TEXTALGORITHM'
    badChars = copy(chars)
    for cell, goodChar in zip(row, hint):
        cell.allowed.add(goodChar)
        #badCount = random.randint(1,2)
        badCount = 1 if random.random() > 0.3 else 2
        for i in range(badCount):
            badChar = random.sample(chars - cell.notAllowed, 1)[0]
            cell.addConstraints(disallowedChar = badChar)


def generateRegexHints(grid):
    hints = {X:[], Y:[], Z:[]}
    for d in (X, Y, Z):
        for row in grid.iterDirection(d):
            regex = ''
            for c in row:
                winners = set(c.allowed)
                losers = set(c.notAllowed) - winners
                regex += findregex(winners, losers)
            regex = shorten(regex, grid.chars)


            hints[d].append(regex)
    return hints


def shorten(regex, chars):
    regex = regex.replace('^', '')
    regex = regex.replace('$', '')
    components = regex.split('|')
    newComponents = []
    orGroup = ''
    for c in components:
        if len(c) < 2:
            orGroup += c
        elif len(c) < 3:
            newComponents.append(orGroupToRe(orGroup))
            orGroup = ''
        else:
            newComponents.append(orGroupToRe(orGroup))
            orGroup = ''
            newComponents.append(orGroupToRe(c))
    regex = ''.join(newComponents)
    regex = re.sub(r'\.\*(\.\*)+', '.*', regex)
    regex = regex.replace('**', '*')
    return regex


def orGroupToRe(orGroup):
    if orGroup == '':
        return ''
    elif len(orGroup) == 1:
        return orGroup if random.random() > 0 else '.'
    elif len(set(orGroup)) == 1:
        return '{}*'.format(list(orGroup).pop())
    elif len(set(orGroup)) > 2:
        return '.*'
    else:
        return '[{}]*'.format(''.join(sorted(set(orGroup))))


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


def getSampleSolution(grid):
    rowSolutions = []
    for row in grid.iterDirection(Y):
        rowSolution = []
        for cell in row:
            rowSolution.append(random.choice(list(cell.allowed)))
        rowSolutions.append(rowSolution)
    return rowSolutions


if __name__ == '__main__':
    pass
    main()
