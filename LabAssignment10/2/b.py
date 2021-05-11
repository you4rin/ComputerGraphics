import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo

gCamAng = 0.
gCamHeight = 1.
frameCnt = 0


def createVertexAndIndexArrayIndexed():
    varr = np.array([
            ( -0.5773502691896258 , 0.5773502691896258 ,  0.5773502691896258 ),
            ( -1 ,  1 ,  1 ), # v0
            ( 0.8164965809277261 , 0.4082482904638631 ,  0.4082482904638631 ),
            (  1 ,  1 ,  1 ), # v1
            ( 0.4082482904638631 , -0.4082482904638631 ,  0.8164965809277261 ),
            (  1 , -1 ,  1 ), # v2
            ( -0.4082482904638631 , -0.8164965809277261 ,  0.4082482904638631 ),
            ( -1 , -1 ,  1 ), # v3
            ( -0.4082482904638631 , 0.4082482904638631 , -0.8164965809277261 ),
            ( -1 ,  1 , -1 ), # v4
            ( 0.4082482904638631 , 0.8164965809277261 , -0.4082482904638631 ),
            (  1 ,  1 , -1 ), # v5
            ( 0.5773502691896258 , -0.5773502691896258 , -0.5773502691896258 ),
            (  1 , -1 , -1 ), # v6
            ( -0.8164965809277261 , -0.4082482904638631 , -0.4082482904638631 ),
            ( -1 , -1 , -1 ), # v7
            ], 'float32')
    iarr = np.array([
            (0,2,1),
            (0,3,2),
            (4,5,6),
            (4,6,7),
            (0,1,5),
            (0,5,4),
            (3,6,2),
            (3,7,6),
            (1,2,6),
            (1,6,5),
            (0,7,3),
            (0,4,7),
            ])
    return varr, iarr

def drawCube_glDrawElements():
    global gVertexArrayIndexed, gIndexArray
    varr = gVertexArrayIndexed
    iarr = gIndexArray
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([3.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,3.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,3.]))
    glEnd()
    
def makeRotMat(x, y, z):
    R = np.identity(4)
    x=np.radians(x)
    y=np.radians(y)
    z=np.radians(z)
    R = R @ np.array([[1.,0.,0.,0.],
                      [0.,np.cos(x),-np.sin(x),0.],
                      [0.,np.sin(x),np.cos(x),0.],
                      [0.,0.,0.,1.]])
    R = R @ np.array([[np.cos(y),0.,np.sin(y),0.],
                      [0.,1.,0.,0.],
                      [-np.sin(y),0.,np.cos(y),0.],
                      [0.,0.,0.,1.]])
    R = R @ np.array([[np.cos(z),-np.sin(z),0.,0.],
                      [np.sin(z),np.cos(z),0.,0.],
                      [0.,0.,1.,0.],
                      [0.,0.,0.,1.]])
    return R
    
def l2norm(v):
    return np.sqrt(np.dot(v, v))

def normalized(v):
    l = l2norm(v)
    return 1/l * np.array(v)

def exp(rv):
    th = l2norm(rv)
    eps = 1e-6
    if(abs(th) < eps):
        return np.identity(3)
    rv = normalized(rv)
    x, y, z = rv[0], rv[1], rv[2]
    cth, sth = np.cos(th),np.sin(th)
    return np.array([[cth+x*x*(1-cth),x*y*(1-cth)-z*sth,x*z*(1-cth)+y*sth],
                     [y*x*(1-cth)+z*sth,cth+y*y*(1-cth),y*z*(1-cth)-x*sth],
                     [z*x*(1-cth)-y*sth,z*y*(1-cth)+x*sth,cth+z*z*(1-cth)]])

def log(R):
    tr = R[0,0]+R[1,1]+R[2,2]
    eps = 1e-6
    if abs(tr - 3.0) < eps:
        return np.array([0., 0., 0.])
    if abs(tr + 1.0) < eps:
        th = np.pi;
        if abs(R[2,2] + 1.0) > eps:
            return th/np.sqrt(2*(1+R[2,2]))*np.array([R[0,2],R[1,2],1+R[2,2]])
        if abs(R[1,1] + 1.0) > eps:
            return th/np.sqrt(2*(1+R[1,1]))*np.array([R[0,1],1+R[1,1],R[2,1]])
        else:
            return th/np.sqrt(2*(1+R[0,0]))*np.array([1+R[0,0],R[1,0],R[2,0]])
    th = np.arccos((tr-1)/2)
    num = 2*np.sin(th)
    return th/num*np.array([R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]])

