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
# 7x6 annunciator panel; labels read from Desktop 30.0s and 30.4s.
# A dash marks text not legible in reference, NOT a claimed canonical label.
import textwrap
bevel('Annunciator_outer_chassis',8.05,5.65,.30,.10,(0,2.825,0),'edge')
bevel('Annunciator_main_face',7.91,5.50,.14,.08,(0,2.825,-.23),'ivory')
texts=[
 ['Reaktör fanlarında hata oluştu','—','—','—','—','—','—'],
 ['Sistem yanıt vermiyor','—','—','Kapama Hatası','—','Öz Yıkım Aktif','—'],
 ['ENTS Hazır Durumda','Acil Soğutma Sıvısı','Tesis elektriği kararsız','Reaktör durması yakında','Reaktör gücü artıyor','—','—'],
 ['Anormal reaktör davranışı','Lazer Hasarı','Reaktör elektromanyetik','—','','',''],
 ['Lazer Isı Tahliye Sistemi','Aşırı yüksek basınç','Kalkan bütünlüğü azalıyor','Reaktör erimesi','ENTS Arızası','ENTS devreye girdi','—'],
 ['Hava alma fanı aktif','Egzoz fanı aktif','Soğutma akışı aktif','C. Pompa 1 Hatası','C. Pompa 2 Hatası','C. Pompa 3 Hatası','C. Pompa 4 Hatası']]
colors=[[(172,170,30),(172,170,30),(172,170,30),(26,91,147),(148,148,148),(148,148,148),(148,148,148)],[(124,76,154)]*7,[(171,84,23)]*7,[(171,84,23)]*7,[(160,35,31),(160,35,31),(160,35,31),(160,35,31),(176,143,29),(176,143,29),(160,35,31)],[(140,140,140),(140,140,140),(140,140,140),(160,35,31),(160,35,31),(160,35,31),(160,35,31)]]
# Face-on geometry, x order mirrored so visual left-to-right follows reference.
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
for row in range(6):
 for col in range(7):
  x=3.32-col*1.106;y=5.05-row*.885;key='%d_%d'%(row+1,col+1)
  bevel('Annunciator_%s_black_recess'%key,1.01,.79,.06,.025,(x,y,-.33),'trim')
  # Use an independent unique textured face, so later runtime integration can
  # map each indicator rather than silently baking them into one combined mesh.
  color=colors[row][col];w,h=512,352
  yy,xx=np.mgrid[0:h,0:w];g=np.clip(1.04-.38*(((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2),.65,1.04)
  image=np.empty((h,w,4),dtype=np.uint8)
  for channel in range(3):image[:,:,channel]=np.clip(color[channel]*g,0,255)
  image[:,:,3]=255;im=Image.fromarray(image,'RGBA');dr=ImageDraw.Draw(im)
  txt=texts[row][col];lines=textwrap.wrap(txt,width=11,break_long_words=False,break_on_hyphens=False) if txt else []
  size=63
  while size>20:
   font=ImageFont.truetype(fontpath,size)
   widths=[dr.textbbox((0,0),line,font=font)[2] for line in lines]
   if (not widths or max(widths)<w*.87) and len(lines)*size*1.12 <h*.80:break
   size-=2
  step=size*1.12;start=(h-len(lines)*step)/2
  for i,line in enumerate(lines):
   bb=dr.textbbox((0,0),line,font=font);dr.text(((w-bb[2])/2,start+i*step-bb[1]),line,font=font,fill=(12,9,10,255),stroke_width=0)
  mt=PBRMaterial(name='Alarm_indicator_material_'+key,baseColorTexture=im,metallicFactor=0,roughnessFactor=.6,emissiveTexture=im,emissiveFactor=[.10,.10,.10],doubleSided=True)
  a=.455;b=.34;z=-.375
  m=trimesh.Trimesh(vertices=[[x-a,y-b,z],[x+a,y-b,z],[x+a,y+b,z],[x-a,y+b,z]],faces=[[0,2,1],[0,3,2]],process=False)
  m.visual=TextureVisuals(uv=np.array([[1,0],[0,0],[0,1],[1,1]]),material=mt);s.add_geometry(m,node_name='ALARM_TILE_'+key,geom_name='ALARM_TILE_'+key)
for x in [-3.86,3.86]:
 for y in [.14,2.82,5.50]:cyl('Mount_screw_%s_%s'%(x,y),.045,.03,(x,y,-.32),'silver')
out=P/'DURUM_VE_UYARI_PANOSU_13_ADAY.glb';s.export(out);print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,2.8,-15.5]),('YAN',[6.0,4.6,-15.0])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,2.75,0]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,2.75,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
