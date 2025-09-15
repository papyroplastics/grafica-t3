import pyglet
from OpenGL.GL import *
import numpy as np
import libs.transformations as tr
import libs.easy_shaders as sh
import libs.gpu_shape as gp
from libs.basic_shapes import Shape

with open("assets\ship_cords.txt", "r") as file:
    ship_vert = np.array(file.read().replace("\n"," ").split(" "))

count = len(ship_vert)//6
dark_vert = np.array(ship_vert).reshape([count,6])
dark_vert[:,3:] = np.zeros(([count,3]))
dark_vert = dark_vert.reshape([count*6])

ship_ind = (0,4,1, 1,4,2, 2,4,3, 3,4,0, 3,5,2, 2,5,1, 1,5,0, 0,5,3,
            6,8,7, 9,7,8, 6,9,8, 9,6,7,
            10,11,12, 11,13,12, 10,12,13, 10,13,11,
            14,16,15, 17,18,19, 16,18,15, 14,15,18,
            22,20,21, 24,23,25, 24,22,21, 20,24,21)

ind_lines = (0,1, 1,2, 2,3, 3,0, 4,0, 4,1, 4,2, 4,3, 5,0,5,1, 5,2, 5,3,
            6,7, 7,8, 8,6, 6,9, 9,7, 9,8,
            10,11, 11,12, 12,10, 10,13, 13,11, 13,12,
            14,15, 15,16, 16,17, 17,18, 18,19, 15,18,
            24,21, 25,24, 24,23, 23,22, 22,21, 21,20)

win = pyglet.window.Window()
program = sh.SimpleModelViewProjectionShaderProgram()
glUseProgram(program.shaderProgram)
ship = gp.createGPUShape(program, Shape(ship_vert, ship_ind))
lines =  gp.createGPUShape(program, Shape(dark_vert, ind_lines))

glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)
glClearColor(0.15, 0.15, 0.17, 1.0)

view = tr.lookAt(np.array([0,0,2]), np.array([0,0,0]), np.array([0,1,2]))
glUniformMatrix4fv(glGetUniformLocation(program.shaderProgram, "view"), 1, GL_TRUE, view)
ratio = win.aspect_ratio
projection = tr.frustum(-0.5 * ratio, 0.5 * ratio, -0.5, 0.5, 0.5, 4)
glUniformMatrix4fv(glGetUniformLocation(program.shaderProgram, "projection"), 1, GL_TRUE, projection)

theta = 0
rot_loc = glGetUniformLocation(program.shaderProgram, "model")

@win.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)
    glUseProgram(program.shaderProgram)
    program.drawCall(ship, GL_TRIANGLES)
    program.drawCall(lines, GL_LINES)

    global theta
    theta += 0.01
    rotation = tr.rotationY(theta)
    glUniformMatrix4fv(rot_loc, 1, GL_TRUE, rotation)

@win.event
def on_close():
    ship.clear()
    lines.clear()
    glDeleteProgram(program.shaderProgram)

pyglet.app.run()