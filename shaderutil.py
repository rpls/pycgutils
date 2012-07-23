# -*- coding: utf-8 -*-
##############################################################################
# 
#  Shaderutilities
#  Authors:
#   - Richard Petri <dasricht at gmail.com>
#
#  This is free and unencumbered software released into the public domain.
#  
#  Anyone is free to copy, modify, publish, use, compile, sell, or
#  distribute this software, either in source code form or as a compiled
#  binary, for any purpose, commercial or non-commercial, and by any
#  means.
#  
#  In jurisdictions that recognize copyright laws, the author or authors
#  of this software dedicate any and all copyright interest in the
#  software to the public domain. We make this dedication for the benefit
#  of the public at large and to the detriment of our heirs and
#  successors. We intend this dedication to be an overt act of
#  relinquishment in perpetuity of all present and future rights to this
#  software under copyright law.
#  
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#   
#  For more information, please refer to <http://unlicense.org/>
#
##############################################################################
from OpenGL.GL import glCreateProgram, glDeleteProgram, glAttachShader, glLinkProgram, glGetProgramiv, glGetProgramInfoLog, glUseProgram
from OpenGL.GL import glCreateShader, glDeleteShader, glShaderSource, glCompileShader, glGetShaderInfoLog, glGetShaderiv
from OpenGL.GL import glGetUniformLocation, glGetAttribLocation
from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_GEOMETRY_SHADER, GL_COMPILE_STATUS, GL_LINK_STATUS, GL_TRUE

class Shader(object):
    '''
    A utility/wrapper for OpenGL Shader.
    '''
    def __init__(self, vsource, fsource, gsource = None):
        self.uniformlocs = {}
        self.attributelocs = {}
        self.program = None
        try:
            shaders = []
            shaders.append(self._createShader(GL_VERTEX_SHADER, vsource))
            if gsource != None:
                shaders.append(self._createShader(GL_GEOMETRY_SHADER, gsource))
            shaders.append(self._createShader(GL_FRAGMENT_SHADER, fsource))
            self.program = self._createProgram(shaders)
            # Flag shader for deletion.
        except:
            if self.program != None:
                glDeleteProgram(self.program)
            raise
        finally:
            for shader in shaders:
                try:
                    glDeleteShader(shader)
                except:
                    pass
    
    def _createShader(self, shadertype, source):
        try:
            shader = None
            shader = glCreateShader(shadertype)
            glShaderSource(shader, source)
            glCompileShader(shader)
            if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
                info = glGetShaderInfoLog(shader)
                raise Exception, "Unable to compile shader. Infolog:\n%s" % (info,)
            return shader
        except Exception:
            # Cleanup on exception
            if shader != None:
                glDeleteShader(shader)
            raise
    
    def _createProgram(self, shaders):
        prog = None
        try:
            prog = glCreateProgram()
            for shader in shaders: 
                glAttachShader(prog, shader)
            
            glLinkProgram(prog)            
            if glGetProgramiv(prog, GL_LINK_STATUS) != GL_TRUE:
                info = glGetProgramInfoLog(prog)
                raise Exception, "Unable to link program. Info log:\n%s" % (info)
            
            return prog
        except Exception:
            if prog != None:
                glDeleteProgram(prog)
            raise
        
    def use(self):
        glUseProgram(self.program)
        
    def uniformlocation(self, name):
        if name not in self.uniformlocs:
                self.uniformlocs[name] = glGetUniformLocation(self.program, name)
        return self.uniformlocs[name]
        
    def attributelocation(self, name):
        if name not in self.attributelocs:
                self.attributelocs[name] = glGetAttribLocation(self.program, name)
        return self.attributelocs[name]