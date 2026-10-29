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
# Structural housing only: separate controls/screens are future individual assets.
# A closed extruded wedge with side armour, sloped deck, and upper instrument frame.
def side_extrude(name,points,width,mat):
 verts=[(x,y,z) for x in [-width/2,width/2] for z,y in points];n=len(points);faces=[]
 for i in range(1,n-1):faces.extend([(0,i+1,i),(n,n+i,n+i+1)])
 for i in range(n):j=(i+1)%n;faces.extend([(i,j,n+j),(i,n+j,n+i)])
 add(name,trimesh.Trimesh(vertices=verts,faces=faces,process=True),mat)
profile=[(-1.2,0),(1.10,0),(1.10,1.73),(.50,1.73),(-.83,1.02),(-1.20,.90)]
side_extrude('Console_structural_hull',profile,6.2,'edge')
box('Continuous_lower_foundation',(6.32,.18,2.4),(0,.09,-.05),'trim')
# sloping instrument deck follows the hull pitch
angle=-np.arctan2(.71,1.33)
def deckbox(name,dims,pos,mat):
 m=trimesh.creation.box(extents=dims);m.apply_transform(trimesh.transformations.rotation_matrix(angle,[1,0,0]));m.apply_translation(pos);add(name,m,mat)
deckbox('Raised_console_deck',(5.75,.095,1.43),(0,1.39,-.16),'gray')
deckbox('Dark_deck_inset',(5.30,.035,1.27),(0,1.445,-.14),'trim')
# Four unlabelled mounting recesses: no buttons or controls included in this component.
for i,x in enumerate([-1.95,-.65,.65,1.95]):
 deckbox('Control_mounting_bay_%d'%i,(1.14,.025,1.07),(x,1.47,-.13),'edge')
 for dx in [-.48,.48]:
  for dz in [-.45,.45]:
   screw=trimesh.creation.cylinder(radius=.034,height=.025,sections=24)
   screw.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2+angle,[1,0,0]))
   screw.apply_translation([x+dx,1.49+dz*.47,-.13+dz*.88]);add('Deck_screw_%s_%s_%s'%(i,dx,dz),screw,'silver')
# Stepped upright housing / shared mount for future screen inserts.
bevel('Instrument_hood_back',5.92,.77,.23,.10,(0,2.08,.81),'edge')
bevel('Instrument_hood_inner',5.68,.58,.06,.07,(0,2.08,.66),'trim')
for x in [-1.87,0,1.87]:
 bevel('Instrument_recess_'+str(x),1.70,.44,.04,.04,(x,2.08,.615),'glass')
# Exterior plates and kick rail.
for side in [-1,1]:
 box('Side_armour_'+str(side),(.12,1.50,1.75),(side*3.12,.85,-.03),'gray')
 box('Side_lower_rubrail_'+str(side),(.14,.16,1.82),(side*3.16,.20,-.03),'trim')
 for z in [-.68,.64]:
  for y in [.36,1.35]:
   t=trimesh.creation.icosphere(subdivisions=1,radius=.04);t.apply_translation([side*3.20,y,z]);add('Side_fastener_%s_%s_%s'%(side,z,y),t,'silver')
box('Front_service_kickplate',(5.65,.53,.055),(0,.42,-1.225),'gray')
for x in [-2.0,0,2.0]:
 box('Front_service_inset_'+str(x),(1.65,.36,.035),(x,.42,-1.265),'edge')
 for j in range(4):box('Front_vent_%s_%s'%(x,j),(1.34,.022,.025),(x,.30+j*.075,-1.29),'gray')
out=P/'KONTROL_KONSOLU_GOVDE_06_ADAY.glb';s.export(out);print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,4.5,-10.5]),('YAN',[6.0,4.0,-9.2])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,1.20,0]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,1.2,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
