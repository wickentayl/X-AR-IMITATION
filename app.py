from __future__ import annotations


import builtins

import contextlib

import ctypes

import datetime

import functools

import json

import math

import os

import select

import signal

import socket

import struct

import sys

import termios

import threading

import time

import traceback

import tty

from collections import deque

from dataclasses import dataclass

from multiprocessing import resource_tracker, shared_memory

from typing import Any

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

_PARENT_MODULE_DIR = os.path.dirname(_MODULE_DIR)

for _path in (_MODULE_DIR, _PARENT_MODULE_DIR):

    if _path and _path not in sys.path:

        sys.path.insert(0, _path)


builtins.print = functools.partial(print, flush=True)


def _load_ctypes_gl_fallback() -> None:

    libgl = ctypes.CDLL("libGL.so.1")

    try:

        libglu = ctypes.CDLL("libGLU.so.1")

    except Exception:

        libglu = None

    def _bind(lib, name, restype=None, argtypes=None, required=True):

        try:

            fn = getattr(lib, name)

        except AttributeError:

            if required:

                raise

            return None

        fn.restype = restype

        fn.argtypes = argtypes

        return fn

    constants = {
        "GL_LIGHTING": 0x0B50,
        "GL_TEXTURE_2D": 0x0DE1,
        "GL_LINES": 0x0001,
        "GL_ENABLE_BIT": 0x00002000,
        "GL_DEPTH_TEST": 0x0B71,
        "GL_LIGHT0": 0x4000,
        "GL_COLOR_MATERIAL": 0x0B57,
        "GL_POSITION": 0x1203,
        "GL_PACK_ALIGNMENT": 0x0D05,
        "GL_COLOR_BUFFER_BIT": 0x00004000,
        "GL_DEPTH_BUFFER_BIT": 0x00000100,
        "GL_PROJECTION": 0x1701,
        "GL_MODELVIEW": 0x1700,
        "GL_RGB": 0x1907,
        "GL_RGBA": 0x1908,
        "GL_UNSIGNED_BYTE": 0x1401,
        "GL_LINEAR": 0x2601,
        "GL_REPEAT": 0x2901,
        "GL_CLAMP_TO_EDGE": 0x812F,
        "GL_UNPACK_ALIGNMENT": 0x0CF5,
        "GL_BLEND": 0x0BE2,
        "GL_SRC_ALPHA": 0x0302,
        "GL_ONE_MINUS_SRC_ALPHA": 0x0303,
        "GL_ALPHA_TEST": 0x0BC0,
        "GL_GREATER": 0x0204,
        "GL_QUADS": 0x0007,
        "GL_TRIANGLES": 0x0004,
        "GL_COMPILE": 0x1300,
        "GL_TEXTURE_MIN_FILTER": 0x2801,
        "GL_TEXTURE_MAG_FILTER": 0x2800,
        "GL_TEXTURE_WRAP_S": 0x2802,
        "GL_TEXTURE_WRAP_T": 0x2803,
        "GL_DITHER": 0x0BD0,
    }

    globals().update(constants)

    _glDisable = _bind(libgl, "glDisable", None, [ctypes.c_uint])

    _glEnable = _bind(libgl, "glEnable", None, [ctypes.c_uint])

    _glLineWidth = _bind(libgl, "glLineWidth", None, [ctypes.c_float])

    _glBegin = _bind(libgl, "glBegin", None, [ctypes.c_uint])

    _glEnd = _bind(libgl, "glEnd", None, [])

    _glColor3f = _bind(
        libgl, "glColor3f", None, [ctypes.c_float, ctypes.c_float, ctypes.c_float]
    )

    _glColor4f = _bind(
        libgl,
        "glColor4f",
        None,
        [ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float],
    )

    _glVertex2f = _bind(libgl, "glVertex2f", None, [ctypes.c_float, ctypes.c_float])

    _glVertex3f = _bind(
        libgl, "glVertex3f", None, [ctypes.c_float, ctypes.c_float, ctypes.c_float]
    )

    _glNormal3f = _bind(
        libgl, "glNormal3f", None, [ctypes.c_float, ctypes.c_float, ctypes.c_float]
    )

    _glTexCoord2f = _bind(libgl, "glTexCoord2f", None, [ctypes.c_float, ctypes.c_float])

    _glPushAttrib = _bind(libgl, "glPushAttrib", None, [ctypes.c_uint])

    _glPopAttrib = _bind(libgl, "glPopAttrib", None, [])

    _glPushMatrix = _bind(libgl, "glPushMatrix", None, [])

    _glTranslatef = _bind(
        libgl, "glTranslatef", None, [ctypes.c_float, ctypes.c_float, ctypes.c_float]
    )

    _glRotatef = _bind(
        libgl,
        "glRotatef",
        None,
        [ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float],
    )

    _glScalef = _bind(
        libgl, "glScalef", None, [ctypes.c_float, ctypes.c_float, ctypes.c_float]
    )

    _glPopMatrix = _bind(libgl, "glPopMatrix", None, [])

    _glClear = _bind(libgl, "glClear", None, [ctypes.c_uint])

    _glClearColor = _bind(
        libgl,
        "glClearColor",
        None,
        [ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float],
    )

    _glMatrixMode = _bind(libgl, "glMatrixMode", None, [ctypes.c_uint])

    _glLoadIdentity = _bind(libgl, "glLoadIdentity", None, [])

    _glLoadMatrixf = _bind(
        libgl, "glLoadMatrixf", None, [ctypes.POINTER(ctypes.c_float)]
    )

    _glLightfv = _bind(
        libgl,
        "glLightfv",
        None,
        [ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_float)],
    )

    _glPixelStorei = _bind(libgl, "glPixelStorei", None, [ctypes.c_uint, ctypes.c_int])

    _glBindTexture = _bind(libgl, "glBindTexture", None, [ctypes.c_uint, ctypes.c_uint])

    _glTexParameteri = _bind(
        libgl, "glTexParameteri", None, [ctypes.c_uint, ctypes.c_uint, ctypes.c_int]
    )

    _glBlendFunc = _bind(libgl, "glBlendFunc", None, [ctypes.c_uint, ctypes.c_uint])

    _glAlphaFunc = _bind(libgl, "glAlphaFunc", None, [ctypes.c_uint, ctypes.c_float])

    _glOrtho = _bind(
        libgl,
        "glOrtho",
        None,
        [
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
        ],
    )

    _glNewList = _bind(libgl, "glNewList", None, [ctypes.c_uint, ctypes.c_uint])

    _glEndList = _bind(libgl, "glEndList", None, [])

    _glCallList = _bind(libgl, "glCallList", None, [ctypes.c_uint])

    _glGenLists = _bind(libgl, "glGenLists", ctypes.c_uint, [ctypes.c_int])

    _glReadPixels = _bind(
        libgl,
        "glReadPixels",
        None,
        [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_void_p,
        ],
    )

    _glGenTextures_c = _bind(
        libgl, "glGenTextures", None, [ctypes.c_int, ctypes.POINTER(ctypes.c_uint)]
    )

    _glTexImage2D_c = _bind(
        libgl,
        "glTexImage2D",
        None,
        [
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_void_p,
        ],
    )

    _glTexSubImage2D_c = _bind(
        libgl,
        "glTexSubImage2D",
        None,
        [
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_void_p,
        ],
    )

    def glDisable(x):

        _glDisable(int(x))

    def glEnable(x):

        _glEnable(int(x))

    def glLineWidth(x):

        _glLineWidth(float(x))

    def glBegin(x):

        _glBegin(int(x))

    def glEnd():

        _glEnd()

    def glColor3f(a, b, c):

        _glColor3f(float(a), float(b), float(c))

    def glColor4f(a, b, c, d):

        _glColor4f(float(a), float(b), float(c), float(d))

    def glColor4fv(v):

        glColor4f(v[0], v[1], v[2], v[3] if len(v) > 3 else 1.0)

    def glVertex2f(a, b):

        _glVertex2f(float(a), float(b))

    def glVertex3f(a, b, c):

        _glVertex3f(float(a), float(b), float(c))

    def glVertex3fv(v):

        glVertex3f(v[0], v[1], v[2])

    def glNormal3f(a, b, c):

        _glNormal3f(float(a), float(b), float(c))

    def glNormal3fv(v):

        glNormal3f(v[0], v[1], v[2])

    def glTexCoord2f(a, b):

        _glTexCoord2f(float(a), float(b))

    def glTexCoord2fv(v):

        glTexCoord2f(v[0], v[1])

    def glPushAttrib(x):

        _glPushAttrib(int(x))

    def glPopAttrib():

        _glPopAttrib()

    def glPushMatrix():

        _glPushMatrix()

    def glTranslatef(a, b, c):

        _glTranslatef(float(a), float(b), float(c))

    def glRotatef(a, b, c, d):

        _glRotatef(float(a), float(b), float(c), float(d))

    def glScalef(a, b, c):

        _glScalef(float(a), float(b), float(c))

    def glPopMatrix():

        _glPopMatrix()

    def glClear(x):

        _glClear(int(x))

    def glClearColor(a, b, c, d):

        _glClearColor(float(a), float(b), float(c), float(d))

    def glMatrixMode(x):

        _glMatrixMode(int(x))

    def glLoadIdentity():

        _glLoadIdentity()

    def glLoadMatrixf(m):

        arr = np.asarray(m, dtype=np.float32).ravel()

        _glLoadMatrixf(arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))

    def glLightfv(light, pname, values):

        arr = np.asarray(values, dtype=np.float32)

        _glLightfv(
            int(light), int(pname), arr.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        )

    def glPixelStorei(pname, value):

        _glPixelStorei(int(pname), int(value))

    def glBindTexture(target, tex):

        _glBindTexture(int(target), int(tex))

    def glTexParameteri(target, pname, value):

        _glTexParameteri(int(target), int(pname), int(value))

    def glBlendFunc(a, b):

        _glBlendFunc(int(a), int(b))

    def glAlphaFunc(func, ref):

        _glAlphaFunc(int(func), float(ref))

    def glOrtho(l, r, b, t, n, f):

        _glOrtho(float(l), float(r), float(b), float(t), float(n), float(f))

    def glNewList(lst, mode):

        _glNewList(int(lst), int(mode))

    def glEndList():

        _glEndList()

    def glCallList(lst):

        _glCallList(int(lst))

    def glGenLists(n):

        return int(_glGenLists(int(n)))

    def glGenTextures(n):

        buf = (ctypes.c_uint * int(n))()

        _glGenTextures_c(int(n), buf)

        return int(buf[0]) if int(n) == 1 else [int(x) for x in buf]

    def glTexImage2D(
        target, level, internal_format, width, height, border, fmt, tp, pixels
    ):

        keepalive = None

        ptr = None

        if pixels is not None:

            if isinstance(pixels, np.ndarray):

                keepalive = np.ascontiguousarray(pixels)

                ptr = keepalive.ctypes.data_as(ctypes.c_void_p)

            elif isinstance(pixels, (bytes, bytearray)):

                keepalive = ctypes.create_string_buffer(bytes(pixels))

                ptr = ctypes.cast(keepalive, ctypes.c_void_p)

            else:

                try:

                    keepalive = bytes(pixels)

                    keepalive = ctypes.create_string_buffer(keepalive)

                    ptr = ctypes.cast(keepalive, ctypes.c_void_p)

                except Exception:

                    ptr = None

        _glTexImage2D_c(
            int(target),
            int(level),
            int(internal_format),
            int(width),
            int(height),
            int(border),
            int(fmt),
            int(tp),
            ptr,
        )

    def glTexSubImage2D(
        target, level, xoffset, yoffset, width, height, fmt, tp, pixels
    ):

        keepalive = None

        ptr = None

        if pixels is not None:

            if isinstance(pixels, np.ndarray):

                keepalive = np.ascontiguousarray(pixels)

                ptr = keepalive.ctypes.data_as(ctypes.c_void_p)

            elif isinstance(pixels, (bytes, bytearray)):

                keepalive = ctypes.create_string_buffer(bytes(pixels))

                ptr = ctypes.cast(keepalive, ctypes.c_void_p)

            else:

                try:

                    keepalive = bytes(pixels)

                    keepalive = ctypes.create_string_buffer(keepalive)

                    ptr = ctypes.cast(keepalive, ctypes.c_void_p)

                except Exception:

                    ptr = None

        _glTexSubImage2D_c(
            int(target),
            int(level),
            int(xoffset),
            int(yoffset),
            int(width),
            int(height),
            int(fmt),
            int(tp),
            ptr,
        )

    def glReadPixels(x, y, width, height, fmt, tp):

        channels = 4 if int(fmt) == GL_RGBA else 3

        size = int(width) * int(height) * channels

        buf = (ctypes.c_ubyte * size)()

        _glReadPixels(
            int(x),
            int(y),
            int(width),
            int(height),
            int(fmt),
            int(tp),
            ctypes.cast(buf, ctypes.c_void_p),
        )

        return bytes(buf)

    if libglu is not None:

        _gluLookAt = _bind(
            libglu,
            "gluLookAt",
            None,
            [
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
            ],
            required=False,
        )

        _gluNewQuadric = _bind(
            libglu, "gluNewQuadric", ctypes.c_void_p, [], required=False
        )

        _gluSphere = _bind(
            libglu,
            "gluSphere",
            None,
            [ctypes.c_void_p, ctypes.c_double, ctypes.c_int, ctypes.c_int],
            required=False,
        )

    else:

        _gluLookAt = _gluNewQuadric = _gluSphere = None

    def gluLookAt(ex, ey, ez, cx, cy, cz, ux, uy, uz):

        if _gluLookAt is not None:

            _gluLookAt(
                float(ex),
                float(ey),
                float(ez),
                float(cx),
                float(cy),
                float(cz),
                float(ux),
                float(uy),
                float(uz),
            )

            return

        eye = np.array([ex, ey, ez], dtype=np.float32)

        center = np.array([cx, cy, cz], dtype=np.float32)

        up = np.array([ux, uy, uz], dtype=np.float32)

        f = center - eye

        f /= max(np.linalg.norm(f), 1e-6)

        s = np.cross(f, up)

        s /= max(np.linalg.norm(s), 1e-6)

        u = np.cross(s, f)

        m = np.array(
            [
                [s[0], u[0], -f[0], 0.0],
                [s[1], u[1], -f[1], 0.0],
                [s[2], u[2], -f[2], 0.0],
                [-np.dot(s, eye), -np.dot(u, eye), np.dot(f, eye), 1.0],
            ],
            dtype=np.float32,
        )

        glLoadMatrixf(m.T)

    def gluNewQuadric():

        if _gluNewQuadric is not None:

            return _gluNewQuadric()

        return None

    def gluSphere(quadric, radius, slices, stacks):

        if _gluSphere is not None and quadric:

            _gluSphere(quadric, float(radius), int(slices), int(stacks))

            return

        return None

    globals().update(
        {
            "glDisable": glDisable,
            "glEnable": glEnable,
            "glLineWidth": glLineWidth,
            "glBegin": glBegin,
            "glEnd": glEnd,
            "glColor3f": glColor3f,
            "glColor4f": glColor4f,
            "glColor4fv": glColor4fv,
            "glVertex2f": glVertex2f,
            "glVertex3f": glVertex3f,
            "glVertex3fv": glVertex3fv,
            "glNormal3f": glNormal3f,
            "glNormal3fv": glNormal3fv,
            "glTexCoord2f": glTexCoord2f,
            "glTexCoord2fv": glTexCoord2fv,
            "glPushAttrib": glPushAttrib,
            "glPopAttrib": glPopAttrib,
            "glPushMatrix": glPushMatrix,
            "glTranslatef": glTranslatef,
            "glRotatef": glRotatef,
            "glScalef": glScalef,
            "glPopMatrix": glPopMatrix,
            "glClear": glClear,
            "glClearColor": glClearColor,
            "glMatrixMode": glMatrixMode,
            "glLoadIdentity": glLoadIdentity,
            "glLoadMatrixf": glLoadMatrixf,
            "glLightfv": glLightfv,
            "glPixelStorei": glPixelStorei,
            "glBindTexture": glBindTexture,
            "glTexParameteri": glTexParameteri,
            "glTexImage2D": glTexImage2D,
            "glTexSubImage2D": glTexSubImage2D,
            "glBlendFunc": glBlendFunc,
            "glAlphaFunc": glAlphaFunc,
            "glOrtho": glOrtho,
            "glNewList": glNewList,
            "glEndList": glEndList,
            "glCallList": glCallList,
            "glGenLists": glGenLists,
            "glGenTextures": glGenTextures,
            "glReadPixels": glReadPixels,
            "gluLookAt": gluLookAt,
            "gluNewQuadric": gluNewQuadric,
            "gluSphere": gluSphere,
        }
    )


