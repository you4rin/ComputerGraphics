import glfw 
from OpenGL.GL import * 
from OpenGL.GLU import * 
import numpy as np 

r=10.
azimuth=np.radians(45)
elevation=np.radians(35.264)
eyePoint=np.array([r*np.cos(elevation)*np.sin(azimuth),r*np.sin(elevation),r*np.cos(elevation)*np.cos(azimuth)])
lookAt=np.array([0.,0.,0.])
axisVec=np.array([0.,0.,0.])
upVec=np.array([0.,1.,0.])
leftButtonClicked=False
rightButtonClicked=False
mouseXpos=0.
mouseYpos=0.
orthogonal=False

def drawUnitSquare():
    glBegin(GL_QUADS)
    glVertex3f(0.,0.,0.)
    glVertex3f(0.,0.,1.)
    glVertex3f(1.,0.,1.)
    glVertex3f(1.,0.,0.)
    glEnd()
    
def drawSquareArray():
    for i in range(-20,21):
        for j in range(-20,21):
            glPushMatrix()
            glTranslatef(i,0,j)
            glScalef(1.,1.,1.)
            drawUnitSquare()
            glPopMatrix()

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255,0,0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([1.,0.,0.]))
    glColor3ub(0,255,0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,1.,0.]))
    glColor3ub(0,0,255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,1.]))
    glEnd()
    
def setCam(eye,at,up):
    gluLookAt(*eye,*at,*up)
    
def render():
    global eyePoint,lookAt,upVec,axisVec,orthogonal,r
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK,GL_LINE )
    glLoadIdentity()
    glViewport(0,0,960,960)
    if orthogonal:
        glOrtho(-r/2.5,r/2.5,-r/2.5,r/2.5,1.,400.)
    else:
        gluPerspective(45.,1.,1.,400.)
    setCam(eyePoint+axisVec,lookAt+axisVec,upVec)
    drawFrame()
    glColor3ub(255,255,255)
    drawSquareArray()
    
def key_callback(window,key,scancode,action,mods):
    global orthogonal
    if(key==glfw.KEY_V):
        if action==glfw.PRESS:
            if orthogonal:
                orthogonal=False
            else:
                orthogonal=True


def mouse_callback(window,button,action,mods):
    global leftButtonClicked,rightButtonClicked
    if button==glfw.MOUSE_BUTTON_LEFT:
        if action==glfw.PRESS or action==glfw.REPEAT:
            leftButtonClicked=True
        else:
            leftButtonClicked=False
    if button==glfw.MOUSE_BUTTON_RIGHT:
        if action==glfw.PRESS or action==glfw.REPEAT:
            rightButtonClicked=True
        else:
            rightButtonClicked=False
            

def cursor_pos_callback(window,xpos,ypos):
    global mouseXpos,mouseYpos,leftButtonClicked,rightButtonClicked
    global azimuth,elevation,eyePoint,lookAt,upVec,axisVec
    if leftButtonClicked:
        azimuth+=np.radians((mouseXpos-xpos)/8)
        elevation+=np.radians((ypos-mouseYpos)/8)
    if rightButtonClicked:
        w=(eyePoint-lookAt)/np.sqrt(np.dot(eyePoint-lookAt,eyePoint-lookAt))
        u=(np.cross(upVec,w))/np.sqrt(np.dot(np.cross(upVec,w),np.cross(upVec,w)))
        v=np.cross(w,u)
        axisVec+=u*(mouseXpos-xpos)/90
        axisVec+=v*(ypos-mouseYpos)/90
    eyePoint=np.array([r*np.cos(elevation)*np.sin(azimuth),r*np.sin(elevation),r*np.cos(elevation)*np.cos(azimuth)])
    mouseXpos=xpos
    mouseYpos=ypos    

def scroll_callback(window,xoffset,yoffset):
    global r,eyePoint,elevation,azimuth
    r+=yoffset/5
    if(r<=0):
        r=0
    eyePoint=np.array([r*np.cos(elevation)*np.sin(azimuth),r*np.sin(elevation),r*np.cos(elevation)*np.cos(azimuth)])

def main():
    if not glfw.init():
        return
    
    window=glfw.create_window(960,960,"",None,None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window,key_callback)
    glfw.set_mouse_button_callback(window,mouse_callback)
    glfw.set_cursor_pos_callback(window,cursor_pos_callback)
    glfw.set_scroll_callback(window,scroll_callback)
    glfw.swap_interval(1)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        t=glfw.get_time()
        render()
        glfw.swap_buffers(window)

if __name__=="__main__":
    main()
