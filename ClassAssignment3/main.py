import glfw 
from OpenGL.GL import * 
from OpenGL.GLU import * 
import numpy as np 

r=10.
t=None
eps=1e-9
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
motionMode=False
boxMode=False
smaller=False
tree=None
jointList=None
frames=None
frametime=0.
framenum = 0

class Tree:
    def __init__(self,root):
        self.root=root
        self.offset=[]
        self.channel=[]
        self.name=None
        self.child=[]
        
    def add_child(self,other):
        self.child.append(other)
        
    def set_name(self,name):
        self.name=name
    
    def set_offset(self,offset):
        self.offset=offset
        
    def set_channel(self,channel):
        self.channel=channel

def set_next_idx():
    global framenum, frames
    if frames == None or len(frames) == 0 or not motionMode:
        return
    framenum = (framenum + 1) % len(frames)
        
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
    
def get_data(cnt):
    global framenum,frames
    #print(len(frames),framenum,len(frames[framenum]),cnt)
    if not motionMode:
        return 0.
    return frames[framenum][cnt]

def make_translate(x,y,z):
    global smaller
    ret=np.identity(4)
    #print('x,y,z before: ',x,y,z)
    if smaller:
        x*=0.01
        y*=0.01
        z*=0.01
    #print('x,y,z after: ',x,y,z)
    ret[0][3]=x
    ret[1][3]=y
    ret[2][3]=z
    return ret

def make_rotate(degree,x,y,z):
    ret=np.identity(4)
    th=np.radians(degree)
    if x:
        ret[1][1]=np.cos(th)
        ret[1][2]=-np.sin(th)
        ret[2][1]=np.sin(th)
        ret[2][2]=np.cos(th)
    elif y:
        ret[0][0]=np.cos(th)
        ret[0][2]=np.sin(th)
        ret[2][0]=-np.sin(th)
        ret[2][2]=np.cos(th)
    elif z:
        ret[0][0]=np.cos(th)
        ret[0][1]=-np.sin(th)
        ret[1][0]=np.sin(th)
        ret[1][1]=np.cos(th)
    return ret

def render_line(M,root,cnt):
    M=M@make_translate(*root.offset)
    for i in root.channel:
        #print(cnt)
        if i[:2]=='XP' or i[:2]=='Xp':
            M=M@make_translate(get_data(cnt),0.,0.)
        elif i[:2]=='YP' or i[:2]=='Yp':
            M=M@make_translate(0.,get_data(cnt),0.)
        elif i[:2]=='ZP' or i[:2]=='Zp':
            M=M@make_translate(0.,0.,get_data(cnt))
        elif i[:2]=='XR' or i[:2]=='Xr':
            M=M@make_rotate(get_data(cnt),True,False,False)
        elif i[:2]=='YR' or i[:2]=='Yr':
            M=M@make_rotate(get_data(cnt),False,True,False)
        elif i[:2]=='ZR' or i[:2]=='Zr':
            M=M@make_rotate(get_data(cnt),False,False,True)
        cnt+=1
    if not root.root:
        #print("Vertex Added in",root.name)
        glVertex3fv((M@np.array([0.,0.,0.,1.]))[:3])
    for i in root.child:
        #print("Vertex Added in",root.name)
        glVertex3fv((M@np.array([0.,0.,0.,1.]))[:3])
        cnt=render_line(M,i,cnt)
    return cnt

def draw_cube(name):
    x1=y1=z1=-0.03
    x2=y2=z2=0.03
    if name=='Spine':
        y1=-0.05
        y2=0.15
    elif name=='RightLeg' or name=='LeftLeg' or name=='RightUpLeg' or name=='LeftUpLeg':
        y1=-0.3
        y2=0.05
    elif name=='RightArm' or name=='RightForeArm':
        x1=-0.05
        x2=0.2
    elif name=='LeftArm' or name=='LeftForeArm':
        x1=-0.2
        x2=0.05
    varr=np.array([[x1,y2,z2],[x2,y1,z2],[x2,y2,z2],
                   [x1,y2,z2],[x1,y1,z2],[x2,y1,z2],
                   [x1,y2,z1],[x2,y2,z1],[x2,y1,z1],
                   [x1,y2,z1],[x2,y2,z1],[x2,y1,z1],
                   [x1,y2,z2],[x2,y2,z2],[x2,y2,z1],
                   [x1,y2,z2],[x2,y2,z1],[x1,y2,z1],
                   [x1,y1,z2],[x2,y1,z1],[x2,y1,z2],
                   [x1,y1,z2],[x1,y1,z1],[x2,y1,z1],
                   [x2,y2,z2],[x2,y1,z2],[x2,y1,z1],
                   [x2,y2,z2],[x2,y1,z1],[x2,y2,z1],
                   [x1,y2,z2],[x1,y1,z1],[x1,y1,z2],
                   [x1,y2,z2],[x1,y2,z1],[x1,y1,z1]
                  ],'float32')
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 3*varr.itemsize, varr)
    glDrawArrays(GL_TRIANGLES, 0, int(varr.size/3))