try:

    import glfw

except Exception:

    glfw = None


try:

    import numpy as np

except Exception:

    np = None


try:

    import cv2

except Exception:

    cv2 = None


try:

    from smbus2 import SMBus

except Exception:

    SMBus = None


try:

    from OpenGL.GL import *

    from OpenGL.GLU import *

    _opengl_gl = __import__("OpenGL.GL", fromlist=["*"])

    _opengl_glu = __import__("OpenGL.GLU", fromlist=["*"])

    globals().update(
        {
            name: getattr(_opengl_gl, name)
            for name in dir(_opengl_gl)
            if not name.startswith("_")
        }
    )

    globals().update(
        {
            name: getattr(_opengl_glu, name)
            for name in dir(_opengl_glu)
            if not name.startswith("_")
        }
    )

    _required_gl_names = [
        "glDisable",
        "glEnable",
        "glLineWidth",
        "glBegin",
        "glColor3f",
        "glColor4f",
        "glColor4fv",
        "glVertex2f",
        "glVertex3f",
        "glVertex3fv",
        "glNormal3f",
        "glNormal3fv",
        "glTexCoord2f",
        "glTexCoord2fv",
        "glEnd",
        "glPushAttrib",
        "glPopAttrib",
        "glPushMatrix",
        "glTranslatef",
        "glRotatef",
        "glScalef",
        "glPopMatrix",
        "glClear",
        "glClearColor",
        "glMatrixMode",
        "glLoadIdentity",
        "glLoadMatrixf",
        "glLightfv",
        "glPixelStorei",
        "glBindTexture",
        "glTexParameteri",
        "glTexImage2D",
        "glTexSubImage2D",
        "glBlendFunc",
        "glAlphaFunc",
        "glOrtho",
        "glNewList",
        "glEndList",
        "glCallList",
        "glReadPixels",
        "glGenTextures",
        "glGenLists",
        "GL_LIGHTING",
        "GL_TEXTURE_2D",
        "GL_LINES",
        "GL_ENABLE_BIT",
        "GL_DEPTH_TEST",
        "GL_LIGHT0",
        "GL_COLOR_MATERIAL",
        "GL_POSITION",
        "GL_PACK_ALIGNMENT",
        "GL_COLOR_BUFFER_BIT",
        "GL_DEPTH_BUFFER_BIT",
        "GL_PROJECTION",
        "GL_MODELVIEW",
        "GL_RGB",
        "GL_RGBA",
        "GL_UNSIGNED_BYTE",
        "GL_LINEAR",
        "GL_REPEAT",
        "GL_CLAMP_TO_EDGE",
        "GL_UNPACK_ALIGNMENT",
        "GL_BLEND",
        "GL_SRC_ALPHA",
        "GL_ONE_MINUS_SRC_ALPHA",
        "GL_ALPHA_TEST",
        "GL_GREATER",
        "GL_QUADS",
        "GL_TRIANGLES",
        "GL_COMPILE",
        "GL_TEXTURE_MIN_FILTER",
        "GL_TEXTURE_MAG_FILTER",
        "GL_TEXTURE_WRAP_S",
        "GL_TEXTURE_WRAP_T",
        "GL_DITHER",
    ]

    for _name in _required_gl_names:

        if _name not in globals():

            try:

                globals()[_name] = getattr(_opengl_gl, _name)

            except Exception:

                pass

    for _name in ("gluLookAt", "gluNewQuadric", "gluSphere"):

        if _name not in globals():

            try:

                globals()[_name] = getattr(_opengl_glu, _name)

            except Exception:

                pass

    if "glEnable" not in globals():

        _load_ctypes_gl_fallback()

    OPENGL_AVAILABLE = True

except Exception:

    OPENGL_AVAILABLE = False

    def _gl_noop(*args, **kwargs):

        return None

    def glReadPixels(*args, **kwargs):

        return b""

    def glGenTextures(*args, **kwargs):

        return 0

    def glGenLists(*args, **kwargs):

        return 0

    glDisable = _gl_noop

    glEnable = _gl_noop

    glLineWidth = _gl_noop

    glBegin = _gl_noop

    glColor3f = _gl_noop

    glColor4f = _gl_noop

    glColor4fv = _gl_noop

    glVertex2f = _gl_noop

    glVertex3f = _gl_noop

    glVertex3fv = _gl_noop

    glNormal3f = _gl_noop

    glNormal3fv = _gl_noop

    glTexCoord2f = _gl_noop

    glTexCoord2fv = _gl_noop

    glEnd = _gl_noop

    glPushAttrib = _gl_noop

    glPopAttrib = _gl_noop

    glPushMatrix = _gl_noop

    glTranslatef = _gl_noop

    glRotatef = _gl_noop

    glScalef = _gl_noop

    glPopMatrix = _gl_noop

    glClear = _gl_noop

    glClearColor = _gl_noop

    glMatrixMode = _gl_noop

    glLoadIdentity = _gl_noop

    glLoadMatrixf = _gl_noop

    glLightfv = _gl_noop

    glPixelStorei = _gl_noop

    glBindTexture = _gl_noop

    glTexParameteri = _gl_noop

    glTexImage2D = _gl_noop

    glTexSubImage2D = _gl_noop

    glBlendFunc = _gl_noop

    glAlphaFunc = _gl_noop

    glOrtho = _gl_noop

    glNewList = _gl_noop

    glEndList = _gl_noop

    glCallList = _gl_noop

    gluLookAt = _gl_noop

    def gluNewQuadric():
        return None

    gluSphere = _gl_noop

    GL_LIGHTING = 0

    GL_TEXTURE_2D = 0

    GL_LINES = 0

    GL_ENABLE_BIT = 0

    GL_DEPTH_TEST = 0

    GL_LIGHT0 = 0

    GL_COLOR_MATERIAL = 0

    GL_POSITION = 0

    GL_PACK_ALIGNMENT = 0

    GL_COLOR_BUFFER_BIT = 0

    GL_DEPTH_BUFFER_BIT = 0

    GL_PROJECTION = 0

    GL_MODELVIEW = 0

    GL_RGB = 0

    GL_RGBA = 0

    GL_UNSIGNED_BYTE = 0

    GL_LINEAR = 0

    GL_REPEAT = 0

    GL_CLAMP_TO_EDGE = 0

    GL_UNPACK_ALIGNMENT = 0

    GL_BLEND = 0

    GL_SRC_ALPHA = 0

    GL_ONE_MINUS_SRC_ALPHA = 0

    GL_ALPHA_TEST = 0

    GL_GREATER = 0

    GL_QUADS = 0

    GL_TRIANGLES = 0

    GL_COMPILE = 0

    GL_TEXTURE_MIN_FILTER = 0

    GL_TEXTURE_MAG_FILTER = 0

    GL_TEXTURE_WRAP_S = 0

    GL_TEXTURE_WRAP_T = 0

    GL_DITHER = 0


THIS_DIR = os.path.dirname(os.path.abspath(__file__))

FALLBACK_ASSET_DIR = os.path.join(THIS_DIR, "ENTIRE", "setupUI", "dist")


class _NullKeyPoller:

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc, tb):

        return False

    def poll(self):

        return None


def _first_existing_file(*paths: str) -> str:

    for path in paths:

        if path and os.path.isfile(path):

            return path

    return paths[0] if paths else ""


def _first_existing_dir(*paths: str) -> str:

    for path in paths:

        if path and os.path.isdir(path):

            return path

    return paths[0] if paths else ""


def find_base_dir() -> str:

    candidates = []

    if getattr(sys, "frozen", False):

        try:

            candidates.append(os.path.dirname(os.path.abspath(sys.executable)))

        except Exception:

            pass

    try:

        candidates.append(os.path.dirname(os.path.abspath(__file__)))

    except Exception:

        pass

    candidates.append(os.getcwd())

    for start_path in candidates:

        current = start_path

        while current:

            if os.path.exists(
                os.path.join(current, "main_config.json")
            ) or os.path.exists(os.path.join(current, "objects.json")):

                return current

            parent = os.path.dirname(current)

            if parent == current:

                break

            current = parent

    return os.getcwd()


BASE_DIR = find_base_dir()

CONFIG_FILE = os.path.join(BASE_DIR, "main_config.json")

OBJECT_JSON_FILE = os.path.join(BASE_DIR, "objects.json")

MODEL_DIR = _first_existing_dir(
    os.environ.get("AR_MODEL_DIR", ""),
    os.path.join(os.path.dirname(BASE_DIR), "models"),
    os.path.join(BASE_DIR, "models"),
    os.path.join(FALLBACK_ASSET_DIR, "models"),
)

ASSET_DIR = _first_existing_dir(BASE_DIR, FALLBACK_ASSET_DIR)

MAP_FILE = _first_existing_file(
    os.path.join(BASE_DIR, "map.png"), os.path.join(FALLBACK_ASSET_DIR, "map.png")
)

TRACK_MASK_FILE = _first_existing_file(
    os.path.join(BASE_DIR, "track_mask.png"),
    os.path.join(FALLBACK_ASSET_DIR, "track_mask.png"),
)


