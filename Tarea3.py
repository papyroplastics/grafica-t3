import pyglet
from OpenGL.GL import *
import numpy as np
from math import cos, sin
import libs.transformations as tr
import libs.easy_shaders as sh
import libs.gpu_shape as gp
from libs.basic_shapes import Shape

# OPENGL SETUP
win = pyglet.window.Window()
win.set_exclusive_mouse(True)
win.set_mouse_visible(False)
program = sh.FogModelViewProjectionShaderProgram()
glUseProgram(program.shaderProgram)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glClearColor(0.5, 0.5, 0.8, 1.0)

# CARGAR NAVE
with open("assets\ship_cords.txt", "r") as file:
    ship_vert = np.array(file.read().replace("\n"," ").split(" "))

count = len(ship_vert)//6
dark_vert = np.array(ship_vert).reshape([count,6])
dark_vert[:,3:] = np.zeros(([count,3]))
dark_vert = dark_vert.reshape([count*6])

ship_ind = (0,1,4, 1,2,4, 2,3,4, 3,0,4, 3,2,5, 2,1,5, 1,0,5, 0,3,5,
            6,7,8, 9,8,7, 6,8,9, 9,7,6, 
            10,12,11, 11,12,13, 10,13,12, 10,11,13, 
            14,15,16, 17,19,18, 16,15,18, 14,18,15,
            22,21,20, 24,25,23, 24,21,22, 20,21,24)

lines_ind = (0,1, 1,2, 2,3, 3,0, 4,0, 4,1, 4,2, 4,3, 5,0,5,1, 5,2, 5,3,
            6,7, 7,8, 8,6, 6,9, 9,7, 9,8,
            10,11, 11,12, 12,10, 10,13, 13,11, 13,12,
            14,15, 15,16, 16,17, 17,18, 18,19, 15,18,
            24,21, 25,24, 24,23, 23,22, 22,21, 21,20) 

ship = gp.createGPUShape(program, Shape(ship_vert, ship_ind))
lines =  gp.createGPUShape(program, Shape(dark_vert, lines_ind))

# CREAR SUELO
length = 72
count = 48
box_len = 2 * length / count
floor_vert = ()
color = True
for x in range(count):
    for z in range(count):
        for u in range(2):
            for v in range(2):
                floor_vert += ((x+u)*box_len-length, 0, (z+v)*box_len-length)
                if color:
                    floor_vert += (0.43, 0.73, 0.43)
                else:
                    floor_vert += (0.3, 0.6, 0.3)
        color = not color
    color = not color

floor_ind = ()
for i in range(count**2):
    j = i*4
    floor_ind += (j, j+1, j+2, j+1, j+3, j+2)

floor = gp.createGPUShape(program, Shape(floor_vert, floor_ind))

