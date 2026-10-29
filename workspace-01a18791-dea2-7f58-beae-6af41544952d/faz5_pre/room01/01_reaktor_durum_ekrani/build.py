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
 'red':material('RED_STATUS_LAMP',(172,44,32),.15,.4,[.25,.02,.005]),
 'purple':material('PURPLE_STATUS_LAMP',(157,47,141),.15,.4,[.12,.01,.09]),
 'gray':material('INSET_METAL',(112,119,118),.55,.6),
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
# model approximates the central upper screen visible in 01_komut_110.jpg
# metres are model units, local front faces -Z; separate meshes preserve materials.
bevel('Outer_backplate',8.80,3.75,.42,.18,(0,1.875,.02),'edge')
bevel('Painted_instrument_body',8.65,3.62,.28,.13,(0,1.875,-.24),'ivory')
bevel('Display_outer_lip',7.98,2.66,.14,.27,(0,2.20,-.43),'gray')
bevel('Display_black_bezel',7.78,2.48,.14,.25,(0,2.20,-.52),'trim')
bevel('Recessed_display_glass',7.55,2.25,.06,.22,(0,2.20,-.61),'glass')
for side in (-1,1):
 for y in (.30,1.85,3.46):
  cyl('Housing_screw_%s_%s'%(side,y),.065,.055,(side*4.12,y,-.425),'silver')
  box('Screw_slot_%s_%s'%(side,y),(.07,.012,.013),(side*4.12,y,-.459),'edge')
# horizontal grooves just above status legend
for i in range(3):box('Lower_service_channel_%d'%i,(7.8,.025,.035),(0,.64+i*.055,-.405),'gray')
# Four real modeled indicators below the screen, with individually colored lenses.
bevel('Operating_mode_frame',2.00,.29,.09,.03,(0,.37,-.43),'edge')
for i,k in enumerate(['purple','red','yellow','green']):
 x=-.735+i*.49
 bevel('Indicator_%d_border'%i,.45,.24,.07,.025,(x,.37,-.49),'silver')
 bevel('Indicator_%d_lens'%i,.37,.17,.04,.015,(x,.37,-.55),k)
# display texture - readable independent material, authored as image in GLB
im=Image.new('RGBA',(1600,490),(10,17,18,255));d=ImageDraw.Draw(im)
f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';fb='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(f,54);small=ImageFont.truetype(f,34);tiny=ImageFont.truetype(f,29);bold=ImageFont.truetype(fb,36)
def centered(y,text,font,fill):
 x=(1600-d.textbbox((0,0),text,font=font)[2])/2;d.text((x,y),text,font=font,fill=fill)
centered(30,'26 °C',font,(207,217,211));centered(94,'(Unknown)',small,(144,157,149));centered(148,'Ateşleme Bekleniyor',font,(218,224,218))
d.rounded_rectangle((196,253,1404,300),radius=12,fill=(34,51,38),outline=(118,154,119),width=3);d.rounded_rectangle((205,261,1393,290),radius=9,fill=(122,213,110));centered(258,'Reaktör Kalkanı (100.0%)',bold,(23,48,27))
for i in range(60):
 if i%2==0:d.rectangle((270+i*18,330,278+i*18,332),fill=(133,142,136))
centered(366,'Reaktör Teşhisleri',tiny,(134,145,139))
im.save(P/'ekran_dokusu.png')
texmat=PBRMaterial(name='WORLD_DISPLAY_TEXTURE',baseColorTexture=im,metallicFactor=0,roughnessFactor=.8,emissiveTexture=im,emissiveFactor=[.12,.12,.12],doubleSided=True)
# Texture plane, faces toward -Z and preserve full image.
verts=np.array([[-3.68,1.115,-.654],[3.68,1.115,-.654],[3.68,3.285,-.654],[-3.68,3.285,-.654]])
mesh=trimesh.Trimesh(vertices=verts,faces=[[0,2,1],[0,3,2]],process=False)
mesh.visual=TextureVisuals(uv=np.array([[1,0],[0,0],[0,1],[1,1]]),material=texmat);s.add_geometry(mesh,node_name='Display_textured_face',geom_name='Display_textured_face')
out=P/'REAKTOR_DURUM_EKRANI_01_ADAY.glb';s.export(out)
print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry))
# Validate GLB is independently readable
loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,2,-12.8]),('YAN',[7.2,4.1,-12.5])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,1.85,-.2]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,1.8,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