def load_config() -> dict[str, Any]:

    cfg = {
        "device_name": "/dev/video0",
        "width": 640,
        "height": 480,
        "video_flip": {
            "horizontal": False,
            "vertical": True,
        },
        "K": [[320, 0, 320], [0, 320, 240], [0, 0, 1]],
        "D": [0, 0, 0, 0, 0],
        "network": {
            "object_update_port": 9002,
            "stream_port": 8080,
            "control_port": 9999,
            "udp_target_ip": "192.168.x.x",
            "udp_target_port": 9000,
            "unity_sync_port": 9003,
            "unity_target_ip": "127.0.0.1",
            "sync_rate": 30,
            "imu_send_rate": 50,
            "movement_delay_ms": 0,
        },
    }

    if os.path.exists(CONFIG_FILE):

        try:

            with open(CONFIG_FILE, "r") as f:

                loaded = json.load(f)

            cfg.update({k: v for k, v in loaded.items() if k != "network"})

            if "network" in loaded:

                cfg["network"].update(loaded["network"])

            print(f"[CONFIG] Loaded from {CONFIG_FILE}")

        except Exception as exc:

            print(f"[CONFIG] Error loading file: {exc}, using defaults.")

    return cfg


SYS_CONFIG = load_config()

NET_CONFIG = SYS_CONFIG["network"]

MOVEMENT_DELAY = max(
    0.0,
    min(float(NET_CONFIG.get("movement_delay_ms", 0)) / 1000.0, 0.5),
)

WINDOW_WIDTH = int(SYS_CONFIG["width"])

WINDOW_HEIGHT = int(SYS_CONFIG["height"])

VIDEO_FLIP_CONFIG = SYS_CONFIG.get("video_flip", {})

VIDEO_FLIP_HORIZONTAL = bool(VIDEO_FLIP_CONFIG.get("horizontal", False))

VIDEO_FLIP_VERTICAL = bool(VIDEO_FLIP_CONFIG.get("vertical", True))

CAMERA_MATRIX = (
    np.array(SYS_CONFIG["K"], dtype=np.float64) if np is not None else SYS_CONFIG["K"]
)

DIST_COEFFS = (
    np.array(SYS_CONFIG["D"], dtype=np.float64) if np is not None else SYS_CONFIG["D"]
)

SHM_NAME = "shm_ar_video"

SHM_BACK_PREFIX = f"_{SHM_NAME}_back_"

SHM_HEADER_SIZE = 16

SHM_SIZE = SHM_HEADER_SIZE + WINDOW_WIDTH * WINDOW_HEIGHT * 3

RENDER_FPS = float(os.environ.get("AR_RENDER_FPS", NET_CONFIG.get("render_fps", 60)))

RENDER_INTERVAL = 0.0 if RENDER_FPS <= 0 else 1.0 / max(1.0, RENDER_FPS)

STREAM_JPEG_QUALITY = int(
    os.environ.get("AR_STREAM_JPEG_QUALITY", NET_CONFIG.get("stream_jpeg_quality", 50))
)

STREAM_JPEG_QUALITY = max(1, min(95, STREAM_JPEG_QUALITY))

STREAM_FPS = float(os.environ.get("AR_STREAM_FPS", NET_CONFIG.get("stream_fps", 20)))

STREAM_INTERVAL = 1.0 / max(1.0, STREAM_FPS)

STREAM_IDLE_SLEEP = 0.005

SHM_FPS = float(os.environ.get("AR_SHM_FPS", NET_CONFIG.get("shm_fps", 30)))

SHM_INTERVAL = 0.0 if SHM_FPS <= 0 else 1.0 / max(1.0, SHM_FPS)

SHM_BUFFER_COUNT = max(
    1, int(os.environ.get("AR_SHM_BUFFERS", NET_CONFIG.get("shm_buffers", 3)))
)

FPS_STATS_ENABLED = os.environ.get("AR_FPS_STATS", "").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

SWAP_BUFFERS = os.environ.get("AR_SWAP_BUFFERS", "0").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

REFEREE_FLUSH_INTERVAL = float(
    os.environ.get(
        "AR_REFEREE_FLUSH_INTERVAL",
        NET_CONFIG.get("referee_flush_interval", 0.5),
    )
)

I2C_BUS_NUM = 3

ICM_ADDR = 105

ACCEL_SENS = 2048.0

GYRO_SENS = 16.4

DEG2RAD = math.pi / 180.0

RAD2DEG = 180.0 / math.pi

Kp = 8.0

Ki = 0.01

GYRO_DEADZONE = 0.02


class KeyPoller:

    def __enter__(self):

        self.fd = sys.stdin.fileno()

        self.old_settings = termios.tcgetattr(self.fd)

        try:

            tty.setcbreak(self.fd)

        except Exception:

            pass

        return self

    def __exit__(self, exc_type, exc, tb):

        try:

            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

        except Exception:

            pass

    def poll(self):

        if select.select([sys.stdin], [], [], 0)[0]:

            return sys.stdin.read(1)

        return None


def get_opengl_projection_matrix(K, w, h, near=0.1, far=100.0):

    fx = K[0][0] if np is None else K[0, 0]

    fy = K[1][1] if np is None else K[1, 1]

    cx = K[0][2] if np is None else K[0, 2]

    cy = K[1][2] if np is None else K[1, 2]

    if np is not None:

        m = np.zeros((4, 4))

    else:

        m = [[0.0] * 4 for _ in range(4)]

    m[0][0] = 2.0 * fx / w

    m[1][1] = 2.0 * fy / h

    m[0][2] = 1.0 - 2.0 * cx / w

    m[1][2] = -(1.0 - 2.0 * cy / h)

    m[2][2] = -(far + near) / (far - near)

    m[2][3] = -(2.0 * far * near) / (far - near)

    m[3][2] = -1.0

    m[3][3] = 0.0

    return m.T if np is not None else m


class ICM42688:

    def __init__(self, bus_num):

        try:

            self.bus = SMBus(bus_num)

        except Exception:

            sys.exit(1)

        try:

            self.bus.write_byte_data(ICM_ADDR, 118, 0)

            time.sleep(0.1)

            self.bus.write_byte_data(ICM_ADDR, 78, 15)

            self.bus.write_byte_data(ICM_ADDR, 79, 6)

            self.bus.write_byte_data(ICM_ADDR, 80, 6)

            time.sleep(0.1)

        except OSError:

            pass

        self.gx_bias = 0.0

        self.gy_bias = 0.0

        self.gz_bias = 0.0

    def calibrate(self):

        gx_s = gy_s = gz_s = 0.0

        samples = 50

        print("[IMU] Calibrating...")

        for _ in range(samples):

            try:

                data = self.bus.read_i2c_block_data(ICM_ADDR, 31, 12)

                vals = struct.unpack(">6h", bytes(data))

                gx_s += vals[3] / GYRO_SENS * DEG2RAD

                gy_s += vals[4] / GYRO_SENS * DEG2RAD

                gz_s += vals[5] / GYRO_SENS * DEG2RAD

            except Exception:

                pass

            time.sleep(0.02)

        self.gx_bias = gx_s / samples

        self.gy_bias = gy_s / samples

        self.gz_bias = gz_s / samples

    def get_data(self):

        try:

            data = self.bus.read_i2c_block_data(ICM_ADDR, 31, 12)

            vals = struct.unpack(">6h", bytes(data))

            ax = vals[0] / ACCEL_SENS

            ay = vals[1] / ACCEL_SENS

            az = vals[2] / ACCEL_SENS

            gx = vals[3] / GYRO_SENS * DEG2RAD - self.gx_bias

            gy = vals[4] / GYRO_SENS * DEG2RAD - self.gy_bias

            gz = vals[5] / GYRO_SENS * DEG2RAD - self.gz_bias

            return (ax, ay, az, gx, gy, gz)

        except Exception:

            return (0.0, 0.0, 1.0, 0.0, 0.0, 0.0)


class MahonyAHRS:

    def __init__(self):

        self.q = [1.0, 0.0, 0.0, 0.0]

        self.e_int = [0.0, 0.0, 0.0]

    def update(self, ax, ay, az, gx, gy, gz, dt):

        norm = math.sqrt(ax * ax + ay * ay + az * az)

        if norm == 0:

            return

        ax /= norm

        ay /= norm

        az /= norm

        q = self.q

        vx = 2.0 * (q[1] * q[3] - q[0] * q[2])

        vy = 2.0 * (q[0] * q[1] + q[2] * q[3])

        vz = q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3]

        ex = ay * vz - az * vy

        ey = az * vx - ax * vz

        ez = ax * vy - ay * vx

        self.e_int[0] += ex * Ki * dt

        self.e_int[1] += ey * Ki * dt

        self.e_int[2] += ez * Ki * dt

        gx += Kp * ex + self.e_int[0]

        gy += Kp * ey + self.e_int[1]

        gz += Kp * ez + self.e_int[2]

        q[0] += 0.5 * (-q[1] * gx - q[2] * gy - q[3] * gz) * dt

        q[1] += 0.5 * (q[0] * gx + q[2] * gz - q[3] * gy) * dt

        q[2] += 0.5 * (q[0] * gy - q[1] * gz + q[3] * gx) * dt

        q[3] += 0.5 * (q[0] * gz + q[1] * gy - q[2] * gx) * dt

        norm = math.sqrt(sum(x * x for x in q))

        self.q = [x / norm for x in q]

    def get_euler_deg(self):

        w, x, y, z = self.q

        roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y)) * RAD2DEG

        sinp = 2 * (w * y - z * x)

        pitch = math.copysign(90, sinp) if abs(sinp) >= 1 else math.asin(sinp) * RAD2DEG

        yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z)) * RAD2DEG

        return (roll, pitch, yaw)


def remove_shm_from_resource_tracker(name=SHM_NAME):

    try:

        resource_tracker.unregister("/" + name, "shared_memory")

    except Exception:

        pass


def cleanup_server_shared_memory(shm, unlink=True):

    if shm is None:

        return

    shm_name = getattr(shm, "_name", None)

    try:

        shm.close()

    except Exception:

        pass

    if not shm_name or not unlink:

        return

    tracker_registered = False

    try:

        resource_tracker.register(shm_name, "shared_memory")

        tracker_registered = True

    except Exception:

        pass

    try:

        shm.unlink()

    except FileNotFoundError:

        if tracker_registered:

            try:

                resource_tracker.unregister(shm_name, "shared_memory")

            except Exception:

                pass

    except Exception:

        if tracker_registered:

            try:

                resource_tracker.unregister(shm_name, "shared_memory")

            except Exception:

                pass


class ShmFramePublisher:

    def __init__(self, front, back_buffers):

        self.front = front

        self.back_buffers = back_buffers

        self.write_index = 0

    @classmethod
    def create(cls):

        front = None

        back_buffers = []

        try:

            front = cls._open_front_buffer()

            for idx in range(SHM_BUFFER_COUNT - 1):

                back_buffers.append(cls._open_back_buffer(idx))

            mode = "single" if not back_buffers else f"{len(back_buffers) + 1}-buffer"

            print(f"!! SHM {mode} Created: {SHM_NAME}")

            return cls(front, back_buffers)

        except Exception:

            for shm in back_buffers:

                cleanup_server_shared_memory(shm)

            if front is not None:

                cleanup_server_shared_memory(front, unlink=False)

            raise

    @staticmethod
    def _open_front_buffer():

        try:

            shm = shared_memory.SharedMemory(name=SHM_NAME, create=True, size=SHM_SIZE)

        except FileExistsError:

            shm = shared_memory.SharedMemory(name=SHM_NAME)

        remove_shm_from_resource_tracker(SHM_NAME)

        return shm

    @staticmethod
    def _open_back_buffer(idx):

        name = f"{SHM_BACK_PREFIX}{idx}"

        try:

            shm = shared_memory.SharedMemory(name=name, create=True, size=SHM_SIZE)

        except FileExistsError:

            shm = shared_memory.SharedMemory(name=name)

            if getattr(shm, "size", SHM_SIZE) < SHM_SIZE:

                cleanup_server_shared_memory(shm)

                shm = shared_memory.SharedMemory(name=name, create=True, size=SHM_SIZE)

        remove_shm_from_resource_tracker(name)

        return shm

    def publish(self, frame_id, width, height, pixels, expected_size):

        header = struct.pack("QII", frame_id, width, height)

        if self.back_buffers:

            back = self.back_buffers[self.write_index % len(self.back_buffers)]

            self.write_index += 1

            back.buf[SHM_HEADER_SIZE : SHM_HEADER_SIZE + expected_size] = pixels[
                :expected_size
            ]

            back.buf[:SHM_HEADER_SIZE] = header

            payload = back.buf[SHM_HEADER_SIZE : SHM_HEADER_SIZE + expected_size]

            try:

                self.front.buf[SHM_HEADER_SIZE : SHM_HEADER_SIZE + expected_size] = (
                    payload
                )

            finally:

                del payload

        else:

            self.front.buf[SHM_HEADER_SIZE : SHM_HEADER_SIZE + expected_size] = pixels[
                :expected_size
            ]

        self.front.buf[:SHM_HEADER_SIZE] = header

    def close(self):

        for shm in self.back_buffers:

            cleanup_server_shared_memory(shm)

        cleanup_server_shared_memory(self.front)


