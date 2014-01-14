from regex_finder import *
import numpy as np

MAX_WIDTH = 13

def main():


    grid = HexGrid()

    for row in grid.iterRows():
        print(row)


class HexGrid:
    def __init__(self):
        self.grid = self.constructGrid()

    def iterRows(self):
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
            row = [None]*frontBuffer[i] + gridRow[:rowLen] + [None]*backBuffer[i]
            grid.append(row)
        return grid

    def iterXDirection(self):
        ar = np.array(self.grid)
        fromIdx = MAX_WIDTH//2
        toIdx = -MAX_WIDTH//2
        for i in range(fromIdx, toIdx, -1):
            cellRow = []
            for cell in np.fliplr(ar).diagonal(i):
                cellRow.append(cell)
            yield cellRow

    def iterYDirection(self):
        for row in self.grid:
            cellRow = []
            for cell in row:
                if not cell:
                    continue
                else:
                    cellRow.append(cell)
            yield cellRow

    def iterZDirection(self):
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
    def __init__(self, cid = 0, allowed = {}, notAllowed = {}):
        self.cid = cid
        self.allowed = allowed
        self.notAllowed = notAllowed

    def __repr__(self):
        return str(self.cid)

    def addConstraints(self, goodChar, badChar):
        if goodChar == badChar:
            raise Exception('Allowed and not allowed characters must be different')
        self.allowed.add(goodChar)
        self.notAllowed.add(badChar)

if __name__ == '__main__':
    main()
