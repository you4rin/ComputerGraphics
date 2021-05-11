import numpy as np
import glfw
from OpenGL.GL import *

mult=[]

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    # draw cooridnates
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    
    glColor3ub(255, 255, 255)
    
    for i in mult[::-1]:
        glMultMatrixf(i.T)
    
    drawTriangle()
    
def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0.,.5]))
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([.5,0.]))
    glEnd()
    
def key_callback(window,key,scancode,action,modes):
    th=np.radians(10)
    if key==glfw.KEY_A:
        if action==glfw.PRESS or action==glfw.REPEAT:
            mult.append(np.array([[np.cos(th),-np.sin(th),0,0],
                                  [np.sin(th),np.cos(th),0,0],
                                  [0,0,1,0],
                                  [0,0,0,1]]))
    if key==glfw.KEY_D:
        if action==glfw.PRESS or action==glfw.REPEAT:
            mult.append(np.array([[np.cos(-th),-np.sin(-th),0,0],
                                  [np.sin(-th),np.cos(-th),0,0],
                                  [0,0,1,0],
                                  [0,0,0,1]]))
    if key==glfw.KEY_Q:
        if action==glfw.PRESS or action==glfw.REPEAT:
            mult.append(np.array([[1,0,0,-0.1],
                                  [0,1,0,0],
                                  [0,0,1,0],
                                  [0,0,0,1]]))
    if key==glfw.KEY_W:
        if action==glfw.PRESS or action==glfw.REPEAT:
            mult.append(np.array([[1,0,0,0.1],
                                  [0,1,0,0],
                                  [0,0,1,0],
                                  [0,0,0,1]]))
    if key==glfw.KEY_1:
        if action==glfw.PRESS or action==glfw.REPEAT:
            mult.clear()
            
def main():
    if not glfw.init():
        return
    
    window=glfw.create_window(480,480,"2019027001",None,None)
    if not window:
        glfw.terminate()
        return
    
    glfw.set_key_callback(window,key_callback)
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

if __name__=="__main__":
    main()