def signal_handler(sig, frame):

    print("\n!! Signal received, stopping server...")

    shared.running = False


class SharedData:

    def __init__(self):

        self.raw_frame = None

        self.jpeg_frame = None

        self.jpeg_seq = 0

        self.ar_jpeg_frame = None

        self.ar_jpeg_seq = 0

        self.new_frame_available = False

        self.http_raw_clients = 0

        self.http_ar_clients = 0

        self.raw_jpeg_encoder = None

        self.ar_jpeg_encoder = None

        self.target_robot_pos = [0.0, 0.0, 0.0]

        self.target_robot_euler = [0.0, 0.0, 0.0]

        self.robot_pos = [0.0, 0.0, 0.0]

        self.robot_euler = [0.0, 0.0, 0.0]

        self.use_external_control = False

        self.control_packets = 0

        self.last_control_time = 0.0

        self.last_control_addr = ""

        self.last_control_payload = {}

        self.delay_buffer = deque()

        self.reset_yaw_req = False

        self.scene_objects = []

        self.pending_json_data = None

        self.reload_objects_req = True

        self.model_cache = {}

        self.lock = threading.Lock()

        self.running = True

        self.camera_frames = 0

        self.camera_overwrites = 0

        self.camera_frames_consumed = 0

        self.render_frames = 0

        self.shm_frames = 0

        self.ar_jpeg_submits = 0


shared = SharedData()


def apply_configured_video_flip(frame):

    if cv2 is None or frame is None:

        return frame

    if VIDEO_FLIP_HORIZONTAL and VIDEO_FLIP_VERTICAL:

        return cv2.flip(frame, -1)

    if VIDEO_FLIP_HORIZONTAL:

        return cv2.flip(frame, 1)

    if VIDEO_FLIP_VERTICAL:

        return cv2.flip(frame, 0)

    return frame


class LatestFrameJpegEncoder(threading.Thread):

    def __init__(self, name, encode_func, publish_func):

        super().__init__(name=name, daemon=True)

        self.encode_func = encode_func

        self.publish_func = publish_func

        self.cond = threading.Condition()

        self.pending_frame = None

        self.pending_seq = 0

    def submit(self, frame):

        with self.cond:

            self.pending_frame = frame

            self.pending_seq += 1

            self.cond.notify()

    def run(self):

        seen_seq = 0

        while shared.running:

            with self.cond:

                self.cond.wait_for(
                    lambda: not shared.running or self.pending_seq != seen_seq,
                    timeout=0.25,
                )

                if not shared.running:

                    break

                frame = self.pending_frame

                seen_seq = self.pending_seq

            if frame is None or cv2 is None:

                continue

            try:

                jpeg_bytes = self.encode_func(frame)

                if jpeg_bytes:

                    self.publish_func(jpeg_bytes)

            except Exception as exc:

                print(f"[JPEG] {self.name} encode failed: {exc}")


class FpsStatsThread(threading.Thread):

    def __init__(self):

        super().__init__(name="fps-stats", daemon=True)

    def run(self):

        last_time = time.perf_counter()

        last_counts = self._snapshot()

        while shared.running:

            time.sleep(5.0)

            now = time.perf_counter()

            counts = self._snapshot()

            elapsed = max(now - last_time, 1e-6)

            rates = [(cur - old) / elapsed for cur, old in zip(counts, last_counts)]

            print(
                "[FPS] "
                f"camera={rates[0]:.1f} overwrite={rates[1]:.1f} "
                f"cam_used={rates[2]:.1f} render={rates[3]:.1f} "
                f"shm={rates[4]:.1f} ar_submit={rates[5]:.1f}"
            )

            last_time = now

            last_counts = counts

    @staticmethod
    def _snapshot():

        return (
            shared.camera_frames,
            shared.camera_overwrites,
            shared.camera_frames_consumed,
            shared.render_frames,
            shared.shm_frames,
            shared.ar_jpeg_submits,
        )


def encode_bgr_frame_to_jpeg(frame):

    ok, encoded = cv2.imencode(
        ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, STREAM_JPEG_QUALITY]
    )

    if not ok:

        return None

    return encoded.tobytes()


def encode_ar_pixels_to_jpeg(frame_info):

    if np is None:

        return None

    pixels, width, height = frame_info

    frame_size = int(width) * int(height) * 3

    img_ar = np.frombuffer(pixels, dtype=np.uint8, count=frame_size).reshape(
        (height, width, 3)
    )

    img_ar_bgr = cv2.cvtColor(cv2.flip(img_ar, 0), cv2.COLOR_RGB2BGR)

    return encode_bgr_frame_to_jpeg(img_ar_bgr)


def publish_camera_jpeg(jpeg_bytes):

    with shared.lock:

        shared.jpeg_frame = jpeg_bytes

        shared.jpeg_seq += 1


def publish_ar_jpeg(jpeg_bytes):

    with shared.lock:

        shared.ar_jpeg_frame = jpeg_bytes

        shared.ar_jpeg_seq += 1


def start_stream_encoders():

    raw_encoder = LatestFrameJpegEncoder(
        "raw-http-jpeg", encode_bgr_frame_to_jpeg, publish_camera_jpeg
    )

    ar_encoder = LatestFrameJpegEncoder(
        "ar-http-jpeg", encode_ar_pixels_to_jpeg, publish_ar_jpeg
    )

    with shared.lock:

        shared.raw_jpeg_encoder = raw_encoder

        shared.ar_jpeg_encoder = ar_encoder

    raw_encoder.start()

    ar_encoder.start()


class ModelAsset:

    def __init__(self, filename: str):

        self.valid = False

        self.parts: list[tuple[int, int, str, float]] = []

        self.mask_parts: list[tuple[int, int, str, float]] = []

        self.base_radius = 0.2

        allow_fallback = os.environ.get("ALLOW_MODEL_FALLBACK", "0") == "1"

        force_fallback_keys = {
            key.strip().lower()
            for key in os.environ.get("FORCE_MODEL_FALLBACK_KEYS", "").split(",")
            if key.strip()
        }

        basename = os.path.basename(filename).lower()

        if allow_fallback and basename in force_fallback_keys:

            self._build_fallback_geometry()

            self.base_radius = 0.5

            self.valid = True

            print(f"[MODEL FALLBACK] Forced placeholder geometry for: {filename}")

            return

        model_path = os.path.join(MODEL_DIR, filename)

        if not os.path.exists(model_path):

            print(f"[ERR] Model not found: {filename}")

            if allow_fallback:

                try:

                    self._build_fallback_geometry()

                    self.base_radius = 0.5

                    self.valid = True

                    print(
                        f"[MODEL FALLBACK] Using placeholder geometry for missing model: {filename}"
                    )

                except Exception as fallback_exc:

                    print(f"[MODEL FALLBACK ERROR] {filename}: {fallback_exc}")

            return

        try:

            from trimesh.exchange.load import load as scene_loader

            from trimesh.scene import Scene as scene_type

            scene = scene_loader(model_path)

            if isinstance(scene, scene_type):

                if len(scene.geometry) > 0:

                    extents = scene.extents

                    self.base_radius = max(extents[0], extents[2]) / 2.0 * 0.9

                    geometries = scene.dump(concatenate=False)

                else:

                    geometries = []

            else:

                extents = scene.extents

                self.base_radius = max(extents[0], extents[2]) / 2.0 * 0.9

                geometries = [scene]

            print(
                f"[MODEL] {filename} Radius: {self.base_radius:.3f}m | Parts: {len(geometries)}"
            )

            for mesh in geometries:

                tex_id = 0

                mask_alpha_tex_id = 0

                tex_has_alpha = False

                alpha_mode = "OPAQUE"

                alpha_cutoff = 0.5

                try:

                    tex_img = None

                    material = (
                        mesh.visual.material
                        if hasattr(mesh.visual, "material")
                        else None
                    )

                    if material is not None:

                        raw_alpha_mode = getattr(material, "alphaMode", None)

                        if isinstance(raw_alpha_mode, str) and raw_alpha_mode:

                            alpha_mode = raw_alpha_mode.upper()

                        raw_alpha_cutoff = getattr(material, "alphaCutoff", None)

                        if raw_alpha_cutoff is not None:

                            with contextlib.suppress(TypeError, ValueError):

                                alpha_cutoff = float(raw_alpha_cutoff)

                        if hasattr(material, "baseColorTexture"):

                            tex_img = material.baseColorTexture

                        elif hasattr(material, "image"):

                            tex_img = material.image

                    if tex_img:

                        tex_id, mask_alpha_tex_id, tex_has_alpha = self._load_texture(
                            tex_img
                        )

                    if alpha_mode not in {"OPAQUE", "BLEND", "MASK"}:

                        alpha_mode = "BLEND" if tex_has_alpha else "OPAQUE"

                    alpha_cutoff = max(0.0, min(1.0, alpha_cutoff))

                except Exception as e:

                    print(f"  - Texture Error: {e}")

                lst = glGenLists(1)

                glNewList(lst, GL_COMPILE)

                vertex_colors = None

                if hasattr(mesh.visual, "vertex_colors"):

                    vertex_colors = mesh.visual.vertex_colors

                if tex_id > 0:

                    glEnable(GL_TEXTURE_2D)

                    glBindTexture(GL_TEXTURE_2D, tex_id)

                    glColor4f(1, 1, 1, 1)

                else:

                    glDisable(GL_TEXTURE_2D)

                    if vertex_colors is not None and len(vertex_colors) > 0:

                        default_color = vertex_colors[0] / 255.0

                        glColor4fv(default_color)

                    elif hasattr(mesh.visual, "material") and hasattr(
                        mesh.visual.material, "main_color"
                    ):

                        c = mesh.visual.material.main_color

                        glColor4fv(c / 255.0)

                    else:

                        glColor4f(0.8, 0.8, 0.8, 1.0)

                glBegin(GL_TRIANGLES)

                verts = mesh.vertices

                norms = mesh.vertex_normals

                uvs = mesh.visual.uv if hasattr(mesh.visual, "uv") else None

                for face in mesh.faces:

                    for vi in face:

                        if len(norms) > vi:

                            glNormal3fv(norms[vi])

                        if tex_id > 0 and uvs is not None and len(uvs) > vi:

                            glTexCoord2fv(uvs[vi])

                        if vertex_colors is not None and len(vertex_colors) > vi:

                            glColor4fv(vertex_colors[vi] / 255.0)

                        glVertex3fv(verts[vi])

                glEnd()

                glDisable(GL_TEXTURE_2D)

                glEndList()

                self.parts.append((lst, tex_id, alpha_mode, alpha_cutoff))

                mask_tex_id = (
                    mask_alpha_tex_id
                    if (mask_alpha_tex_id > 0 and uvs is not None)
                    else 0
                )

                mask_lst = glGenLists(1)

                glNewList(mask_lst, GL_COMPILE)

                if mask_tex_id > 0:

                    glEnable(GL_TEXTURE_2D)

                    glBindTexture(GL_TEXTURE_2D, mask_tex_id)

                else:

                    glDisable(GL_TEXTURE_2D)

                glBegin(GL_TRIANGLES)

                for face in mesh.faces:

                    for vi in face:

                        if mask_tex_id > 0 and len(uvs) > vi:

                            glTexCoord2fv(uvs[vi])

                        glVertex3fv(verts[vi])

                glEnd()

                glDisable(GL_TEXTURE_2D)

                glEndList()

                self.mask_parts.append(
                    (mask_lst, mask_tex_id, alpha_mode, alpha_cutoff, tex_has_alpha)
                )

            self.valid = True

        except Exception as e:

            print(f"[MODEL ERROR] {filename}: {e}")

            import traceback

            traceback.print_exc()

            if allow_fallback:

                try:

                    self._build_fallback_geometry()

                    self.base_radius = 0.5

                    self.valid = True

                    print(
                        f"[MODEL FALLBACK] Using placeholder geometry for: {filename}"
                    )

                except Exception as fallback_exc:

                    print(f"[MODEL FALLBACK ERROR] {filename}: {fallback_exc}")

    def _build_fallback_geometry(self):

        vertices = [
            (-0.5, -0.5, -0.5),
            (0.5, -0.5, -0.5),
            (0.5, 0.5, -0.5),
            (-0.5, 0.5, -0.5),
            (-0.5, -0.5, 0.5),
            (0.5, -0.5, 0.5),
            (0.5, 0.5, 0.5),
            (-0.5, 0.5, 0.5),
        ]

        faces = [
            (0, 1, 2),
            (0, 2, 3),
            (4, 6, 5),
            (4, 7, 6),
            (0, 4, 5),
            (0, 5, 1),
            (1, 5, 6),
            (1, 6, 2),
            (2, 6, 7),
            (2, 7, 3),
            (3, 7, 4),
            (3, 4, 0),
        ]

        draw_lst = glGenLists(1)

        glNewList(draw_lst, GL_COMPILE)

        glDisable(GL_TEXTURE_2D)

        glColor4f(0.85, 0.35, 0.20, 1.0)

        glBegin(GL_TRIANGLES)

        for tri in faces:

            for vi in tri:

                glVertex3fv(vertices[vi])

        glEnd()

        glEndList()

        self.parts.append((draw_lst, 0, "OPAQUE", 0.5))

        mask_lst = glGenLists(1)

        glNewList(mask_lst, GL_COMPILE)

        glBegin(GL_TRIANGLES)

        for tri in faces:

            for vi in tri:

                glVertex3fv(vertices[vi])

        glEnd()

        glEndList()

        self.mask_parts.append((mask_lst, 0, "OPAQUE", 0.5, False))

    def _load_texture(self, img_data):

        try:

            from PIL import Image

            img = (
                img_data if isinstance(img_data, Image.Image) else Image.open(img_data)
            )

            if img.mode != "RGBA":

                img = img.convert("RGBA")

            alpha = np.asarray(img.getchannel("A"), dtype=np.uint8)

            has_alpha = bool((alpha < 250).any())

            ix, iy = img.size

            raw_data = img.tobytes("raw", "RGBA", 0, -1)

            tid = glGenTextures(1)

            glBindTexture(GL_TEXTURE_2D, tid)

            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                ix,
                iy,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                raw_data,
            )

            mask_alpha_tid = 0

            if has_alpha:

                mask_rgba = np.empty((iy, ix, 4), dtype=np.uint8)

                mask_rgba[:, :, :3] = 255

                mask_rgba[:, :, 3] = np.flipud(alpha)

                mask_alpha_tid = glGenTextures(1)

                glBindTexture(GL_TEXTURE_2D, mask_alpha_tid)

                glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

                glTexImage2D(
                    GL_TEXTURE_2D,
                    0,
                    GL_RGBA,
                    ix,
                    iy,
                    0,
                    GL_RGBA,
                    GL_UNSIGNED_BYTE,
                    mask_rgba.tobytes(),
                )

            return tid, mask_alpha_tid, has_alpha

        except Exception as e:

            print(f"Texture load failed: {e}")

            return 0, 0, False

    def draw(self):

        if not self.valid:

            return None

        for lst, _, alpha_mode, alpha_cutoff in self.parts:

            if alpha_mode == "BLEND":

                glEnable(GL_BLEND)

                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            elif alpha_mode == "MASK":

                glEnable(GL_ALPHA_TEST)

                glAlphaFunc(GL_GREATER, alpha_cutoff)

            glCallList(lst)

            if alpha_mode == "BLEND":

                glDisable(GL_BLEND)

            elif alpha_mode == "MASK":

                glDisable(GL_ALPHA_TEST)

    def draw_mask(self):

        if not self.valid:

            return None

        glPushAttrib(GL_ENABLE_BIT)

        glDisable(GL_LIGHTING)

        glDisable(GL_BLEND)

        for (
            mask_lst,
            tex_id,
            alpha_mode,
            alpha_cutoff,
            tex_has_alpha,
        ) in self.mask_parts:

            if tex_id > 0:

                glEnable(GL_TEXTURE_2D)

                glBindTexture(GL_TEXTURE_2D, tex_id)

            else:

                glDisable(GL_TEXTURE_2D)

            use_alpha_test = tex_id > 0 and (
                tex_has_alpha or alpha_mode in {"MASK", "BLEND"}
            )

            if use_alpha_test:

                glEnable(GL_ALPHA_TEST)

                cutoff = alpha_cutoff if alpha_mode == "MASK" else 0.1

                glAlphaFunc(GL_GREATER, max(0.0, min(1.0, cutoff)))

            glCallList(mask_lst)

            if use_alpha_test:

                glDisable(GL_ALPHA_TEST)

        glDisable(GL_TEXTURE_2D)

        glPopAttrib()


