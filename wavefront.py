# -*- coding: utf-8 -*-
##############################################################################
# 
#  objreader - library for reading wavefront obj-files.
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
import re
import numpy as np

OBJFILE_FORMAT_V = 1
OBJFILE_FORMAT_VT = 3
OBJFILE_FORMAT_VN = 5
OBJFILE_FORMAT_VTN = 7

OBJFILE_FORMAT_V_BIT = 1
OBJFILE_FORMAT_N_BIT = 2
OBJFILE_FORMAT_T_BIT = 4

OBJFILE_V_REGEX = re.compile(r'(\d+)')
OBJFILE_VN_REGEX = re.compile(r'(\d+)//(\d+)')
OBJFILE_VT_REGEX = re.compile(r'(\d+)/(\d+)')
OBJFILE_VTN_REGEX = re.compile(r'(\d+)/(\d+)/(\d+)')

class ObjFileParser(object):
    """
    Parser for Wavefront Obj. Files.
    Supports v, vn, vt and f statements for now. Other statements are ignored.
    """
    def __init__(self, filename, padnormals = 4, padtexcoords = 4):
        self.padnormals = padnormals
        self.padtexcoords = padtexcoords
        self.v = []
        self.vn = []
        self.vt = []
        self.f = []
        self.o = {}
        self.g = {}
        
        handlers = {
            'v' : self._v, 
            'vn' : self._vn, 
            'vt' : self._vt,
            'f' : self._f,
            'vp' : self._vp,
#            'o' : self._o,
#            'g' : self._g
        }
        
        self.allfacesclean = True
        self.faceformat = None
        
        with open(filename, 'r') as f:
            i = 0
            for line in f:
                i += 1
                # Remove commentary
                line = line.split('#', 1)[0] 
                line = line.split(None, 1)
                if len(line) > 0:
                    if line[0] in handlers:
                        try:
                            handlers[line[0]](*line[1])
                        except Exception as e:
                            raise Exception, 'Parsing error at line %i: %s' % (i, e)
        
        if not self.allfacesclean:
            self._cleanfaces()
        del self.allfacesclean
    
    def _v(self, args):
        args = args.split()
        if len(args) not in [3, 4]:
            raise Exception, 'Vertex must have 3 or 4 parameters.'
        x, y, z = float(args[0]), float(args[1]) , float(args[2])
        w = 1.0
        if len(args) == 4:
            w = float(args[3])
        v = np.array([x,y,z,w], dtype=np.float32)
        self.v.append(v)
        
    def _vn(self, args):
        args = args.split()
        if len(args) != 3:
            raise Exception, 'Normals must have 3 parameters.'
        x, y, z = float(args[0]), float(args[1]) , float(args[2])
        vn = np.array([x, y, z], dtype=np.float32)
        # Normalize
        norm = np.linalg.norm(vn)
        if norm == 0.0:
            raise Exception, 'Invalid normal.'
        vn /= norm
        if vn.shape[0] < self.padnormals:
            vn = np.concatenate([vn,
                np.zeros(self.padnormals - vn.shape[0], dtype=np.float32)])
        self.vn.append(vn)
        
    def _vt(self, args):
        args = args.split()
        if len(args) not in [2, 3]:
            raise Exception, 'Texturecoordinates must have 2 or 3 parameters.'
        u, v, w = float(args[0]), float(args[1]), 0.0 if len(args) == 2 else float(args[2])
        vt = np.array([u,v,w], dtype=np.float32)
        if vt.shape[0] < self.padtexcoords:
            vt = np.concatenate([vt,
                np.zeros(self.padtexcoords - vt.shape[0], dtype=np.float32)])
        self.vt.append(vt)
    
    def _f(self, args):
        args = args.split()
        if len(args) < 3:
            raise Exception, 'A face must have at least 3 vertices.'
        if len(args) > 3:
            raise NotImplementedError, 'More than 4 vertices not supported yet.'
        # Determine the faceformat and split it.
        faceformat = None
        face = []
        if '//' in args[0]:
            faceformat = OBJFILE_FORMAT_VN
            for arg in args:
                arg = arg.split('//')
                face.append((int(arg[0])-1, int(arg[1])-1, None))
        else:
            if '/' in args[0]:
                args = [arg.split('/') for arg in args]
                if len(args[0]) == 3:
                    faceformat = OBJFILE_FORMAT_VTN
                    for arg in args:                        
                        face.append((int(arg[0])-1, int(arg[2])-1, int(arg[1])-1))
                else:
                    faceformat = OBJFILE_FORMAT_VT
                    for arg in args:
                        face.append((int(arg[0])-1, None, int(arg[1])-1))                    
            else:
                faceformat = OBJFILE_FORMAT_V
                for arg in args:
                    face.append((int(arg)-1, None, None))
                
            
        # Check faceformat.
        if self.faceformat != None and faceformat != self.faceformat:
            raise Exception, 'All faces must have the same faceformat.'
        else:
            self.faceformat = faceformat
        
        # Check if all indices are valid.
        for v in face:
            if v[0] >= len(self.v):
                raise Exception, 'Invalid vertex position index.'
            if v[1] >= 0 and v[1] >= len(self.vn):
                raise Exception, 'Invalid vertex normal index.'
            if v[2] >= 0 and v[2] >= len(self.vt):
                raise Exception, 'Invalid vertex texture coordinate index.'
        
        # Check if all the indices are the same.
        cleanface = []
        for vert in face:
            if all(attr == None or attr == vert[0] for attr in vert):
                # Only add the first index if the vertex is clean, otherwise
                # the tuple.
                vert = vert[0]
            else:
                self.allfacesclean = False
            cleanface.append(vert)
            
        self.f.append(cleanface)
                
    def _vp(self, args):
        raise NotImplementedError, 'Parameter space not implemented.'
        
    def _o(self, args):
        position = len(self.f)
        self.o[args] = position
        
    def _g(self, args):
        position = len(self.f)
        self.g[args] = position
        
    def _cleanfaces(self):
        """
        Cleans up all the faces by generating new v/vn/vt/f buffers.
        The code simply finds all unique face edges and generates the
        appropriate v/vn/vt and a new f. The reasoning behind this is, that
        OpenGL needs all the 
        """
        nv, nvn, nvt, nf = [], [], [], []
        cleanedverts = {}
        
        # V format doesn't need to be cleaned!
        def addvn(vert):
            nv.append(self.v[vert[0]])
            nvn.append(self.vn[vert[1]])
        def addvt(vert):
            nv.append(self.v[vert[0]])
            nvt.append(self.vt[vert[2]])
        def addvtn(vert):
            nv.append(self.v[vert[0]])
            nvn.append(self.vn[vert[1]])
            nvt.append(self.vt[vert[2]])            
        
        addvert = None
        if self.faceformat == OBJFILE_FORMAT_VN:
            addvert = addvn
        elif self.faceformat == OBJFILE_FORMAT_VT:
            addvert = addvt
        elif self.faceformat == OBJFILE_FORMAT_VTN:
            addvert = addvtn
        
        for face in self.f:
            newface = []
            for oldvert in face:
                if oldvert not in cleanedverts:
                    i = len(nv)
                    if isinstance(oldvert, int):
                        oldvert = (oldvert, oldvert, oldvert)
                    addvert(oldvert)
                    cleanedverts[oldvert] = i
                    newvert = i
                else:
                    newvert = cleanedverts[oldvert]
                newface.append(newvert)
            nf.append(newface)    
        
        self.v, self.vn, self.vt, self.f = nv, nvn, nvt, nf
                
    def hasnormals(self):
        return self.faceformat & OBJFILE_FORMAT_N_BIT > 0
        
    def hastexturecoords(self):
        return self.faceformat & OBJFILE_FORMAT_T_BIT > 0
        
    def generateIndexedBuffer(self, layout = [0,1], itype = None):
        """
        Generates a VBO and IBO for OpenGL.
        
        Arguments:
        layout -- layout for the vertex-attributes. list of integers with 0=pos, 1=normal, 2=texcoord
        itype -- numpy type for IBO (determines the minimum required type if None)
        """
        # Build the vertices buffer by simply concatenating data:
        vertices = []
        for vertex in zip(self.v, self.vn, self.vt):
            vertexdata = []
            for attr in layout:
                vertexdata.append(vertex[attr])
            vertices.append(np.concatenate(vertexdata))
        vertexbuffer = np.concatenate(vertices)
        
        if itype == None:
            if len(self.v) < 256:
                itype = np.uint8
            elif len(self.v) < 65536:
                itype = np.uint16
            else:
                itype = np.uint32
            
        indexbuffer = np.zeros(len(self.f) * 3, dtype=itype)
        i = 0
        for face in self.f:
            for vert in face:
                indexbuffer[i] = vert
                i += 1
        return vertexbuffer, indexbuffer