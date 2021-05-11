import numpy as np
import glfw
from OpenGL.GL import *

def render(th):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()

    glColor3ub(255, 255, 255)
    # calculate matrix M1, M2 using th
    # your implementation
    M1=np.array([[np.cos(th),-np.sin(th)],
                  [np.sin(th),np.cos(th)]])@np.array([[2,0],[0,2]])
    M2=np.array([[np.cos(th),-np.sin(th)],
                  [np.sin(th),np.cos(th)]])

    # draw point p
    glBegin(GL_POINTS)
    # your implementation
    glVertex2fv(M1@np.array([.5,0.]))
    glVertex2fv(M1@np.array([0.,.5]))
    glEnd()
    # draw vector v
    glBegin(GL_LINES)
    # your implementation
    glVertex2fv(M2@np.array([0.,0.]))
    glVertex2fv(M2@np.array([.5,0.]))
    glVertex2fv(M2@np.array([0.,0.]))
    glVertex2fv(M2@np.array([0.,.5]))
    glEnd()
    
def main():
    if not glfw.init():
        return
    
    window=glfw.create_window(480,480,"2019027001",None,None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        t=glfw.get_time()
        render(t)
        glfw.swap_buffers(window)

if __name__=="__main__":
    main()