# HERMITE CURVE
class HermiteCurve:
    def __init__(self):
        self.t = 0.0
        self.n = 0
        self.step = 0.0
        self.poss = [None]
        self.dirs = [[None,None]]
        self.start_dir = np.empty(3)
        self.next_pos = np.empty(3)
        self.active = False
        self.path3D = Node()
        self.hermite_matrix = np.array([[ 2,-2, 1, 1],
                                        [-3, 3,-2,-1],
                                        [ 0, 0, 1, 0],
                                        [ 1, 0, 0, 0]])

    def hermite_point(self, pos1, dir1, pos2, dir2):
        pos_matrix = np.vstack([pos1, pos2, dir1, dir2])

        t_arr = np.array([self.t**3, self.t**2, self.t, 1], dtype=np.float32)

        return t_arr @ self.hermite_matrix @ pos_matrix
    
    def start(self, pos, dir):
        if len(self.poss) > 1:
            self.active = True
            difference = np.linalg.norm(self.poss[1] - pos)
            factor = np.log(difference)
            if difference > 3: 
                self.step = 1 / (40 * factor)
                self.dirs[0][1] = dir * 5 * factor
                self.dirs[1][0] = self.start_dir * 5 * factor
            else:
                self.step = 1/20
                self.dirs[0][1] = dir
                self.dirs[1][0] = self.start_dir
            self.poss[0] = pos
            self.next_pos = self.next_curve_position()

    def end(self):
        self.active = False
        self.t = 0.0
        self.n = 0
        
        global phi, theta
        final_dir = self.dirs[-1][1]
        phi = np.arcsin(final_dir[1]/np.linalg.norm(final_dir))
        if final_dir[2] == 0:
            theta = -(np.pi/2)*(final_dir[0]/abs(final_dir[0]))
        else:
            theta = np.arctan(final_dir[0]/final_dir[2])
            if final_dir[2] > 0:
                theta += np.pi

    def next_curve_position(self):
        self.t += self.step

        if self.t >= 1:
            self.t -= 1
            self.n += 1
            if self.n == len(self.poss)-1:
                self.end()
                return self.poss[-1]
            else:
                difference = np.linalg.norm(self.poss[self.n+1] - self.poss[self.n])
                if difference > 2:
                    self.step = 1 / (40 * np.log(difference))
                else:
                    self.step = 1/20
                
        return self.hermite_point(self.poss[self.n], self.dirs[self.n][1], self.poss[self.n+1], self.dirs[self.n+1][0])

    def update_pos(self):
        newPos = np.array(self.next_pos)
        self.next_pos = self.next_curve_position()

        newDir = self.next_pos - newPos
        newDir = newDir / np.linalg.norm(newDir)

        return newPos, newDir
    
    def new_point(self, pos, dir):
        if len(self.poss) == 1:
            self.start_dir = np.array(dir)
            self.dirs += [[np.array(dir),np.array(dir)]]
        else:
            norm = np.linalg.norm(pos - self.poss[-1])
            if norm > 2:
                self.dirs += [[np.array(dir),np.array(dir)]]
                self.dirs[-1][0] *= 7 * np.log(norm)
                self.dirs[-2][1] *= 7 * np.log(norm)
            elif norm > 0.5:
                self.dirs += [[np.array(dir),np.array(dir)]]
            else:
                return
        self.poss += [np.array(pos)]
        self.path3D.children.append(create_checkpoint(pos, dir))


def create_checkpoint(pos, dir):
    vertices = np.array([0.1, 0.1, 0.1, 0.2, 0.2, 0.8,
                        -0.1, 0.1, 0.1, 0.2, 0.2, 0.8,
                        -0.1,-0.1, 0.1, 0.2, 0.2, 0.8,
                         0.1,-0.1, 0.1, 0.2, 0.2, 0.8,
                         0.0, 0.0,-0.25, 0.4, 0.4, 0.8], dtype=np.float32)

    indices = np.array([0,1,2, 0,2,3, 0,4,1, 1,4,2, 2,4,3, 3,4,0])
    gpushape = gp.createGPUShape(program, Shape(vertices, indices))

    s2 = dir[1]
    c2 = np.sqrt(1-s2**2)
    s = -dir[0] / c2
    c = -dir[2] / c2

    node = Node()
    node.children += [gpushape]
    node.transform = tr.translate(*pos) @ tr.trigRotationY(s,c) @ tr.trigRotationX(s2,c2)
    return node

sphere_vertices = []
cosines = [np.cos(np.pi*i/4) for i in range(8)]
sines = [np.cos(np.pi*i/4) for i in range(8)]

def create_midpoint(pos):
    vertices = []

# CREATE SCENEGRAPH
class Node:
    def __init__(self):
        self.transform = tr.identity()
        self.children = []
        self.mode = GL_TRIANGLES

    def draw(self, parent_transform = tr.identity()):
        new_transform = parent_transform @ self.transform
        for child in self.children:
            if isinstance(child, Node):
                child.draw(new_transform)
            else:
                glUniformMatrix4fv(model_loc, 1, GL_TRUE, new_transform)
                program.drawCall(child, self.mode)


