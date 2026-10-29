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
 'red':material('DARK_RED_CAP',(165,26,30),.13,.24,[.09,.002,.002]),
 'purple':material('PURPLE_STATUS_LAMP',(157,47,141),.15,.4,[.12,.01,.09]),
 'gray':material('INSET_METAL',(112,119,118),.55,.6),
 'status':material('STATUS_LIGHT',(255,225,225),.0,.35,[.8,.35,.35]),
 'signal':material('SIGNAL_SYMBOL',(220,220,218),.0,.45,[.18,.18,.18]),
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
# Reactor startup guide panel. Reference says "Reaktör Başlatma Kılavuzu";
# precise gameplay behavior is not inferred from its icon.
def slab(n,w,d,h,c,pos,mat):
 pts=[(-w/2+c,-d/2),(w/2-c,-d/2),(w/2,-d/2+c),(w/2,d/2-c),(w/2-c,d/2),(-w/2+c,d/2),(-w/2,d/2-c),(-w/2,-d/2+c)]
 verts=[(x+pos[0],pos[1]+y,z+pos[2]) for y in [-h/2,h/2] for x,z in pts];f=[]
 for i in range(1,7):f.extend([(0,i,i+1),(8,8+i+1,8+i)])
 for i in range(8):j=(i+1)%8;f.extend([(i,8+j,j),(i,8+i,8+j)])
 add(n,trimesh.Trimesh(vertices=verts,faces=f,process=True),mat)
slab('Guide_panel_mount',1.55,2.05,.12,.05,(0,.06,0),'edge')
slab('Guide_red_frame',1.38,1.65,.07,.045,(0,.15,.15),'red')
slab('Guide_black_face',1.22,1.49,.045,.035,(0,.21,.15),'trim')
# Physical radio arcs, dot and red status bar. Individual dynamic light meshes.
def arc(name,r,rad,cx,cz):
 pts=[];faces=[];N=28
 for i in range(N+1):
  t=(np.pi/2)*i/N
  for rr in [r-rad,r+rad]:pts.append([cx-np.sin(t)*rr,.242,cz+np.cos(t)*rr])
 for i in range(N):a=i*2;faces.extend([(a,a+3,a+1),(a,a+2,a+3)])
 add(name,trimesh.Trimesh(vertices=pts,faces=faces,process=False),'silver')
arc('Guide_signal_outer',.62,.035,.36,-.12);arc('Guide_signal_inner',.39,.035,.36,-.12)
dot=trimesh.creation.cylinder(radius=.08,height=.025,sections=32);dot.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]));dot.apply_translation([.36,.25,-.12]);add('Guide_signal_dot',dot,'silver')
slab('Guide_status_slot_frame',.89,.18,.04,.02,(0,.25,-.48),'red')
slab('Guide_status_indicator',.78,.10,.03,.01,(0,.28,-.48),'status')
# Text on a separate flat legend, close to original, not a guessed feature.
slab('Guide_caption_plate',1.82,.48,.035,.015,(0,.045,-1.16),'edge')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Oblique.ttf',56);glyph=[]
for text,zpos in [('Reaktör Başlatma',-1.09),('Kılavuzu',-1.26)]:
 bb=font.getbbox(text);im=Image.new('L',(bb[2]+6,bb[3]-bb[1]+6),0);ImageDraw.Draw(im).text((3,-bb[1]+3),text,font=font,fill=255)
 mask=np.asarray(im)>110;rows,cols=mask.shape;px=min(1.60/cols,.11/rows)
 for iy in range(rows):
  start=None
  for ix in range(cols+1):
   yes=ix<cols and bool(mask[iy,ix])
   if yes and start is None:start=ix
   if not yes and start is not None:
    m=trimesh.creation.box(extents=[(ix-start)*px,.012,px]);m.apply_translation([(cols/2-(start+ix)/2)*px,.07,zpos+(rows/2-iy-.5)*px]);glyph.append(m);start=None
if glyph:add('Guide_reference_caption',trimesh.util.concatenate(glyph),'silver')
led=trimesh.creation.cylinder(radius=.09,height=.045,sections=32);led.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]));led.apply_translation([0,.075,-1.53]);add('Guide_red_status_led',led,'red')
out=P/'REAKTOR_BASLATMA_KILAVUZU_09_ADAY.glb';s.export(out);print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,3.7,-5.0]),('YAN',[3.0,2.7,-4.2])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,.12,0]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,.12,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
