import random
import string
import collections


def main():
    hexagon = createHexagon()
    printHexagon(hexagon)
    data = getDataFromHexagon(hexagon)
    printData(data)

def createHexagon():
    chars = string.ascii_uppercase

    hexagon = [[0 for x in range(13)] for x in range(13)] ;

    for x in range(0,13):
        if (x == 6):
            #if seventh row, add textalgorithm in the middle
            hexagon[x] = ['T','E','X','T','A','L','G','O','R','I','T','H','M']
        else:
            for y in range(0,13):
                hexagon [x][y] = ''
                if ( y + x > 5 and x + y < 19 ):
                    random.choice(chars)
                    hexagon[x][y] = random.choice(chars)
    return hexagon

def getDataFromHexagon(hexagon):    
    x_strings = ["" for x in range(13)]
    y_strings = ["" for x in range(13)]
    z_strings = ["" for x in range(13)]

    for x in range(0,13):
        x_string=""
        y_string=""
        z_string=""
        for y in range(0,13):
            z_string=z_string+str(hexagon[y][x])
            if (x-y+6 >= 0 and x-y+6 < 13 ):
                x_string=str(hexagon[y][x-y+6])+x_string
        x_strings[x] = x_string
        y_strings[x] = y_string.join(hexagon[x])
        z_strings[x] = z_string;
    data = collections.namedtuple('Data', ['x', 'y', 'z'])
    return  data(x_strings,y_strings,z_strings)

def printData(data):
    for x in range(0,13):
        if (x==0):
            print("'"+data.x[x]+"'")
        else:
            print(",'"+data.x[x]+"'")
    print()
    for x in range(0,13):
        if (x==0):
            print("'"+data.y[x]+"'")
        else:
            print(",'"+data.y[x]+"'")
    print()
    for x in range(0,13):
        if (x==0):
            print("'"+data.z[x]+"'")
        else:
            print(",'"+data.z[x]+"'")

def printHexagon(hexagon):
    for x in range(0,13):
        hexagon_string = ""
        for y in range(0,13):
            hexagon_string+= str(hexagon[x][y]) + " "
        print(hexagon_string)

if __name__ == '__main__':
    main()