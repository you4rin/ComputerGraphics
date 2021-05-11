import numpy as np
import glfw
from OpenGL.GL import *

k=3

def render():
    global k
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_LINE_LOOP)
    for i in np.arange(12):
        glVertex2f(np.cos(np.pi*i/6),np.sin(np.pi*i/6))
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0,0)
    glVertex2f(np.cos(np.pi*k/6),np.sin(np.pi*k/6))
    glEnd()
    
def key_callback(window,key,scancode,action,modes):
    global k
    if key==glfw.KEY_1:
        if action==glfw.PRESS:
            k=2
    if key==glfw.KEY_2:
        if action==glfw.PRESS:
            k=1
    if key==glfw.KEY_3:
        if action==glfw.PRESS:
            k=0
    if key==glfw.KEY_4:
        if action==glfw.PRESS:
            k=11
    if key==glfw.KEY_5:
        if action==glfw.PRESS:
            k=10
    if key==glfw.KEY_6:
        if action==glfw.PRESS:
            k=9        
    if key==glfw.KEY_7:
        if action==glfw.PRESS:
            k=8
    if key==glfw.KEY_8:
        if action==glfw.PRESS:
            k=7
    if key==glfw.KEY_9:
        if action==glfw.PRESS:
            k=6
    if key==glfw.KEY_0:
        if action==glfw.PRESS:
            k=5
    if key==glfw.KEY_Q:
        if action==glfw.PRESS:
            k=4        
    if key==glfw.KEY_W:
        if action==glfw.PRESS:
            k=3
    
def main():
    if not glfw.init():
        return
    
    window=glfw.create_window(480,480,"Hello World",None,None)
    if not window:
        glfw.terminate()
        return
    
    glfw.set_key_callback(window,key_callback)
    glfw.make_context_current(window)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

if __name__=="__main__":
    main()
