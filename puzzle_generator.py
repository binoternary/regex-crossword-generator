import random
import string
from copy import copy, deepcopy
from itertools import product
import json
from time import time
from pprint import pprint
import numpy as np
from regex_finder import findregex

MAX_WIDTH = 13
X, Y, Z = 'x', 'y', 'z'

def main():
    for i in range(30):

        chars = set(random.sample(string.ascii_uppercase, random.randint(5, 26)))
        grid = HexGrid(chars)
        useSpecialHint = random.choice([True, False])
        generateSolution(grid, useSpecialHint)

        hints = generateRegexHints(grid)
        board_data = {'size':MAX_WIDTH, 'name':str(round(time() * 1000000)), 'x':hints[X], 'y':hints[Y], 'z':hints[Z]}
        pprint(board_data)
        filename = 'puzzles/' + board_data['name'] + '.json'
        with open(filename, 'w') as f:
            json.dump(board_data, f)



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
                #goodCount = random.randint(1,2)
                goodCount = 1 if random.random() > 0.3 else 2
                #badCount = random.randint(1,2)
                badCount = 1 if random.random() > 0.3 else 2
                for i in range(goodCount):
                    goodChar = random.sample(grid.chars - cell.notAllowed, 1)[0]
                    cell.addConstraints(allowedChar = goodChar)
                for i in range(badCount):
                    badChar = random.sample(grid.chars - cell.notAllowed, 1)[0]
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
            allowedStrings = getAllowedStrings(row)
            notAllowedStrings = getNotAllowedStrings(row)
            print('allowed', allowedStrings)
            print('not allowed', notAllowedStrings)
            print()

            split = 2 if len(row) < 9 else 3
            regex = ''
            if split == 2:
                wFirst = set(map(lambda s: s[:split], allowedStrings))
                wLast = set(map(lambda s: s[split:], allowedStrings))

                lFirst = set(map(lambda s: s[:split], notAllowedStrings))
                lLast = set(map(lambda s: s[split:], notAllowedStrings))

                lFirst = lFirst - wFirst
                lLast = lLast - wLast

                regex += '.*'
                regex += fixRegexPartSyntax(findregex(wFirst, lFirst), grid.chars)
                regex += '.*'
                regex += fixRegexPartSyntax(findregex(wLast, lLast), grid.chars)
                regex += '.*'
            else:
                wFirst = set(map(lambda s: s[:split], allowedStrings))
                wMid = set(map(lambda s: s[split:split*2], allowedStrings))
                wLast = set(map(lambda s: s[split*2:], allowedStrings))

                lFirst = set(map(lambda s: s[:split], notAllowedStrings))
                lMid = set(map(lambda s: s[split:split*2], notAllowedStrings))
                lLast = set(map(lambda s: s[split:], notAllowedStrings))

                lFirst = lFirst - wFirst
                lMid = lMid - wMid
                lLast = lLast - wLast

                regex += '.*'
                regex += fixRegexPartSyntax(findregex(wFirst, lFirst), grid.chars)
                regex += '.*'
                regex += fixRegexPartSyntax(findregex(wMid, lMid), grid.chars)
                regex += '.*'
                regex += fixRegexPartSyntax(findregex(wLast, lLast), grid.chars)
                regex += '.*'
            regex = regex.replace('^', '')
            regex = regex.replace('$', '')
            hints[d].append(regex)
    return hints

def fixRegexPartSyntax(regexPart, chars):
    if regexPart.find('|') > -1:
        orComponents = regexPart.split('|')
        singleChars = [c for c in orComponents if len(c) < 2]
        sequences = [c for c in orComponents if len(c) > 1]
        singleChars = ''.join(singleChars).replace('.', str(chars.difference(set(singleChars)).pop()))
        if len(singleChars) > 1:
            singleChars =  '[' + singleChars  + ']'
        if sequences:
            return '(' + '|'.join(sequences) + ('|' + singleChars if singleChars else '') + ')'
        else:
            return singleChars
    else:
        return regexPart

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


if __name__ == '__main__':
    main()
