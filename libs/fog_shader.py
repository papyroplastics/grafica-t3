# coding=utf-8
"""Simple Shaders"""

from OpenGL.GL import *
import OpenGL.GL.shaders

from libs.gpu_shape import GPUShape

__author__ = "Lucas Llort"
__license__ = "MIT"

# We will use 32 bits data, so we have 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4


class FogModelViewProjectionShaderProgram: # Shader de neblina

    def __init__(self):

        vertex_shader = """
            #version 330
            
            uniform mat4 viewProj;
            uniform mat4 model;

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            out vec3 fragPos;
            void main()
            {
                fragPos = vec3(model * vec4(position, 1.0));
                gl_Position = viewProj * vec4(fragPos, 1.0);
                newColor = color;
            }
            """

        fragment_shader = """
            #version 330
            in vec3 newColor;
            in vec3 fragPos;

            uniform vec3 shipPos;

            out vec4 outColor;
            void main()
            {
                float alpha = max(1 - 0.014 * max(abs(shipPos.x - fragPos.x), abs(shipPos.z - fragPos.z)), 0);
                outColor = vec4(newColor, alpha);
            }
            """

        # Binding artificial vertex array object for validation
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)


        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)
