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
# The locally upright plate is tilted as a whole to sit on the console.
# Red head is independently named so it can later be made pressable.
bevel('Mute_pedestal_housing',2.45,2.20,.34,.08,(0,1.10,.06),'edge')
bevel('Mute_pedestal_top_cover',2.31,2.08,.10,.06,(0,1.10,-.16),'gray')
bevel('Mute_instrument_recess',1.94,1.30,.075,.055,(0,.88,-.24),'trim')
bevel('Mute_instrument_plate',1.80,1.18,.07,.045,(0,.88,-.30),'gray')
for side in [-1,1]:
 x=side*.75
 box('Hazard_stripe_black_'+str(side),(.13,.91,.025),(x,.88,-.35),'trim')
 for i,y in enumerate([.53,.88,1.23]):
  if i!=1:box('Hazard_yellow_%s_%d'%(side,i),(.13,.28,.025),(x,y,-.37),'yellow')
for y in [.43,.49,1.27,1.33]:box('Vent_slot_'+str(y),(1.0,.04,.025),(0,y,-.35),'edge')
cyl('Button_recess',.39,.10,(0,.89,-.35),'trim')
cyl('Button_outer_bezel',.33,.10,(0,.89,-.42),'edge')
cyl('MOVING_MUTE_BUTTON_RED',.29,.20,(0,.89,-.53),'red')
top=trimesh.creation.icosphere(subdivisions=3,radius=1);top.apply_scale([.285,.285,.08]);top.apply_translation([0,.89,-.64]);add('Button_red_curved_face',top,'red')
for x in [-1.04,1.04]:
 for y in [.13,2.06]:cyl('Housing_fastener_%s_%s'%(x,y),.045,.035,(x,y,-.23),'silver')
# Two-line label present in the 00-second reference, embedded as geometry.
font=ImageFont.truetype('/home/user/faz5_pre/fonts/Teko.ttf',76);glyph=[]
for text,yc,wmax in [('Alarm Seslerini',1.96,1.60),('Kapat',1.72,.72)]:
 bb=font.getbbox(text);img=Image.new('L',(bb[2]+6,bb[3]-bb[1]+6),0);ImageDraw.Draw(img).text((3,-bb[1]+3),text,font=font,fill=255);mask=np.asarray(img)>110;rows,cols=mask.shape;px=min(wmax/cols,.19/rows)
 for iy in range(rows):
  st=None
  for ix in range(cols+1):
   hit=ix<cols and bool(mask[iy,ix])
   if hit and st is None:st=ix
   if not hit and st is not None:
    m=trimesh.creation.box(extents=[(ix-st)*px,px,.010]);m.apply_translation([(cols/2-(st+ix)/2)*px,yc+(rows/2-iy-.5)*px,-.217]);glyph.append(m);st=None
if glyph:add('Mute_caption_lettering',trimesh.util.concatenate(glyph),'trim')
# Transform all parts together, leaving moving head as distinct mesh.
rotate=trimesh.transformations.rotation_matrix(np.deg2rad(48),[1,0,0]);rotate[:3,3]=[0,.18,-.34]
for g in s.geometry.values():g.apply_transform(rotate)
# triangular support cheeks behind tilted face, represented as closed extruded shapes
# behind the panel, dark material as shown by the reference silhouette.
def cheek(name,x):
 p=[(0,0),(1.35,0),(.93,1.47)];t=.11;v=[(x+dx,y,z) for dx in [-t/2,t/2] for z,y in p];faces=[(0,2,1),(3,4,5),(0,1,4),(0,4,3),(1,2,5),(1,5,4),(2,0,3),(2,3,5)];add(name,trimesh.Trimesh(vertices=v,faces=faces,process=True),'trim')
for x in [-1.08,1.08]:cheek('Side_support_'+str(x),x)
out=P/'ALARM_SESLERINI_KAPAT_11_ADAY.glb';s.export(out);print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,3.5,-6.2]),('YAN',[3.3,3.2,-5.2])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,1.1,0]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,1.1,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