class MapRenderer:

    def __init__(self):

        self.tid = 0

        self.valid = False

        self.track_tid = 0

        self.track_mask_valid = False

        self.track_mask_source = ""

        if not os.path.exists(MAP_FILE):

            return

        try:

            img = cv2.imread(MAP_FILE, cv2.IMREAD_UNCHANGED)

            if img is not None:

                img = cv2.flip(img, 0)

                if img.shape[2] == 4:

                    bgr = img[:, :, :3]

                    alpha = img[:, :, 3]

                else:

                    bgr = img[:, :, :3]

                    alpha = (
                        np.full(img.shape[:2], 255, dtype=np.uint8)
                        if np is not None
                        else None
                    )

                if img.shape[2] == 4:

                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)

                    fmt = GL_RGBA

                else:

                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                    fmt = GL_RGB

                self.tid = glGenTextures(1)

                glBindTexture(GL_TEXTURE_2D, self.tid)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

                glTexImage2D(
                    GL_TEXTURE_2D,
                    0,
                    fmt,
                    img.shape[1],
                    img.shape[0],
                    0,
                    fmt,
                    GL_UNSIGNED_BYTE,
                    img,
                )

                self.valid = True

                track_mask = None

                if TRACK_MASK_FILE and os.path.exists(TRACK_MASK_FILE):

                    track_img = cv2.imread(TRACK_MASK_FILE, cv2.IMREAD_UNCHANGED)

                    if track_img is not None:

                        if track_img.shape[:2] != img.shape[:2]:

                            track_img = cv2.resize(
                                track_img,
                                (img.shape[1], img.shape[0]),
                                interpolation=cv2.INTER_AREA,
                            )

                        track_img = cv2.flip(track_img, 0)

                        if track_img.shape[2] == 4:

                            track_mask = track_img[:, :, 3]

                        else:

                            track_gray = cv2.cvtColor(track_img, cv2.COLOR_BGR2GRAY)

                            _, track_mask = cv2.threshold(
                                track_gray, 127, 255, cv2.THRESH_BINARY
                            )

                        self.track_mask_source = TRACK_MASK_FILE

                if track_mask is None:

                    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

                    track_mask = cv2.inRange(hsv, (85, 40, 20), (140, 255, 255))

                    if alpha is not None:

                        track_mask = cv2.bitwise_and(track_mask, alpha)

                    self.track_mask_source = "auto-from-map"

                track_rgba = np.zeros(
                    (track_mask.shape[0], track_mask.shape[1], 4), dtype=np.uint8
                )

                track_rgba[:, :, 0:3] = 255

                track_rgba[:, :, 3] = track_mask

                self.track_tid = glGenTextures(1)

                glBindTexture(GL_TEXTURE_2D, self.track_tid)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)

                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

                glTexImage2D(
                    GL_TEXTURE_2D,
                    0,
                    GL_RGBA,
                    track_rgba.shape[1],
                    track_rgba.shape[0],
                    0,
                    GL_RGBA,
                    GL_UNSIGNED_BYTE,
                    track_rgba,
                )

                self.track_mask_valid = bool(np.count_nonzero(track_mask))

                print(f"[MAP] Loaded {MAP_FILE}")

                if self.track_mask_valid:

                    print(f"[TRACK MASK] Loaded from {self.track_mask_source}")

        except Exception:

            pass

    def draw(self):

        if not self.valid:

            return None

        glEnable(GL_BLEND)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, self.tid)

        glColor4f(1, 1, 1, 1)

        glBegin(GL_QUADS)

        glNormal3f(0, 1, 0)

        glTexCoord2f(0, 0)

        glVertex3f(0.0, 0.0, 0.0)

        glTexCoord2f(1, 0)

        glVertex3f(4.0, 0.0, 0.0)

        glTexCoord2f(1, 1)

        glVertex3f(4.0, 0.0, -5.0)

        glTexCoord2f(0, 1)

        glVertex3f(0.0, 0.0, -5.0)

        glEnd()

        glDisable(GL_TEXTURE_2D)

        glDisable(GL_BLEND)

    def draw_track_mask(self, rgb: tuple[int, int, int]):

        if not self.track_mask_valid:

            return None

        glEnable(GL_BLEND)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, self.track_tid)

        glColor4f(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0, 1.0)

        glBegin(GL_QUADS)

        glNormal3f(0, 1, 0)

        glTexCoord2f(0, 0)

        glVertex3f(0.0, 0.0, 0.0)

        glTexCoord2f(1, 0)

        glVertex3f(4.0, 0.0, 0.0)

        glTexCoord2f(1, 1)

        glVertex3f(4.0, 0.0, -5.0)

        glTexCoord2f(0, 1)

        glVertex3f(0.0, 0.0, -5.0)

        glEnd()

        glDisable(GL_TEXTURE_2D)

        glDisable(GL_BLEND)


class SceneObject:

    def __init__(self, data: dict[str, Any], model_asset: ModelAsset | None = None):

        self.data = data

        self.model = model_asset

        self.id = data.get("ID", 0)

        self.is_active = data.get("isActive", True)

        self.respawn_time = float(data.get("respawnTime", 5.0))

        self.vanish_timestamp = 0.0

        self.obj_type = data.get("type", "static")

        self.name = data.get("name", "").lower()

        raw_pos = data.get("position", {"x": 0, "y": 0, "z": 0})

        self.base_pos = np.array([raw_pos["x"], raw_pos["y"], -raw_pos["z"]])

        raw_rot = data.get("rotation", {"x": 0, "y": 0, "z": 0})

        self.base_rot = np.array([raw_rot["x"], -raw_rot["y"], raw_rot["z"]])

        raw_scale = data.get("scale", {"x": 1, "y": 1, "z": 1})

        self.scale = np.array([raw_scale["x"], raw_scale["y"], raw_scale["z"]])

        self.move_type = data.get("moveType", "None")

        self.start_time = time.time()

        self.speed = data.get("speed", 0.0)

        self.move_points = []

        for p in data.get("movePoints", []):

            self.move_points.append(np.array([p["x"], p["y"], -p["z"]]))

        self.total_path_len = 0.0

        self.segment_lens = []

        if len(self.move_points) > 1:

            for i in range(len(self.move_points) - 1):

                d = np.linalg.norm(self.move_points[i + 1] - self.move_points[i])

                self.segment_lens.append(d)

                self.total_path_len += d

        self.is_traffic_light = "trafficlight" in self.name

        self.is_traffic_rect = "trafficrect" in self.name

        self.last_hit_time = 0.0

        self.hit_cooldown = 1.0

        self.traffic_state = 0

        self.traffic_timer = 0.0

        self.time_red = 5.0

        self.time_green = 5.0

        self.time_yellow = 2.0

        self.trigger_cooldown = 0.0

        self.is_checkpoint = data.get("type") == "checkpoint"

        self.checkpoint_index = -1

        if self.is_checkpoint:

            try:

                parts = data.get("name", "").split("_")

                self.checkpoint_index = int(parts[-1])

            except Exception:

                self.checkpoint_index = 0

    @property
    def collision_radius(self):

        if self.is_traffic_rect or self.is_traffic_light:

            return 0.0

        if not self.model or not self.model.valid:

            return 0.1

        max_scale = max(self.scale[0], self.scale[2])

        return float(self.model.base_radius * max_scale)

    def update_traffic_logic(self, dt):

        if not self.is_traffic_light:

            return

        self.traffic_timer += dt

        if self.traffic_state == 0:

            if self.traffic_timer > self.time_red:

                self.traffic_state = 1

                self.traffic_timer = 0

        elif self.traffic_state == 1:

            if self.traffic_timer > self.time_green:

                self.traffic_state = 2

                self.traffic_timer = 0

        elif self.traffic_state == 2:

            if self.traffic_timer > self.time_yellow:

                self.traffic_state = 0

                self.traffic_timer = 0

    def get_current_transform(self):

        if not self.is_active:

            return (None, None, None)

        curr_pos = self.base_pos.copy()

        curr_rot = self.base_rot.copy()

        if (
            self.move_type == "PingPong"
            and len(self.move_points) >= 2
            and self.speed > 0
        ):

            now = time.time()

            elapsed = now - self.start_time

            if elapsed < 0:

                elapsed = 0

            cycle_dist = self.total_path_len * 2

            curr_dist = (elapsed * self.speed) % cycle_dist

            p_start, p_end = None, None

            if curr_dist <= self.total_path_len:

                accum = 0.0

                for i, seg_len in enumerate(self.segment_lens):

                    if accum + seg_len >= curr_dist:

                        ratio = (curr_dist - accum) / seg_len

                        p_start = self.move_points[i]

                        p_end = self.move_points[i + 1]

                        curr_pos = p_start + (p_end - p_start) * ratio

                        break

                    accum += seg_len

            else:

                return_dist = curr_dist - self.total_path_len

                accum = 0.0

                for i in range(len(self.segment_lens) - 1, -1, -1):

                    seg_len = self.segment_lens[i]

                    if accum + seg_len >= return_dist:

                        ratio = (return_dist - accum) / seg_len

                        p_start = self.move_points[i + 1]

                        p_end = self.move_points[i]

                        curr_pos = p_start + (p_end - p_start) * ratio

                        break

                    accum += seg_len

            if p_start is not None and p_end is not None:

                dx = (p_end - p_start)[0]

                dz = (p_end - p_start)[2]

                if abs(dx) > 1e-05 or abs(dz) > 1e-05:

                    curr_rot[1] = math.degrees(math.atan2(dx, -dz))

        return (curr_pos, curr_rot, self.scale)