def render_box(root,cnt):
    glPushMatrix()
    glTranslatef(*root.offset)
    for i in root.channel:
        if i[:2]=='XP' or i[:2]=='Xp':
            glTranslatef(get_data(cnt),0.,0.)
        elif i[:2]=='YP' or i[:2]=='Yp':
            glTranslatef(0.,get_data(cnt),0.)
        elif i[:2]=='ZP' or i[:2]=='Zp':
            glTranslatef(0.,0.,get_data(cnt))
        elif i[:2]=='XR' or i[:2]=='Xr':
            glRotatef(get_data(cnt),1.,0.,0.)
        elif i[:2]=='YR' or i[:2]=='Yr':
            glRotatef(get_data(cnt),0.,1.,0.)
        elif i[:2]=='ZR' or i[:2]=='Zr':
            glRotatef(get_data(cnt),0.,0.,1.)
        cnt+=1
    draw_cube(root.name)
    for i in root.child:
        cnt=render_box(i,cnt)
    glPopMatrix()
    return cnt
    
def render():
    global eyePoint,lookAt,upVec,axisVec,orthogonal,r
    global tree,motionMode,boxMode,smaller
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
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
    
    glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
    
    if boxMode:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        lightPos=(3.,4.,5.,1.)
        glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
        lightColor=(1.,1.,1.,1.)
        ambientLightColor=(.1,.1,.1,1.)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
        glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)
        objectColor=(0.72265625,0.65234375,0.984375,1.)
        specularObjectColor=(1.,1.,1.,1.)
        glMaterialfv(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,objectColor)
        glMaterialfv(GL_FRONT,GL_SHININESS,10)
        glMaterialfv(GL_FRONT,GL_SPECULAR,specularObjectColor)
        render_box(tree,0)
        glDisable(GL_LIGHTING)
    elif tree != None:
        glColor3ub(0xB9,0xA7,0xFC)
        glBegin(GL_LINES)
        render_line(np.identity(4),tree,0)
        glEnd()
        
    set_next_idx()
    
    
def key_callback(window,key,scancode,action,mods):
    global orthogonal,motionMode,framenum
    if key==glfw.KEY_V:
        if action==glfw.PRESS:
            if orthogonal:
                orthogonal=False
            else:
                orthogonal=True
    if key==glfw.KEY_SPACE:
        if action==glfw.PRESS:
            motionMode=not motionMode
            framenum=0


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
    global tree,jointList,frames,frametime,boxMode,framenum,smaller
    tree=None
    jointList=[]
    chancnt=0
    framenum=0
    framecnt=0
    frames=[]
    node=[]
    curPath=paths[0]
    filename=curPath.replace('\\','/').split('/')[-1]
    print("File name:",filename)
    
    if(filename == 'sample-spin.bvh' or filename == 'sample-walk.bvh'):
        boxMode = True
        smaller = False
    else:
        boxMode = False
        smaller = True
    
    f=open(curPath)
    for line in f:
        curLine=line.strip().split()
        #print(curLine)
        if len(curLine)==0:
            continue
        if curLine[0]=='ROOT':
            node.append(Tree(True))
            tree=node[-1]
            jointList.append(curLine[1])
            node[-1].set_name(curLine[1])
            #print('Root append')
        if curLine[0]=='JOINT':
            node.append(Tree(False))
            node[-2].add_child(node[-1])
            jointList.append(curLine[1])
            node[-1].set_name(curLine[1])
            #print('Joint append')
        if curLine[0]=='End':
            node.append(Tree(False))
            node[-2].add_child(node[-1])
            node[-1].set_name("End Site")
            #print('End append')
        if curLine[0]=='OFFSET':
            node[-1].set_offset([float(i) for i in curLine[1:]])
        if curLine[0]=='CHANNELS':
            node[-1].set_channel(curLine[2:])
            chancnt+=int(curLine[1])
        if curLine[0]=='}':
            node.pop()
            #print('pop')
        if curLine[0]=='Frames:':
            framecnt=int(curLine[1])
        if curLine[0]=='Frame':
            frametime=float(curLine[2])
        if framecnt!=0 and len(curLine)==chancnt:
            frames.append([float(i) for i in curLine])
    print('Number of frames:',framecnt)
    print('FPS:',int(round(1/frametime)))
    print('Number of joints (including root):',len(jointList))
    print('List of all joint names:')
    for i in jointList:
        print(i)
    
def main():
    global t
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
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        t=glfw.get_time()
        render()
        glfw.swap_buffers(window)

if __name__=="__main__":
    main()
