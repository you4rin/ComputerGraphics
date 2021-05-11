import glfw 
from OpenGL.GL import * 
from OpenGL.GLU import * 
import numpy as np
import ctypes

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
isSingle=True
curPath=None
vectices=[]
normals=[]
mean_normals=None
varr=None
smooth_varr=None
stomp_vertices=[]
stomp_normals=[]
stomp_mean_normals=None
stomp_varr=None
stomp_smooth_varr=None
branch_vertices=[]
branch_normals=[]
branch_mean_normals=None
branch_varr=None
branch_smooth_varr=None
leaf_vertices=[]
leaf_normals=[]
leaf_mean_normals=None
leaf_varr=None
leaf_mean_normals=None
wireFrame=False

def drawUnitSquare():
    glBegin(GL_LINES)
    glVertex3f(0.,0.,0.)
    glVertex3f(0.,0.,1.)
    glVertex3f(0.,0.,1.)
    glVertex3f(1.,0.,1.)
    glVertex3f(1.,0.,1.)
    glVertex3f(1.,0.,0.)
    glVertex3f(1.,0.,0.)
    glVertex3f(0.,0.,0.)
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
    
def obj_render():
    global curPath,vertices,normals,varr
    if curPath==None:
        return
    objectColor=(.5,.5,.5,1.)
    specularObjectColor=(1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
    glMaterialfv(GL_FRONT,GL_SHININESS,10)
    glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT,6*varr.itemsize,varr)
    glVertexPointer(3,GL_FLOAT,6*varr.itemsize,
                    ctypes.c_void_p(varr.ctypes.data+3*varr.itemsize))
    glDrawArrays(GL_TRIANGLES,0,int(varr.size/6))
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)

def load_tree():
    global stomp_vertices,stomp_normals,stomp_varr,stomp_mean_normals,stomp_smooth_varr
    global branch_vertices,branch_normals,branch_varr,branch_mean_normals,branch_smooth_varr
    global leaf_vertices,leaf_normals,leaf_varr,leaf_mean_normals,leaf_smooth_varr
    path='./obj_files/stomp.obj'
    f=open(path)
    
    for line in f:
        curLine=line.split()
        if(len(curLine)==0):
            continue
        if curLine[0]=='v':
            stomp_vertices.append(tuple([eval(i) for i in curLine[1:4]]))
        if curLine[0]=='vn':
            stomp_normals.append(tuple([eval(i) for i in curLine[1:4]]))
        if curLine[0]=='f':
            tmp=[]
            for i in curLine[1:]:
                div=i.split('/')
                tmp.append([int(i) for i in div])
            for i in range(1,len(tmp)-1):
                if(type(stomp_varr)!=np.ndarray):
                    stomp_varr=np.array(stomp_normals[tmp[i-1][2]-1])
                else:
                    stomp_varr=np.vstack((stomp_varr,stomp_normals[tmp[i-1][2]-1]))
                stomp_varr=np.vstack((stomp_varr,stomp_vertices[tmp[i-1][0]-1]))
                stomp_varr=np.vstack((stomp_varr,stomp_normals[tmp[i][2]-1]))
                stomp_varr=np.vstack((stomp_varr,stomp_vertices[tmp[i][0]-1]))
                stomp_varr=np.vstack((stomp_varr,stomp_normals[tmp[-1][2]-1]))
                stomp_varr=np.vstack((stomp_varr,stomp_vertices[tmp[-1][0]-1]))
    stomp_varr=stomp_varr.astype(np.float32)
    
    path='./obj_files/branch.obj'
    f=open(path)
    for line in f:
        curLine=line.split()
        if(len(curLine)==0):
            continue
        if curLine[0]=='v':
            branch_vertices.append(tuple([eval(i) for i in curLine[1:4]]))
        if curLine[0]=='vn':
            branch_normals.append(tuple([eval(i) for i in curLine[1:4]]))
        if curLine[0]=='f':
            tmp=[]
            for i in curLine[1:]:
                div=i.split('/')
                tmp.append([int(i) for i in div])
            for i in range(1,len(tmp)-1):
                if(type(branch_varr)!=np.ndarray):
                    branch_varr=np.array(branch_normals[tmp[i-1][2]-1])
                else:
                    branch_varr=np.vstack((branch_varr,branch_normals[tmp[i-1][2]-1]))
                branch_varr=np.vstack((branch_varr,branch_vertices[tmp[i-1][0]-1]))
                branch_varr=np.vstack((branch_varr,branch_normals[tmp[i][2]-1]))
                branch_varr=np.vstack((branch_varr,branch_vertices[tmp[i][0]-1]))
                branch_varr=np.vstack((branch_varr,branch_normals[tmp[-1][2]-1]))
                branch_varr=np.vstack((branch_varr,branch_vertices[tmp[-1][0]-1]))
    branch_varr=branch_varr.astype(np.float32)
    path='./obj_files/leaf.obj'
    f=open(path)
    for line in f:
        curLine=line.split()
        if(len(curLine)==0):
            continue
        if curLine[0]=='v':
            leaf_vertices.append(tuple([eval(i) for i in curLine[1:4]]))
        if curLine[0]=='vn':
            leaf_normals.append(tuple([eval(i) for i in curLine[1:4]]))
        if curLine[0]=='f':
            tmp=[]
            for i in curLine[1:]:
                div=i.split('/')
                tmp.append([int(i) for i in div])
            for i in range(1,len(tmp)-1):
                if(type(leaf_varr)!=np.ndarray):
                    leaf_varr=np.array(leaf_normals[tmp[i-1][2]-1])
                else:
                    leaf_varr=np.vstack((leaf_varr,leaf_normals[tmp[i-1][2]-1]))
                leaf_varr=np.vstack((leaf_varr,leaf_vertices[tmp[i-1][0]-1]))
                leaf_varr=np.vstack((leaf_varr,leaf_normals[tmp[i][2]-1]))
                leaf_varr=np.vstack((leaf_varr,leaf_vertices[tmp[i][0]-1]))
                leaf_varr=np.vstack((leaf_varr,leaf_normals[tmp[-1][2]-1]))
                leaf_varr=np.vstack((leaf_varr,leaf_vertices[tmp[-1][0]-1]))
    leaf_varr=leaf_varr.astype(np.float32)
    