class ObjectUDPThread(threading.Thread):

    def __init__(self):

        super().__init__(daemon=True)

    def run(self):

        port = int(NET_CONFIG.get("object_update_port", 9002))

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind(("0.0.0.0", port))

        sock.settimeout(1.0)

        print(f"[ObjectUDP] Listening on :{port}")

        while shared.running:

            try:

                data, addr = sock.recvfrom(65535)

            except socket.timeout:

                continue

            except Exception:

                continue

            try:

                payload = json.loads(data.decode("utf-8"))

            except Exception:

                continue

            if "objects" not in payload:

                continue

            try:

                with open(OBJECT_JSON_FILE, "w", encoding="utf-8") as f:

                    json.dump(payload, f, indent=2, ensure_ascii=False)

            except Exception:

                pass

            with shared.lock:

                shared.pending_json_data = payload

                shared.reload_objects_req = True

            print(f"[ObjectUDP] Received {len(payload['objects'])} objects from {addr}")

        sock.close()


class UnitySyncThread(threading.Thread):

    def __init__(self):

        super().__init__(daemon=True)

    def run(self):

        target_ip = str(NET_CONFIG.get("unity_target_ip", "127.0.0.1"))

        port = int(NET_CONFIG.get("unity_sync_port", 9003))

        rate = float(NET_CONFIG.get("sync_rate", 30))

        period = 1.0 / rate

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while shared.running:

            start_t = time.time()

            current_lap = 0

            with shared.lock:

                if shared.lap_manager is not None:

                    current_lap = shared.lap_manager.current_lap

            with shared.lock:

                objects = list(shared.scene_objects)

            sync_list = []

            for obj in objects:

                pos, rot, sc = obj.get_current_transform()

                if pos is None:

                    continue

                item = {
                    "id": obj.id,
                    "p": [round(pos[0], 3), round(pos[1], 3), round(-pos[2], 3)],
                    "r": [0, round(rot[1], 2), 0],
                    "a": obj.is_active,
                    "s": getattr(obj, "traffic_state", 0),
                    "lap": current_lap,
                }

                sync_list.append(item)

            try:

                msg = json.dumps({"sync": sync_list}, separators=(",", ":"))

                sock.sendto(msg.encode("utf-8"), (target_ip, port))

            except Exception:

                pass

            elapsed = time.time() - start_t

            sleep_time = period - elapsed

            if sleep_time > 0:

                time.sleep(sleep_time)

        sock.close()


class UDPControlThread(threading.Thread):

    def __init__(self):

        super().__init__(daemon=True)

    def run(self):

        port = int(NET_CONFIG.get("control_port", 9999))

        pos_offset = NET_CONFIG.get("pos_offset", [0, 0, 0])

        euler_offset = NET_CONFIG.get("euler_offset", [0, 0, 0])

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind(("0.0.0.0", port))

        sock.settimeout(1.0)

        print(f"[UDPControl] Listening on :{port}")

        while shared.running:

            try:

                data, addr = sock.recvfrom(2048)

            except socket.timeout:

                continue

            except Exception:

                continue

            try:

                payload = json.loads(data.decode("utf-8"))

            except Exception:

                continue

            msg_type = payload.get("type", "")

            if msg_type == "robot_position":

                try:

                    pos = payload.get("pos", [0, 0, 0])

                    euler = payload.get("euler", [0, 0, 0])

                    final_p = [
                        pos[0] + pos_offset[0],
                        pos[1] + pos_offset[1],
                        pos[2] + pos_offset[2],
                    ]

                    final_p[2] = -final_p[2]

                    final_e = [
                        euler[0] + euler_offset[0],
                        euler[1] + euler_offset[1],
                        euler[2] + euler_offset[2],
                    ]

                    with shared.lock:

                        if MOVEMENT_DELAY > 0:

                            shared.delay_buffer.append((time.time(), final_p, final_e))

                        else:

                            shared.target_robot_pos = final_p

                            shared.target_robot_euler = final_e

                        shared.use_external_control = True

                        shared.control_packets += 1

                        shared.last_control_time = time.time()

                        shared.last_control_addr = f"{addr[0]}:{addr[1]}"

                        shared.last_control_payload = payload

                except Exception:

                    pass

        sock.close()


class IMUThread(threading.Thread):

    def __init__(self):

        super().__init__(daemon=True)

    def run(self):

        print("[IMU] Started.")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        target = (NET_CONFIG["udp_target_ip"], NET_CONFIG["udp_target_port"])

        imu = ICM42688(I2C_BUS_NUM)

        imu.calibrate()

        ahrs = MahonyAHRS()

        loop_delay = 1.0 / NET_CONFIG["imu_send_rate"]

        last_t = time.perf_counter()

        cont_yaw = 0.0

        yaw_off = 0.0

        last_raw = 0.0

        first = True

        while shared.running:

            now = time.perf_counter()

            dt = now - last_t

            last_t = now

            ax, ay, az, gx, gy, gz = imu.get_data()

            ahrs.update(ax, ay, az, gx, gy, gz, dt)

            r, p, y = ahrs.get_euler_deg()

            if first:

                last_raw = y

                cont_yaw = y

                yaw_off = y

                first = False

            d_yaw = y - last_raw

            if d_yaw < -180:

                d_yaw += 360

            elif d_yaw > 180:

                d_yaw -= 360

            cont_yaw += d_yaw

            last_raw = y

            with shared.lock:

                if shared.reset_yaw_req:

                    yaw_off = cont_yaw

                    shared.reset_yaw_req = False

            final_y = -(cont_yaw - yaw_off)

            with shared.lock:

                if not shared.use_external_control:

                    shared.robot_euler = [p, final_y, r]

            try:

                sock.sendto(f"X0.00,Y{final_y:.2f},Z0.00".encode(), target)

            except Exception:

                pass

            pt = time.perf_counter() - now

            if pt < loop_delay:

                time.sleep(loop_delay - pt)


class BackgroundRenderer:

    def __init__(self):

        self.t = glGenTextures(1)

        self._texture_initialized = False

        self._texture_size = (0, 0)

        glBindTexture(GL_TEXTURE_2D, self.t)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        if cv2 is not None:

            new_K, roi = cv2.getOptimalNewCameraMatrix(
                CAMERA_MATRIX,
                DIST_COEFFS,
                (WINDOW_WIDTH, WINDOW_HEIGHT),
                0,
                (WINDOW_WIDTH, WINDOW_HEIGHT),
            )

            self.mapx, self.mapy = cv2.initUndistortRectifyMap(
                CAMERA_MATRIX,
                DIST_COEFFS,
                None,
                new_K,
                (WINDOW_WIDTH, WINDOW_HEIGHT),
                5,
            )

        else:

            self.mapx = None

            self.mapy = None

    def update_and_draw(self, img, fps, pos, euler):

        if img is None:

            return None

        undistorted_img = cv2.remap(img, self.mapx, self.mapy, cv2.INTER_LINEAR)

        i = cv2.cvtColor(undistorted_img, cv2.COLOR_BGR2RGB)

        h, w = i.shape[:2]

        glBindTexture(GL_TEXTURE_2D, self.t)

        if not self._texture_initialized or self._texture_size != (w, h):

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, i)

            self._texture_initialized = True

            self._texture_size = (w, h)

        else:

            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, i)

        self.draw()

    def draw_existing(self):

        glBindTexture(GL_TEXTURE_2D, self.t)

        self.draw()

    def draw(self):

        glMatrixMode(GL_PROJECTION)

        glPushMatrix()

        glLoadIdentity()

        glOrtho(0, 1, 0, 1, -1, 1)

        glMatrixMode(GL_MODELVIEW)

        glPushMatrix()

        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)

        glDisable(GL_LIGHTING)

        glEnable(GL_TEXTURE_2D)

        glColor3f(1, 1, 1)

        glBegin(GL_QUADS)

        glTexCoord2f(0, 1)

        glVertex2f(0, 0)

        glTexCoord2f(1, 1)

        glVertex2f(1, 0)

        glTexCoord2f(1, 0)

        glVertex2f(1, 1)

        glTexCoord2f(0, 0)

        glVertex2f(0, 1)

        glEnd()

        glDisable(GL_TEXTURE_2D)

        glEnable(GL_LIGHTING)

        glEnable(GL_DEPTH_TEST)

        glPopMatrix()

        glMatrixMode(GL_PROJECTION)

        glPopMatrix()

        glMatrixMode(GL_MODELVIEW)


class LapGameManager:

    def __init__(self, referee):

        self.referee = referee

        self.checkpoints = {}

        self.total_checkpoints = 0

        self.current_lap = 0

        self.next_checkpoint_index = 0

        self.has_started_race = False

        self.last_trigger_time = 0

        self.trigger_cooldown = 2.0

    def reload_checkpoints(self, scene_objects):

        self.checkpoints = {}

        max_idx = -1

        for obj in scene_objects:

            if obj.is_checkpoint:

                self.checkpoints[obj.checkpoint_index] = obj

                if obj.checkpoint_index > max_idx:

                    max_idx = obj.checkpoint_index

        self.total_checkpoints = max_idx + 1

        if self.total_checkpoints > 0:

            print(f"[LAP SYSTEM] 系统就绪: 共 {self.total_checkpoints} 个记录点。")

            print("[LAP SYSTEM] 等待开始... 请前往 Checkpoint_0")

    def on_checkpoint_enter(self, index):

        now = time.time()

        if now - self.last_trigger_time < self.trigger_cooldown:

            return

        self.referee.log_event("LAP_CHECKPOINT", 0, f"经过记录点 {index}")

        self.last_trigger_time = now

        print(
            f"--- [检测到记录点] 撞到了: {index} | 当前需找: {self.next_checkpoint_index} ---"
        )

        if index == self.next_checkpoint_index:

            print(f"[LAP] ✅ 有效! Checkpoint {index} 通过!")

            self.next_checkpoint_index += 1

            if index == 0 and not self.has_started_race:

                self.has_started_race = True

                self.current_lap = 1

                print(">>> 🏁 比赛正式开始! (计时启动) <<<")

                return

            elif index == 0:

                return

            return

        elif index == 0 and self.next_checkpoint_index >= self.total_checkpoints:

            self.complete_lap()

            return

        elif index == 0:

            print(
                f"[LAP] ❌ 无效! 你回到了起点，但中间漏了点。应去: {self.next_checkpoint_index}"
            )

            return

        else:

            print(
                f"[LAP] ❌ 顺序错误! 你撞到了 {index}，但应该去: {self.next_checkpoint_index}"
            )

    def complete_lap(self):

        msg = f"完成第 {self.current_lap} 圈"

        print(f"🏁 {msg}")

        self.referee.log_event("LAP_FINISH", 0, msg, {"lap": self.current_lap})

        self.current_lap += 1

        self.next_checkpoint_index = 1


class RefereeSystem:

    def __init__(self):

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        self.filename = os.path.join(os.getcwd(), f"match_record_{timestamp}.json")

        self.records = []

        self.start_time = time.time()

        self.lock = threading.Lock()

        self.flush_cond = threading.Condition(self.lock)

        self.dirty = True

        self.stopped = False

        self.writer_thread = threading.Thread(
            target=self._writer_loop, name="referee-log-writer", daemon=True
        )

        self.writer_thread.start()

        self.flush_now()

        print(f"[REFEREE] 裁判系统启动! 记录文件: {self.filename}")

    def log_event(self, event_type, obj_id, message, extra_data=None):

        current_time = time.time()

        elapsed = current_time - self.start_time

        record = {
            "time_str": datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "elapsed_seconds": round(elapsed, 2),
            "type": event_type,
            "obj_id": obj_id,
            "message": message,
            "data": extra_data if extra_data else {},
        }

        with self.flush_cond:

            record["index"] = len(self.records) + 1

            self.records.append(record)

            self.dirty = True

            self.flush_cond.notify()

        print(f"📋 [REF] {event_type} | {message}")

    def _snapshot(self):

        with self.lock:

            return list(self.records)

    def _writer_loop(self):

        while True:

            with self.flush_cond:

                self.flush_cond.wait_for(
                    lambda: self.stopped or self.dirty,
                    timeout=REFEREE_FLUSH_INTERVAL,
                )

                if self.stopped and not self.dirty:

                    return

                if not self.dirty:

                    continue

                records = list(self.records)

                self.dirty = False

            self.save_to_disk(records)

    def flush_now(self):

        self.save_to_disk(self._snapshot())

    def close(self):

        with self.flush_cond:

            self.stopped = True

            self.flush_cond.notify()

        self.writer_thread.join(timeout=1.0)

        self.flush_now()

    def save_to_disk(self, records=None):

        try:

            if records is None:

                records = self._snapshot()

            data = {
                "match_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_events": len(records),
                "events": records,
            }

            with open(self.filename, "w", encoding="utf-8") as f:

                json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

        except Exception as e:

            print(f"[REFEREE ERROR] Save failed: {e}")


