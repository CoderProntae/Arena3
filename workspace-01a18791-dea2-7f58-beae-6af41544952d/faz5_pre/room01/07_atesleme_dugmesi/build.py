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
# 3D standalone main ignition pushbutton; button cap is separate geometry.
# The associated legend plate is separate from the dark mounting frame.
def flat_bevel(name,w,depth,height,cut,pos,mat):
 # eight clipped corners in X/Z; layers rise along Y
 pts=[(-w/2+cut,-depth/2),(w/2-cut,-depth/2),(w/2,-depth/2+cut),(w/2,depth/2-cut),(w/2-cut,depth/2),(-w/2+cut,depth/2),(-w/2,depth/2-cut),(-w/2,-depth/2+cut)]
 verts=[(x+pos[0],pos[1]+y,z+pos[2]) for y in [-height/2,height/2] for x,z in pts];faces=[]
 for i in range(1,7):faces.extend([(0,i,i+1),(8,8+i+1,8+i)])
 for i in range(8):j=(i+1)%8;faces.extend([(i,8+j,j),(i,8+i,8+j)])
 add(name,trimesh.Trimesh(vertices=verts,faces=faces,process=True),mat)
flat_bevel('Outer_metal_mount',3.12,2.12,.10,.13,(0,.05,0),'edge')
flat_bevel('Lower_black_collared_frame',2.98,1.98,.08,.11,(0,.14,0),'trim')
flat_bevel('Raised_housing_rim',2.85,1.84,.12,.12,(0,.24,0),'gray')
flat_bevel('Inner_black_gasket',2.71,1.70,.09,.11,(0,.33,0),'trim')
flat_bevel('Red_button_border',2.55,1.54,.08,.10,(0,.405,0),'red')
# Three perimeter rings form beveled sides and a gently sloped top.
def cap_ring(w,d,c,y):
 pts=[(-w/2+c,-d/2),(w/2-c,-d/2),(w/2,-d/2+c),(w/2,d/2-c),(w/2-c,d/2),(-w/2+c,d/2),(-w/2,d/2-c),(-w/2,-d/2+c)]
 return [(x,y,z) for x,z in pts]
verts=cap_ring(2.46,1.45,.12,.44)+cap_ring(2.46,1.45,.12,.61)+cap_ring(2.27,1.26,.16,.71)
faces=[]
for ring in range(2):
 for i in range(8):
  j=(i+1)%8;a=ring*8+i;b=ring*8+j;c=(ring+1)*8+j;d=(ring+1)*8+i
  faces.extend([(a,c,b),(a,d,c)])
for i in range(1,7):faces.append((16,16+i+1,16+i))
cap=trimesh.Trimesh(vertices=verts,faces=faces,process=True);cap.fix_normals();add('MOVING_IGNITION_RED_CAP',cap,'red')
for x in [-1.33,1.33]:
 for z in [-.81,.81]:
  a=trimesh.creation.cylinder(radius=.043,height=.025,sections=24);a.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]));a.apply_translation([x,.39,z]);add('Mount_screw_%s_%s'%(x,z),a,'silver')
# Control surface label, typography and a black circular indicator drawn from reference.
flat_bevel('Legend_plate',2.96,.52,.035,.025,(0,.04,-1.40),'edge')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Oblique.ttf',56)
text='Ana Reaktör Ateşleme';bb=font.getbbox(text);im=Image.new('L',(bb[2]+6,bb[3]-bb[1]+6),0);ImageDraw.Draw(im).text((3,-bb[1]+3),text,font=font,fill=255)
mask=np.asarray(im)>110;rows,cols=mask.shape;px=2.60/cols;glyph=[]
for iy in range(rows):
 start=None
 for ix in range(cols+1):
  yes=ix<cols and bool(mask[iy,ix])
  if yes and start is None:start=ix
  if not yes and start is not None:
   m=trimesh.creation.box(extents=[(ix-start)*px,.012,px]);m.apply_translation([(cols/2-(start+ix)/2)*px,.064,-1.40+(rows/2-iy-.5)*px]);glyph.append(m);start=None
if glyph:add('Reference_ignition_legend',trimesh.util.concatenate(glyph),'silver')
out=P/'ANA_REAKTOR_ATESLEME_DUGMESI_07_ADAY.glb';s.export(out);print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,5.0,-6.7]),('YAN',[4.1,3.2,-5.9])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,.12,0]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,.12,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
