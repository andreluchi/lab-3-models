import struct
from obj import Obj
import math


# ===============================================================
# Utilities
# ===============================================================

def char(c):
    """
    Input: requires a size 1 string
    Output: 1 byte of the ascii encoded char
    """
    return struct.pack('=c', c.encode('ascii'))


def word(w):
    """
    Input: requires a number such that (-0x7fff - 1) <= number <= 0x7fff
           ie. (-32768, 32767)
    Output: 2 bytes
    Example:
    >>> struct.pack('=h', 1)
    b'\x01\x00'
    """
    return struct.pack('=h', w)


def dword(d):
    """
    Input: requires a number such that -2147483648 <= number <= 2147483647
    Output: 4 bytes
    Example:
    >>> struct.pack('=l', 1)
    b'\x01\x00\x00\x00'
    """
    return struct.pack('=l', d)

"Function that parses a color"
def color(r, g, b):
    return bytes([b, g, r])


# ===============================================================
# Constants
# ===============================================================

BLACK = color(0, 0, 0)
GREEN = color(50, 168, 82)
BLUE = color(50, 83, 168)
RED = color(168, 50, 60)
WHITE = color(255, 255, 255)



class ViewPort(object):

    def setSize(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y



# ===============================================================
# Renders a BMP file
# ===============================================================



class Render(object):
    def __init__(self):
        self.paintColor = WHITE
        self.bufferColor = BLACK


    def glInit(self):
        self.viewPort = ViewPort()

    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        self.glClear()


    def glViewPort(self, x, y, width, height):
        self.viewPort.setSize(x, y, width, height)

    def glClear(self):
        self.framebuffer = [
            [self.bufferColor for x in range(self.width)]
            for y in range(self.height)
        ]

    def glFinish(self, filename='out.bmp'):
        f = open(filename, 'bw')

        # File header (14 bytes)
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        # Image header (40 bytes)
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        # Pixel data (width x height x 3 pixels)
        for x in range(self.height):
            for y in range(self.width):
                f.write(self.framebuffer[x][y])

        f.close()

    


    # Gl vertex solo normaliza las coordenadas de un solo punto
    def glVertex(self, x, y):
        currentYCordinate =  self.viewPort.y + (self.viewPort.height//2) * (y + 1)
        currentXCordinate = self.viewPort.x + (self.viewPort.width//2) * (x + 1)
        self.point(currentXCordinate, currentYCordinate)

    def point(self, normalizedX, normalizedY):
        self.framebuffer[int(normalizedY)][int(normalizedX)] = self.paintColor

    def glClearColor(self, r, g, b):
        self.bufferColor = color(r,g,b)

    def glColor(self, r, g, b):
        self.paintColor= color(r,g,b)

    def line(self, x0, y0, x1, y1, transform = True):
        if transform:
            y0 = self.viewPort.y + (self.viewPort.height // 2) * (y0 + 1)
            y1 = self.viewPort.y + (self.viewPort.height // 2) * (y1 + 1)
            x0 = self.viewPort.x + (self.viewPort.width // 2) * (x0 + 1)
            x1 = self.viewPort.x + (self.viewPort.width // 2) * (x1 + 1)
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        steep = dy > dx
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        offset = 0
        threshold = 0.5 * 2 * dx

        y = y0
        for x in range(x0, x1 + 1):
            if steep:
                self.point(y, x)
            else:
                self.point(x, y)

            offset += dy * 2
            if offset >= threshold:
                y += 1 if y0 < y1 else -1
                threshold += dx * 2

    def getLine(self, x0, y0, x1, y1):
        linePoints = []
        # y0 = self.viewPort.y + (self.viewPort.height / 2) * (y0 + 1)
        # y1 = self.viewPort.y + (self.viewPort.height / 2) * (y1 + 1)
        # x0 = self.viewPort.x + (self.viewPort.width / 2) * (x0 + 1)
        # x1 = self.viewPort.x + (self.viewPort.width / 2) * (x1 + 1)
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        steep = dy > dx
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        offset = 0
        threshold = dx

        y = y0
        for x in range(int(x0), int(x1) + 1):
            if steep:
                linePoints.append(Point(y, x))
            else:
                linePoints.append(Point(x, y))

            offset += dy * 2
            if offset >= threshold:
                y += 1 if y0 < y1 else -1
                threshold += dx * 2
        return linePoints

    def drawLines(self, polygon):
        yPointsLines = []
        xPointsLines = []
        lines = []

        for index, point in enumerate(polygon.points):
            point2 = polygon.points[(index + 1) % len(polygon.points)]
            line = self.getLine(point[0], point[1], point2[0], point2[1])
            self.line(point[0], point[1], point2[0], point2[1], False)
            for lp in line:
                lines.append(lp)
                yPointsLines.append(lp.y)
                xPointsLines.append(lp.x)

        # centerY = self.viewPort.height / 2
        # centerX = self.viewPort.width / 2


        minY = min(yPointsLines)
        maxY = max(yPointsLines)
        minX = min(xPointsLines)
        maxX = max(xPointsLines)
        for indexX in range(minX, maxX):
            iterableLinesX = [line for line in lines if line.x == indexX]
            for indexY in range(minY, maxY):
                iterableLinesY = [linep for linep in lines if linep.y == indexY]
                if minY < indexY < maxY:
                    if minX < indexX < maxX:
                        if any(i.y <= indexY for i in iterableLinesX) and any(i.y >= indexY for i in iterableLinesX):
                            if any(i.x <= indexX for i in iterableLinesY) and any(i.x >= indexX for i in iterableLinesY):
                                self.point(indexX, indexY)

    def load(self, filename, translate, scale):
        model = Obj(filename)

        for face in model.faces:
            vcount = len(face)

            for j in range(vcount):
                f1 = face[j][0]
                f2 = face[(j + 1) % vcount][0]

                v1 = model.vertices[f1 - 1]
                v2 = model.vertices[f2 - 1]

                x1 = round((v1[0] + translate[0]) * scale[0])
                y1 = round((v1[1] + translate[1]) * scale[1])
                x2 = round((v2[0] + translate[0]) * scale[0])
                y2 = round((v2[1] + translate[1]) * scale[1])

                self.line(x1, y1, x2, y2, False)