def slerp(R1, R2, t):
    return R1@exp(t*log(R1.T@R2))    
    
def render(t):
    global gCamAng, gCamHeight,frameCnt
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1,10)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5*np.sin(gCamAng),gCamHeight,5*np.cos(gCamAng), 0,0,0, 0,1,0)

    # draw global frame
    drawFrame()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_RESCALE_NORMAL)

    lightPos = (3.,4.,5.,1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)

    lightColor = (1.,1.,1.,1.)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)
    
    R1_0 = makeRotMat(20,30,30)
    R1_20 = makeRotMat(45,60,40)
    R1_40 = makeRotMat(60,70,50)
    R1_60 = makeRotMat(80,85,70)
    R2_0 = makeRotMat(15,30,25)
    R2_20 = makeRotMat(25,40,40)
    R2_40 = makeRotMat(40,60,50)
    R2_60 = makeRotMat(55,80,65)
    T1 = np.identity(4)
    T1[0][3] = 1.
    
    # frame 0
    
    glPushMatrix()
    J1 = R1_0
    glMultMatrixf(J1.T)
    glPushMatrix()
    objectColor = (1.,0.,0.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    J2 = R1_0 @ T1 @ R2_0

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    # frame 20
    
    glPushMatrix()
    J1 = R1_20
    glMultMatrixf(J1.T)
    glPushMatrix()
    objectColor = (1.,1.,0.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
    
    J2 = R1_20 @ T1 @ R2_20

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
    
    # frame 40
    
    glPushMatrix()
    J1 = R1_40
    glMultMatrixf(J1.T)
    glPushMatrix()
    objectColor = (0.,1.,0.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
    
    J2 = R1_40 @ T1 @ R2_40

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    # frame 60
    
    glPushMatrix()
    J1 = R1_60
    glMultMatrixf(J1.T)
    glPushMatrix()
    objectColor = (0.,0.,1.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
    
    J2 = R1_60 @ T1 @ R2_60

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()
    
    # current frame
    
    if(frameCnt % 20 != 0):
        glPushMatrix()
        R1_cur=np.identity(4)
        R2_cur=np.identity(4)
        if(0<frameCnt<20):
            R1_cur[:3,:3]=slerp(R1_0[:3,:3],R1_20[:3,:3],frameCnt/20)
        if(20<frameCnt<40):
            R1_cur[:3,:3]=slerp(R1_20[:3,:3],R1_40[:3,:3],(frameCnt-20)/20)
        if(40<frameCnt<60):
            R1_cur[:3,:3]=slerp(R1_40[:3,:3],R1_60[:3,:3],(frameCnt-40)/20)
        J1 = R1_cur
        glMultMatrixf(J1.T)
        glPushMatrix()
        objectColor = (1.,1.,1.,1.)
        specularObjectColor = (1.,1.,1.,1.)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
        glMaterialfv(GL_FRONT, GL_SHININESS, 10)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()
        glPopMatrix()

        if(0<frameCnt<20):
            R2_cur[:3,:3]=slerp(R2_0[:3,:3],R2_20[:3,:3],frameCnt/20)
        if(20<frameCnt<40):
            R2_cur[:3,:3]=slerp(R2_20[:3,:3],R2_40[:3,:3],(frameCnt-20)/20)
        if(40<frameCnt<60):
            R2_cur[:3,:3]=slerp(R2_40[:3,:3],R2_60[:3,:3],(frameCnt-40)/20)
        J2 = R1_cur @ T1 @ R2_cur

        glPushMatrix()
        glMultMatrixf(J2.T)
        glPushMatrix()
        glTranslatef(0.5,0,0)
        glScalef(0.5, 0.05, 0.05)
        drawCube_glDrawElements()
        glPopMatrix()
        glPopMatrix()
    
    glDisable(GL_LIGHTING)
    
    frameCnt += 1
    frameCnt %= 61


def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight
    # rotate the camera when 1 or 3 key is pressed or repeated
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key==glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key==glfw.KEY_2:
            gCamHeight += .1
        elif key==glfw.KEY_W:
            gCamHeight += -.1

gVertexArrayIndexed = None
gIndexArray = None

def main():
    global gVertexArrayIndexed, gIndexArray
    if not glfw.init():
        return
    window = glfw.create_window(640,640,'2019027001', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    gVertexArrayIndexed, gIndexArray = createVertexAndIndexArrayIndexed()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        t = glfw.get_time()
        render(t)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
