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
# Card geometry based on 31.2s, placed horizontally for inspection only.
# It is a visual GLB candidate; no change to any existing inventory or permission logic.
verts=[[-1.65,.05,-.04],[1.18,.05,-.04],[1.18,.27,-.04],[1.65,.27,-.04],[1.65,2.05,-.04],[-1.65,2.05,-.04]]
# Closed six-sided notched prism; independent of third-party geometry libraries.
outline=[(-1.65,.05),(1.18,.05),(1.18,.27),(1.65,.27),(1.65,2.05),(-1.65,2.05)]
v=[(x,y,z) for z in [-.04,.04] for x,y in outline];tri=[(0,2,1),(0,5,2),(5,4,2),(2,4,3)];faces=tri+[(a+6,c+6,b+6) for a,b,c in tri]
for i in range(6):j=(i+1)%6;faces.extend([(i,j,j+6),(i,j+6,i+6)])
body=trimesh.Trimesh(vertices=v,faces=faces,process=True);body.fix_normals();add('Card_plastic_body',body,'ivory')
# Card face: readable text visible in the source; no invented serial or permissions.
im=Image.new('RGBA',(1650,1000),(174,176,175,255));d=ImageDraw.Draw(im)
d.rectangle((0,0,1650,108),fill=(170,32,33,255));d.rectangle((0,108,1650,118),fill=(118,29,31,255))
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def center(text,y,size,color,fontpath=font):
 f=ImageFont.truetype(fontpath,size);bb=d.textbbox((0,0),text,font=f);d.text(((1650-bb[2])/2,y),text,font=f,fill=color)
center('Reaktör Operatörü',175,110,(20,20,21),font)
center('Seviye 2',380,130,(112,35,38),font)
center('RO Departmanı',560,84,(25,25,25),font)
center('Bu kartı kimseyle paylaşmayın',800,59,(112,35,38),font)
im.save(P/'operator_karti_on.png');mt=PBRMaterial(name='OPERATOR_CARD_FACE',baseColorTexture=im,metallicFactor=0,roughnessFactor=.75,doubleSided=True)
# Explicit polygon + UV preserves the notch in the printed surface.
pts=[[-1.65,.05,-.045],[1.18,.05,-.045],[1.18,.27,-.045],[1.65,.27,-.045],[1.65,2.05,-.045],[-1.65,2.05,-.045]]
uv=np.array([[1,0],[.1424,0],[.1424,.11],[0,.11],[0,1],[1,1]])
m=trimesh.Trimesh(vertices=pts,faces=[[0,2,1],[0,5,2],[5,4,2],[2,4,3]],process=False);m.visual=TextureVisuals(uv=uv,material=mt);s.add_geometry(m,node_name='Operator_card_print',geom_name='Operator_card_print')
out=P/'REAKTOR_OPERATORU_KARTI_16_ADAY.glb';s.export(out);print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,1.1,-6.5]),('YAN',[3.5,2.6,-5.3])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,1.05,0]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,1.05,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
