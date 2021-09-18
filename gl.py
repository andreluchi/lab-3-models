from Renderer import Render, GREEN, BLUE
from polygon import Polygon

bitmap = Render()
bitmap.glInit()
bitmap.glCreateWindow(1000,500)
bitmap.glViewPort(30,30,800,800)
bitmap.load("./cube2.obj", (4, 3), (100, 100))
bitmap.glFinish()