class CameraThread(threading.Thread):

    @staticmethod
    def _fourcc_name(cap) -> str:

        try:

            value = int(cap.get(cv2.CAP_PROP_FOURCC))

            return "".join(chr((value >> (8 * i)) & 0xFF) for i in range(4)).strip()

        except Exception:

            return ""

    @staticmethod
    def _camera_candidates():

        configured = SYS_CONFIG.get("device_name", "")

        candidates = []

        seen = set()

        def add(device):

            if device is None or device == "":

                return

            key = str(device)

            if key in seen:

                return

            seen.add(key)

            candidates.append(device)

        add(configured)

        if isinstance(configured, str) and configured:

            with contextlib.suppress(Exception):

                add(os.path.realpath(configured))

        if os.name != "nt":

            with contextlib.suppress(Exception):

                for name in sorted(os.listdir("/dev")):

                    if name.startswith("video-camera"):

                        path = os.path.join("/dev", name)

                        add(path)

                        with contextlib.suppress(Exception):

                            add(os.path.realpath(path))

            for node in (31, 22, 32, 23, 33, 24, 20, 0, 1, 2, 3, 11, 12, 13):

                add(f"/dev/video{node}")

        return candidates

    def _try_open(self):

        import platform

        if "Windows" in platform.platform():

            test_nodes = [0, 1, 2]

            backends = [cv2.CAP_DSHOW, cv2.CAP_ANY]

        else:

            test_nodes = self._camera_candidates()

            backends = [cv2.CAP_V4L2]

        raw_fourccs = {"RG10", "BA10", "GB10", "BG10", "Y10"}

        for device in test_nodes:

            for backend in backends:

                label = (
                    f"/dev/video{device}" if isinstance(device, int) else str(device)
                )

                print(f"[CAM] 探测摄像头 {label} (Backend: {backend})...")

                try:

                    if "Windows" in platform.platform():

                        cap = cv2.VideoCapture(device, backend)

                    else:

                        cap = cv2.VideoCapture(device, backend)

                    if cap.isOpened():

                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)

                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)

                        cap.set(cv2.CAP_PROP_FPS, 30)

                        cap.set(cv2.CAP_PROP_CONVERT_RGB, 1)

                        fourcc = self._fourcc_name(cap)

                        if fourcc in raw_fourccs:

                            print(f"[CAM] ❌ {label} 是原始 Bayer 流({fourcc})，跳过。")

                            cap.release()

                            continue

                        ret, _ = cap.read()

                        if ret:

                            fourcc = self._fourcc_name(cap)

                            print(
                                f"[CAM] ✅ 成功连接并打开图像通道: {label}"
                                f" ({fourcc or 'unknown'})"
                            )

                            return cap

                        else:

                            print(f"[CAM] ❌ {label} 无数据返回，跳过。")

                    cap.release()

                except Exception as e:

                    print(f"[CAM] ❌ 探测节点 {label} 发生异常: {e}")

        return None

    def run(self):

        cap = self._try_open()

        if not cap:

            print("[CAM] 🚨 严重错误：无法打开任何相机节点！")

            return

        print("[CAM] 🚀 摄像头读取线程已启动...")

        next_jpeg_submit_time = 0.0

        while shared.running:

            ret, f = cap.read()

            if not ret:

                print("[CAM] ⚠️ 读取帧失败，尝试重新连接...")

                cap.release()

                time.sleep(1)

                cap = self._try_open()

                if not cap:

                    print("[CAM] 🚨 重新连接失败，退出线程。")

                    break

                continue

            if f.shape[1] != WINDOW_WIDTH or f.shape[0] != WINDOW_HEIGHT:

                f = cv2.resize(f, (WINDOW_WIDTH, WINDOW_HEIGHT))

            f = apply_configured_video_flip(f)

            with shared.lock:

                if shared.new_frame_available:

                    shared.camera_overwrites += 1

                shared.raw_frame = f

                shared.new_frame_available = True

                shared.camera_frames += 1

                raw_clients = shared.http_raw_clients

                raw_encoder = shared.raw_jpeg_encoder

            now = time.time()

            if (
                raw_clients > 0
                and raw_encoder is not None
                and now >= next_jpeg_submit_time
            ):

                raw_encoder.submit(f)

                next_jpeg_submit_time = now + STREAM_INTERVAL

            time.sleep(0.001)

        if cap:

            cap.release()

        print("[CAM] 🛑 摄像头线程已安全退出。")


def handle_http_client(conn):

    try:

        try:

            with contextlib.suppress(Exception):

                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            req = conn.recv(1024).decode("utf-8", errors="ignore")

            if not req:

                conn.close()

                return

            request_line = req.split("\n")[0]

            if " /control_state" in request_line:

                with shared.lock:

                    state = {
                        "control_packets": shared.control_packets,
                        "last_control_time": shared.last_control_time,
                        "last_control_addr": shared.last_control_addr,
                        "last_control_payload": shared.last_control_payload,
                        "use_external_control": shared.use_external_control,
                        "target_robot_pos": list(shared.target_robot_pos),
                        "target_robot_euler": list(shared.target_robot_euler),
                        "robot_pos": list(shared.robot_pos),
                        "robot_euler": list(shared.robot_euler),
                        "render_frames": shared.render_frames,
                        "shm_frames": shared.shm_frames,
                        "ar_jpeg_seq": shared.ar_jpeg_seq,
                    }

                body = json.dumps(state, ensure_ascii=False).encode("utf-8")

                conn.sendall(
                    b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: "
                    + str(len(body)).encode("ascii")
                    + b"\r\n\r\n"
                    + body
                )

                conn.close()

                return

            is_ar_stream = False

            if "/ar_feed" in request_line:

                is_ar_stream = True

            with shared.lock:

                if is_ar_stream:

                    shared.http_ar_clients += 1

                else:

                    shared.http_raw_clients += 1

            conn.sendall(
                b"HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n"
            )

            last_sent_seq = -1

            while shared.running:

                data = None

                if is_ar_stream:

                    with shared.lock:

                        data = shared.ar_jpeg_frame

                        seq = shared.ar_jpeg_seq

                else:

                    with shared.lock:

                        data = shared.jpeg_frame

                        seq = shared.jpeg_seq

                if data and seq != last_sent_seq:

                    header = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"

                    conn.sendall(header + data + b"\r\n")

                    last_sent_seq = seq

                else:

                    time.sleep(STREAM_IDLE_SLEEP)

        except Exception:

            pass

        finally:

            with shared.lock:

                if "is_ar_stream" in locals():

                    if is_ar_stream:

                        shared.http_ar_clients = max(0, shared.http_ar_clients - 1)

                    else:

                        shared.http_raw_clients = max(0, shared.http_raw_clients - 1)

            conn.close()

    except Exception:

        conn.close()

        raise


def http_server_job():

    port = int(NET_CONFIG["stream_port"])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:

        try:

            s.bind(("0.0.0.0", port))

            s.listen(8)

            print(f"[HTTP] Streaming on port {port}")

            while shared.running:

                try:

                    s.settimeout(1.0)

                    c, _ = s.accept()

                    threading.Thread(
                        target=handle_http_client, args=(c,), daemon=True
                    ).start()

                except Exception:

                    continue

        except Exception as exc:

            print(f"[HTTP] Server Error: {exc}")

        s.close()

    finally:

        s.close()


def check_car_collision_optimized(car_pos, cos_t, sin_t, obj_pos, obj_radius):

    half_w = 0.08

    half_l = 0.15

    dx = obj_pos[0] - car_pos[0]

    dz = obj_pos[2] - car_pos[2]

    local_x = dx * cos_t - dz * sin_t

    local_z = dx * sin_t + dz * cos_t

    closest_x = max(-half_w, min(local_x, half_w))

    closest_z = max(-half_l, min(local_z, half_l))

    dist_x = local_x - closest_x

    dist_z = local_z - closest_z

    return dist_x * dist_x + dist_z * dist_z < obj_radius * obj_radius


def check_point_in_obb(point_pos, box_pos, box_euler, box_scale):

    dx = point_pos[0] - box_pos[0]

    dz = point_pos[2] - box_pos[2]

    yaw_rad = math.radians(-box_euler[1])

    local_x = dx * math.cos(yaw_rad) - dz * math.sin(yaw_rad)

    local_z = dx * math.sin(yaw_rad) + dz * math.cos(yaw_rad)

    radius_x = box_scale[0] * 0.5 * 1.1

    radius_z = box_scale[2] * 0.5 * 1.1

    in_x = abs(local_x) < radius_x

    in_z = abs(local_z) < radius_z

    return in_x and in_z


def lerp(a, b, t):

    return a + (b - a) * t


def lerp_angle(a, b, t):

    diff = (b - a + 180) % 360 - 180

    return a + diff * t


def advance_interval_deadline(deadline, now, interval):

    if interval <= 0:

        return now

    if deadline <= 0 or now - deadline > interval * 4:

        return now + interval

    while deadline <= now:

        deadline += interval

    return deadline


@dataclass
class _RuntimeState:

    window: Any = None

    shm: shared_memory.SharedMemory | None = None

    shm_publisher: ShmFramePublisher | None = None

    bg: BackgroundRenderer | None = None

    map_r: MapRenderer | None = None

    proj_mat: Any = None

    referee: RefereeSystem | None = None

    lap_mgr: LapGameManager | None = None

    traffic_sphere_list: int = 0


def _load_scene_objects(new_data: dict[str, Any]) -> list[SceneObject]:

    new_objs: list[SceneObject] = []

    for o in new_data.get("objects", []):

        name = str(o.get("name", ""))

        name_lower = name.lower()

        is_checkpoint = o.get("type") == "checkpoint" or "checkpoint" in name_lower

        is_traffic_control = name_lower.startswith(
            "trafficlight"
        ) or name_lower.startswith("trafficrect")

        is_special = is_checkpoint or is_traffic_control

        model = None

        resolved_name = name

        if not is_special and resolved_name and not resolved_name.endswith(".glb"):

            resolved_name += ".glb"

        if not is_special and resolved_name:

            if resolved_name not in shared.model_cache:

                asset = ModelAsset(resolved_name)

                if asset.valid:

                    shared.model_cache[resolved_name] = asset

                else:

                    print(
                        f"[WARN] Model '{resolved_name}' failed to load, object will have no visual."
                    )

            model = shared.model_cache.get(resolved_name)

        obj = SceneObject(o, model)

        if not hasattr(obj, "last_hit_time"):

            obj.last_hit_time = 0.0

        if not hasattr(obj, "hit_cooldown"):

            obj.hit_cooldown = 1.0

        new_objs.append(obj)

    return new_objs


def _load_scene_from_file_if_needed(new_data, do_reload):

    if do_reload and new_data is None and os.path.exists(OBJECT_JSON_FILE):

        try:

            with open(OBJECT_JSON_FILE, "r", encoding="utf-8") as f:

                new_data = json.load(f)

        except Exception:

            pass

    return new_data


def _select_key_context():

    try:

        if sys.stdin.isatty():

            return KeyPoller()

    except Exception:

        pass

    return _NullKeyPoller()


def _apply_projection_and_camera(proj_mat, pos, euler):

    glMatrixMode(GL_PROJECTION)

    glLoadIdentity()

    glLoadMatrixf(proj_mat)

    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity()

    pr = math.radians(euler[0])

    yr = math.radians(euler[1])

    target = [
        pos[0] + math.sin(yr) * math.cos(pr),
        pos[1] + math.sin(pr),
        pos[2] - math.cos(yr) * math.cos(pr),
    ]

    eye = np.array(pos, dtype=np.float32)

    center = np.array(target, dtype=np.float32)

    up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

    f = center - eye

    f_norm = float(np.linalg.norm(f))

    if f_norm < 1e-6:

        f = np.array([0.0, 0.0, -1.0], dtype=np.float32)

    else:

        f = f / f_norm

    s = np.cross(f, up)

    s_norm = float(np.linalg.norm(s))

    if s_norm < 1e-6:

        s = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    else:

        s = s / s_norm

    u = np.cross(s, f)

    view_mat = np.array(
        [
            [s[0], u[0], -f[0], 0.0],
            [s[1], u[1], -f[1], 0.0],
            [s[2], u[2], -f[2], 0.0],
            [-np.dot(s, eye), -np.dot(u, eye), np.dot(f, eye), 1.0],
        ],
        dtype=np.float32,
    )

    glLoadMatrixf(view_mat)


def _build_traffic_sphere_list() -> int:

    if not OPENGL_AVAILABLE:

        return 0

    try:

        lst = glGenLists(1)

        if not lst:

            return 0

        quadric = gluNewQuadric()

        glNewList(lst, GL_COMPILE)

        gluSphere(quadric, 0.5, 16, 16)

        glEndList()

        return int(lst)

    except Exception:

        return 0


