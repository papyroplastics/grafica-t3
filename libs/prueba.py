import pyglet as pg
from OpenGL.GL import *
import gpu_shape as gs
import easy_shaders as sh
import transformations as tr

win = pg.window.Window()
program = sh.SimpleShaderProgram
glClearColor(0.15, 0.15, 0.2)