linesNode = Node()
linesNode.mode = GL_LINES
linesNode.children += [lines]

shipNode = Node()
shipNode.children += [ship, linesNode]

floorNode = Node()
floorNode.children += [floor]

scene = Node()
scene.children += [shipNode, floorNode]

# SET TRANSFORMS
view = tr.lookAt(np.array([0,2,3]), np.array([0,2,0]), np.array([0,1,3]))
projection = tr.perspective(60, win.aspect_ratio, 0.5, 100)
model_loc = glGetUniformLocation(program.shaderProgram, "model")
view_loc = glGetUniformLocation(program.shaderProgram, "view")
proj_loc = glGetUniformLocation(program.shaderProgram, "projection")
shipPos_loc = glGetUniformLocation(program.shaderProgram, "shipPos")
glUniformMatrix4fv(view_loc, 1, GL_TRUE, view)
glUniformMatrix4fv(proj_loc, 1, GL_TRUE, projection)

# Programa :D
theta = 0.0
phi = 0.0
rotate_left = False
rotate_right = False
forward = False
backward = False
visible_path = False
position = np.array([0, 2, 0], dtype=np.float32)
direction = np.array([0, 0, -1], dtype=np.float32)
animation = HermiteCurve()

def updateScenegraph():
    global theta, position, direction
    if animation.active:
        position, direction = animation.update_pos()
        s2 = direction[1]
        c2 = np.sqrt(1-s2**2)
        s = -direction[0] / c2
        c = -direction[2] / c2

    else:
        if rotate_left:
            theta += 0.05
        if rotate_right:
            theta -= 0.05

        s = sin(theta)
        c = cos(theta)
        s2 = sin(phi)
        c2 = cos(phi)

        direction = np.array((-s*c2,s2,-c*c2))

        if forward:
            if position[1]<=1 and phi<0:
                direction[1] = 0
            position += direction * 0.08

        elif backward:
            if position[1]<=1 and phi>0:
                direction[1] = 0
            position -= direction * 0.08

    glUniform3f(shipPos_loc, *position)
    shipNode.transform = tr.translate(*position) @ tr.trigRotationY(s,c) @ tr.trigRotationX(s2,c2)
    floorNode.transform = tr.translate(6*(position[0]//6), 0, 6*(position[2]//6))

@win.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)
    glUseProgram(program.shaderProgram)
    scene.draw()
    if visible_path:
        animation.path3D.draw()
    updateScenegraph()
    
@win.event
def on_mouse_motion(x, y, dx, dy):
    global phi
    if not animation.active:
        if dy > 0.0 and phi < 0.785:
            phi += dy/600
        elif dy < 0.0 and phi > -0.785:
            phi += dy/600

@win.event
def on_key_press(symbol, mods):
    global rotate_left, rotate_right, forward, backward, visible_path
    if symbol == pyglet.window.key.A:
        rotate_left = True
    elif symbol == pyglet.window.key.D:
        rotate_right = True
    elif symbol == pyglet.window.key.W:
        forward = True
    elif symbol == pyglet.window.key.S:
        backward = True
    elif symbol == pyglet.window.key.R and not animation.active:
        animation.new_point(position, direction)
    elif symbol == pyglet.window.key._1 and not animation.active:
        animation.start(position, direction)
    elif symbol == pyglet.window.key.V:
        visible_path = not visible_path
    elif symbol == pyglet.window.key.ESCAPE:
        win.close()

@win.event
def on_key_release(symbol, mods):
    global rotate_left, rotate_right, forward, backward
    if symbol == pyglet.window.key.A:
        rotate_left = False
    elif symbol == pyglet.window.key.D:
        rotate_right = False
    elif symbol == pyglet.window.key.W:
        forward = False
    elif symbol == pyglet.window.key.S:
        backward = False

@win.event
def on_close():
    ship.clear()
    lines.clear()
    floor.clear()
    glDeleteProgram(program.shaderProgram)

pyglet.app.run()