# -*- coding: utf-8 -*-
##############################################################################
#
#  A boilerplate for small OpenGL/GLFW Demos. 
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
import time
import numpy as np
import threading
from glfw import *

OSX_CORE_PROFILE_HINTS = {GLFW_OPENGL_VERSION_MAJOR : 3,
                          GLFW_OPENGL_VERSION_MINOR : 2,
                          GLFW_OPENGL_PROFILE : GLFW_OPENGL_CORE_PROFILE,
                          GLFW_OPENGL_FORWARD_COMPAT : GL_TRUE}

class demoplate(threading.Thread):
    '''
    A small boiler plate for GLFW demos.
    '''

    def __init__(self, windowsize = (640, 480), windowhints = {}):
        super(demoplate, self).__init__()
        self.windowsize = windowsize
        self.windowhints = windowhints
        self.running = False
        self.mousepos = np.array([0, 0], dtype = np.int)
        self.mousediff = np.array([0, 0], dtype = np.int)
        self.mousewheelpos = 0

    def _initglfw(self):
        '''
        Initialiszes GLFW and opens the window.
        '''
        if not glfwInit():
            raise Exception, 'Unable to initialize GLFW.'
        
        for key, val in self.windowhints.items():
            glfwOpenWindowHint(key, val)

        if not glfwOpenWindow(self.windowsize[0], self.windowsize[1],
                              0, 0, 0, 0, 32, 0, GLFW_WINDOW):
            raise Exception, 'Unable to open window.'
    
    def _initcallbacks(self):
        glfwSetWindowSizeCallback(self.resize)
        glfwSetKeyCallback(self.keyboard)
        glfwSetMousePosCallback(self.mousemove)
        glfwSetMouseButtonCallback(self.mousebutton)
        glfwSetMouseWheelCallback(self.mousewheel)
        glfwEnable(GLFW_AUTO_POLL_EVENTS)
        
    def _cleanup(self):
        glfwTerminate()
        
    def run(self):
        '''
        Initializes glfw and runs the mainloop. 
        '''
        self._initglfw()
        self.running = True
        self.init()
        self._initcallbacks()
        t = time.time()
        try:
            while self.running:
                self.display(time.time() - t)
                t = time.time()
                glfwSwapBuffers()
                if not glfwGetWindowParam(GLFW_OPENED):
                    self.running = False
        except:
            self.running = False
            self._cleanup()
            raise
        
        self.cleanup()
        self._cleanup()
        
    def init(self):
        '''
        Called once before the main-loop.
        '''
        pass
    
    def cleanup(self):
        '''
        Called after the main-loop exits.
        '''
        pass
        
    def display(self, time):
        '''
        Called from the main-loop.
        Argument is the time (in seconds) passed since the last call.
        '''
        pass
        
    def resize(self, width, height):
        '''
        Called when the window resizes (and once on window init).
        '''
        pass
    
    def keyboard(self, key, action):
        '''
        Called on a keypress. Default: Close window on ESC.
        '''
        if key == GLFW_KEY_ESC:
            self.running = False
    
    def mousemove(self, x, y):
        '''
        Called when the mouse moves. Default: Stores the position/diff in the
        mousepos attribute.
        '''
        pos = np.array([x, y], dtype = np.int)
        self.mousediff = self.mousepos - pos
        self.mousepos = pos
        
    def mousebutton(self, button, action):
        '''
        Called when a mouse button is pressed.
        '''
        pass
    
    def mousewheel(self, wheelpos):
        '''
        Called when the mouse wheel is used. Default: Sets the mousewheelpos
        attribute.
        '''
        self.mousewheelpos = wheelpos
        