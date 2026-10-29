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
# The face, handle and keyhole for the "Anahtar Depolama" console drawer.
# This is a standalone 3D model, not yet attached to the approved console.
bevel('Drawer_frame',3.8,1.52,.22,.05,(0,.81,0),'trim')
bevel('DRAWER_MOVING_FRONT',3.62,1.35,.10,.045,(0,.81,-.15),'gray')
bevel('Drawer_inner_recess',3.44,1.20,.04,.035,(0,.81,-.22),'ivory')
# Small dark sign with white lettering, directly printed on metal.
box('Drawer_label_dark', (2.20,.30,.02),(.13,1.21,-.25),'gray')
im=Image.new('RGBA',(900,140),(112,119,118,255));d=ImageDraw.Draw(im);ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',85);t='Anahtar Depolama';bb=d.textbbox((0,0),t,font=ft);d.text(((900-bb[2])/2,(140-bb[3]+bb[1])/2-bb[1]),t,font=ft,fill=(229,230,228,255))
im.save(P/'anahtar_depolama_etiket.png');mt=PBRMaterial(name='DRAWER_LABEL',baseColorTexture=im,metallicFactor=0,roughnessFactor=.8,doubleSided=True)
x=.13;y=1.21;z=-.265;a=1.10;b=.15
mesh=trimesh.Trimesh(vertices=[[x-a,y-b,z],[x+a,y-b,z],[x+a,y+b,z],[x-a,y+b,z]],faces=[[0,2,1],[0,3,2]],process=False);mesh.visual=TextureVisuals(uv=np.array([[1,0],[0,0],[0,1],[1,1]]),material=mt);s.add_geometry(mesh,node_name='Drawer_label_text',geom_name='Drawer_label_text')
# Drawer pull: two stand-offs, rounded grip and metal bases.
for x in [-.64,.64]:
 cyl('Handle_mount_'+str(x),.09,.045,(x,.58,-.27),'edge')
 cyl('Handle_standoff_'+str(x),.05,.18,(x,.58,-.38),'silver')
# horizontal bar; cylinder axis rotated from Z to X
rod=trimesh.creation.cylinder(radius=.065,height=1.28,sections=24);rod.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0]));rod.apply_translation([0,.58,-.48]);add('DRAWER_HANDLE',rod,'silver')
for x in [-.64,.64]:
 cap=trimesh.creation.icosphere(subdivisions=2,radius=.064);cap.apply_translation([x,.58,-.48]);add('Handle_end_'+str(x),cap,'silver')
cyl('Lock_outer',.12,.035,(-1.25,.65,-.27),'edge');cyl('Lock_face',.09,.05,(-1.25,.65,-.30),'silver');box('Lock_key_slot',(.025,.105,.015),(-1.25,.65,-.335),'trim')
# Fine horizontal grooves on bottom frame in the reference.
for y in [.18,.23,.28]:box('Lower_drawer_trim_'+str(y),(3.26,.018,.018),(0,y,-.25),'gray')
out=P/'ANAHTAR_DEPOLAMA_CEKMECESI_18_ADAY.glb';s.export(out);print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,1.0,-7.0]),('YAN',[4.1,2.5,-6.0])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,.85,0]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,.85,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
