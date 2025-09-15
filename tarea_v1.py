import pyglet as pg
from OpenGL.GL import *
import numpy as np
import libs.gpu_shape as gs
import libs.easy_shaders as sh
import libs.transformations as tr

class shape:
    def __init__(self, vertices, indices):
        self.vertices = np.array(vertices)
        self.indices = np.array(indices)

win = pg.window.Window()
program = sh.SimpleModelViewProjectionShaderProgram()
glClearColor(0.15, 0.15, 0.2)
