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
 'blue':material('BLUE_STATUS_LAMP',(25,99,165),.15,.38,[.005,.05,.14]),
 'red':material('RED_STATUS_LAMP',(172,44,32),.15,.4,[.25,.02,.005]),
 'purple':material('PURPLE_STATUS_LAMP',(157,47,141),.15,.4,[.12,.01,.09]),
 'gray':material('INSET_METAL',(112,119,118),.55,.6),
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
# Panel modeled from the two-color unit immediately left of the central display.
# Front faces -Z, and each colored lens remains independently named for animation.
bevel('Rear_mount',2.65,2.40,.28,.055,(0,1.22,.0),'edge')
bevel('Front_enclosure',2.57,2.32,.15,.045,(0,1.22,-.21),'ivory')
box('Upper_status_plate',(2.35,.48,.07),(0,2.12,-.32),'gray')
for i,(x,color) in enumerate([(0.60,'red'),(-0.60,'blue')]):
 box('Indicator_%d_upper_inset'%i,(1.03,.36,.055),(x,2.12,-.37),'edge')
 bevel('Indicator_%d_upper_status'%i,.87,.24,.055,.02,(x,2.12,-.41),'ivory')
 box('Indicator_%d_square_frame'%i,(1.07,1.16,.09),(x,1.38,-.34),'edge')
 box('Indicator_%d_metal_base'%i,(.99,1.08,.07),(x,1.38,-.40),'gray')
 cyl('Indicator_%d_outer_rim'%i,.455,.11,(x,1.38,-.47),'trim')
 cyl('Indicator_%d_bezel'%i,.395,.10,(x,1.38,-.54),'silver')
 cyl('Indicator_%d_dark_gasket'%i,.35,.07,(x,1.38,-.60),'edge')
 cyl('Indicator_%d_%s_lens'% (i,color),.305,.07,(x,1.38,-.67),color)
 lens=trimesh.creation.icosphere(subdivisions=3,radius=1);lens.apply_scale([.30,.30,.065]);lens.apply_translation([x,1.38,-.70]);add('Indicator_%d_%s_glass'% (i,color),lens,color)
 for dx in [-.43,.43]:
  for dy in [-.45,.45]:cyl('Indicator_%d_screw_%s_%s'%(i,dx,dy),.032,.035,(x+dx,1.38+dy,-.445),'silver')
 box('Indicator_%d_wire_top'%i,(.045,.21,.04),(x,.71,-.34),'edge')
 cyl('Indicator_%d_terminal'%i,.12,.06,(x,.52,-.36),'trim')
 cyl('Indicator_%d_terminal_collar'%i,.075,.05,(x,.52,-.41),'edge')
 box('Indicator_%d_wire_bottom'%i,(.045,.34,.045),(x,.23,-.34),'edge')
for y in [.08,.13,.18]:box('Lower_seam_%s'%y,(2.25,.02,.03),(0,y,-.30),'gray')
for x in [-1.19,1.19]:
 for y in [.13,2.28]:cyl('Panel_mount_screw_%s_%s'%(x,y),.045,.04,(x,y,-.30),'silver')
out=P/'IKILI_KIRMIZI_MAVI_GOSTERGE_03_ADAY.glb';s.export(out)
print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,1.2,-6.5]),('YAN',[3.3,2.8,-6.5])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,1.20,-.2]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,1.2,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
