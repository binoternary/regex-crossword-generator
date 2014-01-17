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
    for i in range(10):

        chars = set(random.sample(string.ascii_uppercase, random.randint(8, 16)))
        grid = HexGrid(chars)
        useSpecialHint = False#random.choice([True, False])
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
        gridRow = [Cell() for i in range(1, MAX_WIDTH + 1)]
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
    def __init__(self):
        self.regex = ''
        self.allowed = set()
        self.notAllowed = set()


    def addConstraints(self, allowedChar = None, disallowedChar = None):
        if allowedChar:
            self.allowed.add(allowedChar)
        if disallowedChar:
            self.notAllowed.add(disallowedChar)

    def compactRegex(self):
        self.regex = self.regex.replace('|', '')
        self.regex = self.regex.replace('^', '')
        self.regex = self.regex.replace('$', '')


def generateSolution(grid, useSpecialSolution = True):
    for row in grid.iterYDirection():
        if useSpecialSolution and len(row) == MAX_WIDTH:
            insertSpecialSolution(row, grid.chars)
        else:
            for cell in row:
                goodCount = random.randint(1,3)
                #goodCount = 1 if random.random() > 0.3 else 2
                badCount = random.randint(1,3)
                #badCount = 1 if random.random() > 0.3 else 2
                for i in range(goodCount):
                    goodChar = random.sample(grid.chars - cell.allowed - cell.notAllowed, 1)[0]
                    cell.addConstraints(allowedChar = goodChar)
                for i in range(badCount):
                    badChar = random.sample(grid.chars - cell.allowed - cell.notAllowed, 1)[0]
                    cell.addConstraints(disallowedChar = badChar)
                cell.regex = findregex(cell.allowed, cell.notAllowed - cell.allowed)
                assert(cell.regex != '')
                cell.compactRegex()



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
            components = []
            regex = ''
            for c in row:
                components.append(c.regex)
            regex = shorten('-'.join(components))

            hints[d].append(regex)
    return hints


def shorten(regex):
    components = regex.split('-')
    #print(1, 'components:', components)
    orGroups = []
    regex = ''
    for c in components:
        #print(2, 'component:', c)
        if rnd(0.7):
            orGroups.append(c)
        else:
            regex += mergeOrGroups(orGroups)
            #print(3, 'regex:', regex)
            regex += mergeOrGroups([c])
            #print(4, 'regex:', regex)
            orGroups = []

    regex += mergeOrGroups(orGroups)
    #print(6, 'regex:', regex)

    regex = regex.replace('..*', '.*')
    regex = re.sub(r'\.\*(\.\*)+', '.*', regex)
    regex = regex.replace('**', '*')
    #print(8, 'regex:', regex)
    return regex


def mergeOrGroups(orGroups):
    #print(5, 'orGroups:', orGroups)
    if len(orGroups) == 0:
        return ''
    elif len(orGroups) == 1:
        rePart = orGroups.pop()
        if len(rePart) > 2:
            return '.'
        elif len(rePart) > 1:
            return '[{}]'.format(rePart)
        else:
            return rePart
    else:
        repeatSet = set(''.join(orGroups))
        if len(repeatSet) == 1:
            return '{}*'.format(repeatSet.pop())
        elif len(repeatSet) > 3:
            return '.*'
        else:
            if rnd(0.2):
                return '.*'
            else:
                repeat = '+' if rnd(0.8) else '*'
                return '[{}]{}'.format(''.join(sorted(repeatSet)), repeat)



def rnd(x = 0.5):
    return random.random() < x


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