def tree_render(t):
    objectColor=(.5859375,.29296875,0.,1.)
    specularObjectColor=(1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
    glMaterialfv(GL_FRONT,GL_SHININESS,10)
    glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
    
    glPushMatrix()
    glTranslatef(abs(t%2-1)-0.5,0,abs(t%2-1)-0.5)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT,6*stomp_varr.itemsize,stomp_varr)
    glVertexPointer(3,GL_FLOAT,6*stomp_varr.itemsize,
                    ctypes.c_void_p(stomp_varr.ctypes.data+3*stomp_varr.itemsize))
    glDrawArrays(GL_TRIANGLES,0,int(stomp_varr.size/6))
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)
    
    glPushMatrix()
    glTranslatef(0,1.5,0)
    glRotatef(57.5+5*np.sin(t),1,0,1)
    glScalef(0.001,0.001,0.001)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT,6*branch_varr.itemsize,branch_varr)
    glVertexPointer(3,GL_FLOAT,6*branch_varr.itemsize,
                    ctypes.c_void_p(branch_varr.ctypes.data+3*branch_varr.itemsize))
    glDrawArrays(GL_TRIANGLES,0,int(branch_varr.size/6))
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)
    
    objectColor=(.50390625,.75390625,.27734375,1.)
    specularObjectColor=(1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
    glMaterialfv(GL_FRONT,GL_SHININESS,10)
    glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
    
    glPushMatrix()
    glScalef(20,10,20)
    glTranslatef(-15,158,1)
    glRotatef(125.5-5*np.sin(t),1,0,1)
    glRotatef(30*np.sin(t),1,0,1)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT,6*leaf_varr.itemsize,leaf_varr)
    glVertexPointer(3,GL_FLOAT,6*leaf_varr.itemsize,
                    ctypes.c_void_p(leaf_varr.ctypes.data+3*leaf_varr.itemsize))
    glDrawArrays(GL_TRIANGLES,0,int(leaf_varr.size/6))
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)
    glPopMatrix()
    glPopMatrix() 
    
    objectColor=(.5859375,.29296875,0.,1.)
    specularObjectColor=(1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
    glMaterialfv(GL_FRONT,GL_SHININESS,10)
    glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
    
    glPushMatrix()
    glTranslatef(0,1.7,0)
    glRotatef(-57.5+5*np.sin(t),1,0,1)
    glScalef(0.001,0.001,0.001)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT,6*branch_varr.itemsize,branch_varr)
    glVertexPointer(3,GL_FLOAT,6*branch_varr.itemsize,
                    ctypes.c_void_p(branch_varr.ctypes.data+3*branch_varr.itemsize))
    glDrawArrays(GL_TRIANGLES,0,int(branch_varr.size/6))
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)
    
    objectColor=(.50390625,.75390625,.27734375,1.)
    specularObjectColor=(1.,1.,1.,1.)
    glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
    glMaterialfv(GL_FRONT,GL_SHININESS,10)
    glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
    
    glPushMatrix()
    glScalef(20,10,20)
    glTranslatef(14,155,4)
    glRotatef(-125.5-5*np.sin(t),1,0,1)
    glRotatef(30*np.sin(t),1,0,1)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT,6*leaf_varr.itemsize,leaf_varr)
    glVertexPointer(3,GL_FLOAT,6*leaf_varr.itemsize,
                    ctypes.c_void_p(leaf_varr.ctypes.data+3*leaf_varr.itemsize))
    glDrawArrays(GL_TRIANGLES,0,int(leaf_varr.size/6))
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)
    glPopMatrix()
    glPopMatrix()   
    glPopMatrix() 
    