def main():

    signal.signal(signal.SIGINT, signal_handler)

    signal.signal(signal.SIGTERM, signal_handler)

    state = _RuntimeState()

    if glfw is not None and OPENGL_AVAILABLE:

        try:

            if glfw.init():

                glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

                state.window = glfw.create_window(
                    WINDOW_WIDTH, WINDOW_HEIGHT, "Server", None, None
                )

                if state.window:

                    glfw.make_context_current(state.window)

                    with contextlib.suppress(Exception):

                        glfw.swap_interval(0)

        except Exception:

            state.window = None

    try:

        try:

            state.shm_publisher = ShmFramePublisher.create()

            state.shm = state.shm_publisher.front

        except Exception:

            try:

                state.shm = shared_memory.SharedMemory(name=SHM_NAME)

                remove_shm_from_resource_tracker(SHM_NAME)

                state.shm_publisher = ShmFramePublisher(state.shm, [])

            except Exception:

                state.shm = None

                print(
                    "[WARN] Failed to create or attach shared memory; continuing without SHM."
                )

        if OPENGL_AVAILABLE:

            glEnable(GL_DEPTH_TEST)

            glEnable(GL_LIGHTING)

            glEnable(GL_LIGHT0)

            glEnable(GL_COLOR_MATERIAL)

            glLightfv(GL_LIGHT0, GL_POSITION, (0, 10, 0, 1))

            glPixelStorei(GL_PACK_ALIGNMENT, 1)

        state.bg = BackgroundRenderer()

        state.map_r = MapRenderer()

        state.proj_mat = get_opengl_projection_matrix(
            CAMERA_MATRIX, WINDOW_WIDTH, WINDOW_HEIGHT, 0.1, 100.0
        )

        state.traffic_sphere_list = _build_traffic_sphere_list()

        state.referee = RefereeSystem()

        state.lap_mgr = LapGameManager(state.referee)

        with shared.lock:

            shared.lap_manager = state.lap_mgr

        start_stream_encoders()

        CameraThread().start()

        threading.Thread(target=http_server_job, daemon=True).start()

        IMUThread().start()

        UDPControlThread().start()

        ObjectUDPThread().start()

        UnitySyncThread().start()

        if FPS_STATS_ENABLED:

            FpsStatsThread().start()

        print("!! AR Server Running... (Ref System ON) !!")

        frame_cnt = 0

        cam_p = [0.0, 0.0, 0.0]

        target_frame_time = RENDER_INTERVAL

        last_frame_time = time.time()

        smooth_speed = 10.0

        next_ar_jpeg_submit_time = 0.0

        next_shm_output_time = 0.0

        with _select_key_context() as key_poller:

            try:

                while shared.running and not (
                    state.window is not None
                    and glfw is not None
                    and glfw.window_should_close(state.window)
                ):

                    loop_start_time = time.time()

                    current_time = time.time()

                    dt = current_time - last_frame_time

                    last_frame_time = current_time

                    if key_poller.poll() == "1":

                        with shared.lock:

                            shared.reset_yaw_req = True

                    if glfw is not None and state.window is not None:

                        try:

                            glfw.poll_events()

                        except Exception:

                            pass

                    new_data = None

                    do_reload = False

                    with shared.lock:

                        if shared.reload_objects_req:

                            do_reload = True

                            if shared.pending_json_data:

                                new_data = shared.pending_json_data

                                shared.pending_json_data = None

                            shared.reload_objects_req = False

                    new_data = _load_scene_from_file_if_needed(new_data, do_reload)

                    if new_data:

                        new_objs = _load_scene_objects(new_data)

                        with shared.lock:

                            shared.scene_objects = new_objs

                        state.lap_mgr.reload_checkpoints(new_objs)

                        print(f"[SCENE] Updated {len(new_objs)} objects.")

                    frame = None

                    with shared.lock:

                        if shared.new_frame_available:

                            frame = shared.raw_frame

                            shared.new_frame_available = False

                            shared.camera_frames_consumed += 1

                        if MOVEMENT_DELAY > 0:

                            while (
                                shared.delay_buffer
                                and current_time - shared.delay_buffer[0][0]
                                >= MOVEMENT_DELAY
                            ):

                                _, delayed_p, delayed_r = shared.delay_buffer.popleft()

                                shared.target_robot_pos = delayed_p

                                shared.target_robot_euler = delayed_r

                        target_p = list(shared.target_robot_pos)

                        target_r = list(shared.target_robot_euler)

                        use_external_control = shared.use_external_control

                        pos = list(shared.robot_pos)

                        euler = list(shared.robot_euler)

                        draw_objs = list(shared.scene_objects)

                    if use_external_control:

                        safe_dt = min(dt, 0.1)

                        factor = min(safe_dt * smooth_speed, 1.0)

                        pos[0] = lerp(pos[0], target_p[0], factor)

                        pos[1] = lerp(pos[1], target_p[1], factor)

                        pos[2] = lerp(pos[2], target_p[2], factor)

                        euler[0] = lerp_angle(euler[0], target_r[0], factor)

                        euler[1] = lerp_angle(euler[1], target_r[1], factor)

                        euler[2] = lerp_angle(euler[2], target_r[2], factor)

                        with shared.lock:

                            shared.robot_pos = pos

                            shared.robot_euler = euler

                    cam_p = np.array(pos) if np is not None else list(pos)

                    cam_yaw = euler[1]

                    theta_rad = math.radians(-cam_yaw)

                    cos_t = math.cos(theta_rad)

                    sin_t = math.sin(theta_rad)

                    current_light_state = -1

                    for obj in draw_objs:

                        if obj.is_traffic_light:

                            current_light_state = obj.traffic_state

                            break

                    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                    if frame is not None:

                        state.bg.update_and_draw(frame, 0, pos, euler)

                    else:

                        state.bg.draw_existing()

                    _apply_projection_and_camera(state.proj_mat, pos, euler)

                    state.map_r.draw()

                    for obj in draw_objs:

                        obj.update_traffic_logic(dt)

                        if obj.obj_type == "dynamic" and not obj.is_active:

                            if (
                                obj.respawn_time > 0
                                and current_time - obj.vanish_timestamp
                                > obj.respawn_time
                            ):

                                obj.is_active = True

                                print(f"✨ [RESPAWN] 物体 {obj.id} 复活了!")

                                state.referee.log_event(
                                    "SYSTEM", obj.id, "物体自动复活", {"name": obj.name}
                                )

                        if (
                            not obj.is_active
                            and not obj.is_checkpoint
                            and not obj.is_traffic_rect
                        ):

                            continue

                        if (
                            obj.is_traffic_rect
                            and obj.traffic_state != 0
                            and current_time - obj.trigger_cooldown > 1.0
                        ):

                            obj.traffic_state = 0

                        if (
                            hasattr(obj, "collision_reset_time")
                            and obj.collision_reset_time > 0
                            and current_time > obj.collision_reset_time
                        ):

                            obj.traffic_state = 0

                            obj.collision_reset_time = 0

                        cp, cr, cs = obj.get_current_transform()

                        if cp is None:

                            continue

                        if obj.is_checkpoint:

                            if check_point_in_obb(cam_p, cp, cr, cs):

                                state.lap_mgr.on_checkpoint_enter(obj.checkpoint_index)

                            continue

                        if obj.is_traffic_rect:

                            if (
                                check_point_in_obb(cam_p, cp, cr, cs)
                                and current_time - obj.trigger_cooldown > 2.0
                            ):

                                obj.trigger_cooldown = current_time

                                state_map = {0: 1, 1: 2, 2: 3}

                                obj.traffic_state = state_map.get(
                                    current_light_state, 0
                                )

                                status_msg = "未知"

                                if obj.traffic_state == 1:

                                    status_msg = "❌ 闯红灯"

                                elif obj.traffic_state == 2:

                                    status_msg = "✅ 绿灯通行"

                                elif obj.traffic_state == 3:

                                    status_msg = "⚠️ 黄灯通过"

                                state.referee.log_event(
                                    "TRAFFIC",
                                    obj.id,
                                    status_msg,
                                    {"light": current_light_state},
                                )

                            continue

                        if obj.is_traffic_light:

                            glPushMatrix()

                            glTranslatef(cp[0], cp[1], cp[2])

                            if obj.traffic_state == 0:

                                glColor3f(1, 0, 0)

                            elif obj.traffic_state == 1:

                                glColor3f(0, 1, 0)

                            elif obj.traffic_state == 2:

                                glColor3f(1, 1, 0)

                            else:

                                glColor3f(0.5, 0.5, 0.5)

                            if state.traffic_sphere_list:

                                glScalef(cs[0], cs[0], cs[0])

                                glCallList(state.traffic_sphere_list)

                            else:

                                sphere = gluNewQuadric()

                                gluSphere(sphere, 0.5 * cs[0], 16, 16)

                            glPopMatrix()

                            continue

                        if (
                            abs(cp[0] - cam_p[0]) < 10.0
                            and abs(cp[2] - cam_p[2]) < 10.0
                        ):

                            is_hit = check_car_collision_optimized(
                                cam_p, cos_t, sin_t, cp, obj.collision_radius
                            )

                            if is_hit:

                                if not hasattr(obj, "last_hit_time"):

                                    obj.last_hit_time = 0

                                if not hasattr(obj, "hit_cooldown"):

                                    obj.hit_cooldown = 1.0

                                if current_time - obj.last_hit_time > obj.hit_cooldown:

                                    obj.last_hit_time = current_time

                                    obj.traffic_state = 1

                                    obj.collision_reset_time = current_time + 0.5

                                    obj_type_str = (
                                        "Dynamic"
                                        if obj.obj_type == "dynamic"
                                        else "Static"
                                    )

                                    state.referee.log_event(
                                        "COLLISION",
                                        obj.id,
                                        f"碰撞 {obj_type_str}",
                                        {"name": obj.name},
                                    )

                                    if obj.obj_type == "dynamic":

                                        obj.is_active = False

                                        obj.vanish_timestamp = current_time

                                        print(
                                            f"!! 💥 击碎动态物体: {obj.id} (将在 {obj.respawn_time}s 后复活) !!"
                                        )

                                    else:

                                        print(
                                            f"!! 🚧 撞击静态障碍: {obj.id} (无伤害) !!"
                                        )

                        if obj.is_active and obj.model is not None:

                            glPushMatrix()

                            glTranslatef(cp[0], cp[1], cp[2])

                            glRotatef(cr[1], 0, 1, 0)

                            glRotatef(cr[0], 1, 0, 0)

                            glRotatef(cr[2], 0, 0, 1)

                            glScalef(cs[0], cs[1], cs[2])

                            obj.model.draw()

                            glPopMatrix()

                    try:

                        with shared.lock:

                            ar_clients = shared.http_ar_clients

                            ar_encoder = shared.ar_jpeg_encoder

                        now = loop_start_time

                        needs_ar_jpeg = (
                            ar_clients > 0
                            and ar_encoder is not None
                            and now >= next_ar_jpeg_submit_time
                        )

                        needs_shm_frame = state.shm is not None and (
                            SHM_INTERVAL <= 0 or now >= next_shm_output_time
                        )

                        if needs_ar_jpeg or needs_shm_frame:

                            pixels = glReadPixels(
                                0,
                                0,
                                WINDOW_WIDTH,
                                WINDOW_HEIGHT,
                                GL_RGB,
                                GL_UNSIGNED_BYTE,
                            )

                            expected_size = WINDOW_WIDTH * WINDOW_HEIGHT * 3

                            if len(pixels) >= expected_size:

                                if needs_shm_frame and state.shm_publisher is not None:

                                    frame_cnt += 1

                                    state.shm_publisher.publish(
                                        frame_cnt,
                                        WINDOW_WIDTH,
                                        WINDOW_HEIGHT,
                                        pixels,
                                        expected_size,
                                    )

                                    shared.shm_frames += 1

                                    next_shm_output_time = advance_interval_deadline(
                                        next_shm_output_time, now, SHM_INTERVAL
                                    )

                                if needs_ar_jpeg:

                                    ar_encoder.submit(
                                        (
                                            pixels[:expected_size],
                                            WINDOW_WIDTH,
                                            WINDOW_HEIGHT,
                                        )
                                    )

                                    shared.ar_jpeg_submits += 1

                                    next_ar_jpeg_submit_time = (
                                        advance_interval_deadline(
                                            next_ar_jpeg_submit_time,
                                            now,
                                            STREAM_INTERVAL,
                                        )
                                    )

                    except Exception:

                        pass

                    shared.render_frames += 1

                    if SWAP_BUFFERS and glfw is not None and state.window is not None:

                        try:

                            glfw.swap_buffers(state.window)

                        except Exception:

                            pass

                    pt = time.time() - loop_start_time

                    if pt < target_frame_time:

                        time.sleep(target_frame_time - pt)

            except KeyboardInterrupt:

                pass

            except Exception:

                traceback.print_exc()

    finally:

        shared.running = False

        if state.referee is not None:

            with contextlib.suppress(Exception):

                state.referee.close()

        if state.shm_publisher is not None:

            state.shm_publisher.close()

        else:

            cleanup_server_shared_memory(state.shm)

        if glfw is not None:

            with contextlib.suppress(Exception):

                glfw.terminate()


if __name__ == "__main__":

    from multiprocessing import freeze_support

    freeze_support()

    main()
