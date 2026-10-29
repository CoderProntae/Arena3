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
 'wineglass':material('DARK_RED_DISPLAY_GLASS',(48,8,12),.14,.30,[.025,.001,.002]),
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
# Desktop video control-status panel, right of startup guide.
# Text behind mouse tooltip cannot be read; display is intentionally generic.
def slab(n,w,d,h,c,pos,mat):
 pts=[(-w/2+c,-d/2),(w/2-c,-d/2),(w/2,-d/2+c),(w/2,d/2-c),(w/2-c,d/2),(-w/2+c,d/2),(-w/2,d/2-c),(-w/2,-d/2+c)]
 v=[(x+pos[0],pos[1]+y,z+pos[2]) for y in [-h/2,h/2] for x,z in pts];f=[]
 for i in range(1,7):f.extend([(0,i,i+1),(8,8+i+1,8+i)])
 for i in range(8):j=(i+1)%8;f.extend([(i,8+j,j),(i,8+i,8+j)])
 add(n,trimesh.Trimesh(vertices=v,faces=f,process=True),mat)
# Slim inset display with one frame and a near-flush, dark glass surface.
slab('Outer_chassis',3.65,1.89,.06,.10,(0,.03,0),'edge')
slab('Screen_thin_frame',3.52,1.77,.025,.10,(0,.073,0),'trim')
slab('Screen_inset_glass',3.32,1.58,.012,.09,(0,.092,0),'wineglass')
# An actual textured display surface, not painted/red button geometry.
# The example text is illustrative because the source image is partly obscured.
w,h=1600,760
Y,X=np.mgrid[0:h,0:w]; glow=np.exp(-(((X-w*.49)/(w*.40))**2+((Y-h*.46)/(h*.50))**2)*2.0)
rng=np.random.default_rng(281);noise=rng.normal(0,.8,(h,w))
arr=np.zeros((h,w,4),dtype=np.uint8)
arr[:,:,0]=np.clip(13+17*glow+noise,0,255);arr[:,:,1]=np.clip(3+3*glow+noise*.2,0,255);arr[:,:,2]=np.clip(5+5*glow+noise*.2,0,255);arr[:,:,3]=255
img=Image.fromarray(arr,'RGBA');d=ImageDraw.Draw(img)
font='/home/user/faz5_pre/fonts/Teko.ttf';big=ImageFont.truetype(font,114);small=ImageFont.truetype(font,55)
def center(t,y,f,color):
 bb=d.textbbox((0,0),t,font=f);d.text(((w-(bb[2]-bb[0]))/2,y-bb[1]),t,font=f,fill=color)
center('Kontrol durumu bekleniyor',250,big,(211,172,174,255))
center('REAKTÖR SİSTEMİ',380,small,(158,105,108,255))
for y in range(2,h,4):d.line((0,y,w,y),fill=(21,5,8,255),width=1)
img.save(P/'ekran_ornek_durum.png')
mt=PBRMaterial(name='STATUS_SCREEN_EXAMPLE_REPLACE_AT_RUNTIME',baseColorTexture=img,metallicFactor=0,roughnessFactor=.23,emissiveTexture=img,emissiveFactor=[.4,.4,.4],doubleSided=True)
vertices=[[-1.59,.103,-.72],[1.59,.103,-.72],[1.59,.103,.72],[-1.59,.103,.72]]
m=trimesh.Trimesh(vertices=vertices,faces=[[0,1,2],[0,2,3]],process=False)
m.visual=TextureVisuals(uv=np.array([[1,0],[0,0],[0,1],[1,1]]),material=mt);s.add_geometry(m,node_name='DYNAMIC_SCREEN_TEXTURE_FACE',geom_name='DYNAMIC_SCREEN_TEXTURE_FACE')
# Desk caption matches the readable video text.
slab('Caption_plate',2.85,.46,.035,.02,(0,.04,-1.19),'edge')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Oblique.ttf',56);glyph=[]
for text,zpos in [('Reaktör Kontrol',-1.12),('Durumu',-1.27)]:
 bb=font.getbbox(text);im=Image.new('L',(bb[2]+6,bb[3]-bb[1]+6),0);ImageDraw.Draw(im).text((3,-bb[1]+3),text,font=font,fill=255)
 mask=np.asarray(im)>110;rows,cols=mask.shape;px=min(2.2/cols,.10/rows)
 for iy in range(rows):
  start=None
  for ix in range(cols+1):
   yes=ix<cols and bool(mask[iy,ix])
   if yes and start is None:start=ix
   if not yes and start is not None:
    m=trimesh.creation.box(extents=[(ix-start)*px,.012,px]);m.apply_translation([(cols/2-(start+ix)/2)*px,.064,zpos+(rows/2-iy-.5)*px]);glyph.append(m);start=None
if glyph:add('Control_status_reference_caption',trimesh.util.concatenate(glyph),'silver')
for x in [-1.64,1.64]:
 for z in [-.75,.75]:
  a=trimesh.creation.cylinder(radius=.035,height=.024,sections=24);a.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]));a.apply_translation([x,.09,z]);add('Mount_fastener_%s_%s'%(x,z),a,'silver')
out=P/'REAKTOR_KONTROL_DURUMU_10_REV3.glb';s.export(out);print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,4.2,-5.6]),('YAN',[3.5,3.0,-5.3])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,.12,0]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,.12,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
