import os
os.environ['PYOPENGL_PLATFORM']='egl'
import numpy as np, trimesh
from PIL import Image, ImageDraw, ImageFont
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals
from pathlib import Path
P=Path(__file__).parent
s=trimesh.Scene()
def material(name,c,metal=.0,rough=.7,emissive=None):
 return PBRMaterial(name=name,baseColorFactor=np.array([*c,255],dtype=np.uint8),metallicFactor=metal,roughnessFactor=rough,emissiveFactor=emissive)
mats={
 'ivory':material('PAINTED_SILVER_HOUSING',(171,175,170),.55,.48),
 'edge':material('DARK_METAL_FRAME',(46,52,56),.6,.5),
 'trim':material('BLACK_SCREEN_BEZEL',(13,19,23),.22,.4),
 'glass':material('DARK_GLASS',(9,16,18),.16,.22),
 'silver':material('FASTENERS',(150,155,153),.8,.35),
 'green':material('GREEN_STATUS_LAMP',(65,178,71),.15,.35,[.04,.28,.04]),
 'yellow':material('YELLOW_STATUS_LAMP',(204,183,45),.15,.4,[.23,.17,.015]),
 'amber':material('AMBER_STATUS_LAMP',(224,113,23),.15,.4,[.25,.07,.005]),
 'red':material('RED_STATUS_LAMP',(172,44,32),.15,.4,[.25,.02,.005]),
 'purple':material('PURPLE_STATUS_LAMP',(157,47,141),.15,.4,[.12,.01,.09]),
 'gray':material('INSET_METAL',(112,119,118),.55,.6),
 'case':material('BROWN_DARK_HOUSING',(82,57,45),.25,.72),
 'blueglass':material('BLUE_DISPLAY',(15,16,60),.08,.28,[.01,.015,.20]),
 'blueink':material('BLUE_DISPLAY_ACCENT',(38,42,203),.0,.4,[.06,.07,.6]),
 'greenrim':material('GREEN_DIAL_ACCENT',(43,156,73),.15,.45,[.015,.3,.025]),
 'legend':material('SHIELD_LEGEND_BURGUNDY',(135,25,36),.05,.72),
}
def add(n,mesh,mat):
 mesh.visual=trimesh.visual.TextureVisuals(material=mats[mat]);s.add_geometry(mesh,node_name=n,geom_name=n)
def box(n,dim,pos,mat):
 a=trimesh.creation.box(extents=dim);a.apply_translation(pos);add(n,a,mat)
def bevel(n,w,h,d,r,pos,mat):
 # clipped corners, 3D closed manifold; front is negative Z
 pts=[(-w/2+r,-h/2),(w/2-r,-h/2),(w/2,-h/2+r),(w/2,h/2-r),(w/2-r,h/2),(-w/2+r,h/2),(-w/2,h/2-r),(-w/2,-h/2+r)]
 verts=[(x+pos[0],y+pos[1],pos[2]+z) for z in (-d/2,d/2) for x,y in pts];f=[]
 for i in range(1,7):f.extend([(0,i+1,i),(8,8+i,8+i+1)])
 for i in range(8):j=(i+1)%8;f.extend([(i,j,8+j),(i,8+j,8+i)])
 add(n,trimesh.Trimesh(vertices=verts,faces=f,process=True),mat)
def cyl(n,r,d,pos,mat):
 m=trimesh.creation.cylinder(radius=r,height=d,sections=32);m.apply_translation(pos);add(n,m,mat)
# Console device, visual based on Desktop recording 30.4s. The display text
# is illegible; blue visual marks are non-verbal placeholders, not inferred labels.
bevel('Outer_case',3.16,1.92,1.00,.11,(0,.98,0),'case')
bevel('Main_front_plate',2.95,1.68,.12,.10,(0,.98,-.56),'gray')
bevel('Blue_display_black_bezel',2.58,.42,.08,.09,(0,1.53,-.65),'trim')
bevel('Blue_display_glass',2.43,.28,.045,.07,(0,1.53,-.72),'blueglass')
# Example segment markings only: not a transcription or real device state.
for i in range(29):
 x=-1.10+i*.078
 box('Blue_display_tick_%02d'%i,(.039,.05+(i%3)*.012,.012),(x,1.52,-.747),'blueink')
box('Blue_display_lower_trim',(2.29,.045,.025),(0,1.28,-.67),'trim')
# large textured left control; viewer on -Z sees +X on left
cyl('Left_dial_black_mount',.34,.10,(.96,.47,-.66),'trim')
cyl('Left_dial_ring',.28,.10,(.96,.47,-.72),'edge')
cyl('LEFT_ROTARY_CONTROL',.22,.16,(.96,.47,-.79),'gray')
for i in range(12):
 a=i*2*np.pi/12;x=.96+.19*np.cos(a);y=.47+.19*np.sin(a)
 cyl('Left_dial_grip_%02d'%i,.025,.045,(x,y,-.89),'silver')
for i,x in enumerate([.49,.19,-.11]):
 cyl('Small_knob_mount_%d'%i,.13,.075,(x,.34,-.65),'trim')
 cyl('SMALL_CONTROL_%d'%i,.085,.12,(x,.34,-.71),'edge')
 box('Small_knob_index_%d'%i,(.018,.09,.015),(x,.34,-.78),'silver')
# right-side green accented control in reference.
cyl('Right_control_outer',.34,.10,(-.99,.54,-.65),'trim')
cyl('Right_control_green_ring',.29,.08,(-.99,.54,-.72),'greenrim')
cyl('Right_control_dark_inset',.245,.08,(-.99,.54,-.78),'trim')
cyl('RIGHT_ROTARY_CONTROL',.19,.14,(-.99,.54,-.84),'gray')
box('Right_control_indicator',(.045,.28,.015),(-.99,.54,-.92),'edge')
for x in [-1.39,1.39]:
 for y in [.20,1.77]:cyl('Device_fastener_%s_%s'%(x,y),.035,.025,(x,y,-.64),'silver')
for x in [-1.22,1.22]:box('Lower_rubber_feet_'+str(x),(.42,.11,.72),(x,.015,.04),'trim')
out=P/'KONSOL_CIHAZI_12_ADAY.glb';s.export(out);print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
# Render exact exported GLB with neutral studio illumination.
import OpenGL.arrays.ctypesparameters
import pyrender
import ctypes
from OpenGL.raw.GL.VERSION.GL_1_1 import glGenTextures as rawGenTextures
import pyrender.texture
# Avoid PyOpenGL wrapper's unsupported ctypes pointer auto-conversion.
def gen_texture(n):
    a=(ctypes.c_uint*n)();rawGenTextures(n,a);return a[0] if n==1 else list(a)
pyrender.texture.glGenTextures=gen_texture
render=pyrender.Scene.from_trimesh_scene(loaded,ambient_light=[.28,.28,.28],bg_color=[.09,.12,.16,1])
# Camera looks toward object center, standard -Z view in camera coordinates.
def look_at(eye,target):
 z=np.array(eye)-np.array(target);z=z/np.linalg.norm(z);up=np.array([0.,1.,0.]);x=np.cross(up,z);x=x/np.linalg.norm(x);y=np.cross(z,x);M=np.eye(4);M[:3,:3]=np.column_stack((x,y,z));M[:3,3]=eye;return M
for name,eye in [('ON',[0,1.2,-6.8]),('YAN',[3.6,2.7,-6.0])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,1.12,0]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,1.12,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
