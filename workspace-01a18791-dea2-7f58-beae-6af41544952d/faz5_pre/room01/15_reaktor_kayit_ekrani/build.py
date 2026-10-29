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
# Reactor connection log display. Text sampled from the visible reference;
# example state texture is static until the later Roblox SurfaceGui integration.
bevel('Monitor_rear_mount',7.15,3.65,.30,.10,(0,1.83,0),'edge')
bevel('Monitor_light_metal_body',7.05,3.54,.14,.08,(0,1.83,-.22),'ivory')
bevel('Monitor_outer_bezel',6.89,3.40,.08,.10,(0,1.83,-.32),'gray')
bevel('Monitor_black_glass_rim',6.77,3.27,.06,.08,(0,1.83,-.39),'trim')
bevel('Monitor_recessed_glass',6.67,3.17,.04,.07,(0,1.83,-.44),'glass')
# Reference startup log state is shown only as an example; real logs are dynamic.
im=Image.new('RGBA',(1600,760),(8,11,12,255));d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf';small=ImageFont.truetype(font,31);caption=ImageFont.truetype(font,38)
for y in range(0,760,5):d.line((0,y,1600,y),fill=(10,13,14,255),width=1)
d.text((78,500),'Operatör girdisi bekleniyor...',font=small,fill=(140,150,143,255))
d.line((70,650,1530,650),fill=(42,51,48),width=2)
t='Reaktör Bağlantı Kayıtları';bb=d.textbbox((0,0),t,font=caption);d.text(((1600-bb[2])/2,681),t,font=caption,fill=(138,148,141,255))
im.save(P/'baglanti_kayit_ornek.png');mt=PBRMaterial(name='LOG_DISPLAY_PLACEHOLDER',baseColorTexture=im,metallicFactor=0,roughnessFactor=.65,emissiveTexture=im,emissiveFactor=[.2,.2,.2],doubleSided=True)
mesh=trimesh.Trimesh(vertices=[[-3.27,.29,-.463],[3.27,.29,-.463],[3.27,3.35,-.463],[-3.27,3.35,-.463]],faces=[[0,2,1],[0,3,2]],process=False);mesh.visual=TextureVisuals(uv=np.array([[1,0],[0,0],[0,1],[1,1]]),material=mt);s.add_geometry(mesh,node_name='DYNAMIC_LOG_DISPLAY',geom_name='DYNAMIC_LOG_DISPLAY')
out=P/'REAKTOR_BAGLANTI_KAYIT_EKRANI_15_ADAY.glb';s.export(out);print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,1.9,-12.0]),('YAN',[5.8,3.6,-11.0])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,1.8,0]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,1.35,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