def render(t):
    global eyePoint,lookAt,upVec,axisVec,orthogonal,r,curPath
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    if wireFrame:
        glPolygonMode(GL_FRONT_AND_BACK,GL_LINE )
    else:
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL )
    glLoadIdentity()
    glViewport(0,0,960,960)
    if orthogonal:
        glOrtho(-r/2.5,r/2.5,-r/2.5,r/2.5,1.,800.)
    else:
        gluPerspective(45.,1.,1.,400.)
    setCam(eyePoint+axisVec,lookAt+axisVec,upVec)
    drawFrame()
    glColor3ub(255,255,255)
    drawSquareArray()
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_NORMALIZE)
    
    glPushMatrix()
    lightPos0=(3.,4.,5.,1.)
    lightPos1=(-3.,4.,-5.,1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos0)
    glLightfv(GL_LIGHT1, GL_POSITION, lightPos1)
    glPopMatrix()
    
    lightColor0=(1.,1.,1.,1.)
    #lightColor0=(0.,0.,0.,0.)
    ambientLightColor0=(.1,.1,.1,1.)
    lightColor1=(1.,1.,1.,1.)
    ambientLightColor1=(.1,.1,.1,1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor0)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor0)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, lightColor1)
    glLightfv(GL_LIGHT1, GL_SPECULAR, lightColor1)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLightColor1) 
    
    if isSingle:
        obj_render()
    else:
        tree_render(t)
        
    glDisable(GL_LIGHTING)
    
def key_callback(window,key,scancode,action,mods):
    global orthogonal,isSingle,wireFrame
    if key==glfw.KEY_V:
        if action==glfw.PRESS:
            if orthogonal:
                orthogonal=False
            else:
                orthogonal=True
    if key==glfw.KEY_H:
        if action==glfw.PRESS:
            isSingle=not isSingle
    if key==glfw.KEY_Z:
        if action==glfw.PRESS:
            wireFrame=not wireFrame


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

def drop_callback(window,paths):
    global curPath,vertices,normals,varr
    if isSingle:
        curPath=paths[0]
        print("File name:",curPath.replace('\\','/').split('/')[-1])
        vertices=[]
        f=open(curPath)
        three=0
        four=0
        multi=0
        varr=None
        for line in f:
            curLine=line.split()
            if(len(curLine)==0):
                continue
            if curLine[0]=='v':
                vertices.append(tuple([eval(i) for i in curLine[1:4]]))
            if curLine[0]=='vn':
                normals.append(tuple([eval(i) for i in curLine[1:4]]))
            if curLine[0]=='f':
                if(len(curLine)==4):
                    three+=1
                elif(len(curLine)==5):
                    four+=1
                else:
                    multi+=1
                tmp=[]
                for i in curLine[1:]:
                    div=i.replace('//','/').split('/')
                    tmp.append([int(i) for i in div])
                for i in range(1,len(tmp)-1):
                    if(type(varr)!=np.ndarray):
                        if(len(tmp[i-1])==2):
                            varr=np.array(normals[tmp[i-1][1]-1])
                        else:
                            varr=np.array(normals[tmp[i-1][2]-1])
                    else:
                        if(len(tmp[i-1])==2):
                            varr=np.vstack((varr,normals[tmp[i-1][1]-1]))
                        else:
                            varr=np.vstack((varr,normals[tmp[i-1][2]-1]))
                    varr=np.vstack((varr,vertices[tmp[i-1][0]-1]))
                    if(len(tmp[i-1])==2):
                        varr=np.vstack((varr,normals[tmp[i][1]-1]))
                    else:
                        varr=np.vstack((varr,normals[tmp[i][2]-1]))
                    varr=np.vstack((varr,vertices[tmp[i][0]-1]))
                    if(len(tmp[i-1])==2):
                        varr=np.vstack((varr,normals[tmp[-1][1]-1]))
                    else:
                        varr=np.vstack((varr,normals[tmp[-1][2]-1]))
                    varr=np.vstack((varr,vertices[tmp[-1][0]-1]))
        varr=varr.astype(np.float32)
        print('Total nuber of faces:',three+four+multi)
        print('Number of faces with 3 vertices:',three)
        print('Number of faces with 4 vertices:',four)
        print('Number of faces with more than 4 vertices:',multi)
        
    
    
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
    glfw.set_drop_callback(window,drop_callback)
    glfw.swap_interval(1)
    
    load_tree()
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        t=glfw.get_time()
        render(t) 
        glfw.swap_buffers(window)

if __name__=="__main__":
    main()
