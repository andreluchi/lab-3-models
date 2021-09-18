from Renderer import Render, GREEN, BLUE
from polygon import Polygon

bitmap = Render()
bitmap.glInit()
bitmap.glCreateWindow(1000,500)
bitmap.glViewPort(30,30,800,800)
bitmap.load("./fox.obj", (100, 10), (5, 5))
bitmap.glFinish()