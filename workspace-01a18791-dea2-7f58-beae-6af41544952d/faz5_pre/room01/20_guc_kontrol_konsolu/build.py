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
# Power control console shell, based on Desktop recording 1s and 10s.
# Controls and drawer handles are separate models to be approved individually.
# Coordinate: front -Z, worktop y about 1.5, back guard y 2.1.
box('Bottom_rear_structural_rail',(8.10,.28,.16),(0,.33,.73),'edge')
box('Underside_horizontal_support',(7.92,.32,.34),(0,.54,.44),'gray')
for side in [-1,1]:
 x=side*3.86
 bevel('Pedestal_side_'+str(side),.47,1.57,1.68,.025,(x,.795,.02),'gray')
 box('Side_endcap_'+str(side),(.075,1.40,1.60),(side*4.12,.81,.02),'ivory')
 box('End_inset_'+str(side),(.035,.91,.88),(side*4.17,.69,-.18),'edge')
 box('End_inner_panel_'+str(side),(.025,.79,.76),(side*4.20,.69,-.18),'gray')
 for y in [.28,1.38]:
  for z in [-.60,.60]:
   a=trimesh.creation.icosphere(subdivisions=1,radius=.035);a.apply_translation([side*4.22,y,z]);add('End_screw_%s_%s_%s'%(side,y,z),a,'silver')
# Under the desk there is a visible open knee space; the back rail is not a solid front.
box('Worktop_main_slab',(8.23,.18,1.68),(0,1.60,.02),'gray')
box('Worktop_top',(8.10,.055,1.59),(0,1.716,.02),'ivory')
box('Worktop_front_dark_edge',(8.16,.11,.09),(0,1.60,-.83),'edge')
# subtle worn safety stripe segments, matching the narrow warning line in footage
for i in range(35):
 x=-3.92+i*.23
 if i%2==0:box('Safety_stripe_%02d'%i,(.16,.025,.015),(x,1.665,-.887),'yellow')
# Raised back shield is one continuous blank panel; instruments added later.
box('Console_rear_guard',(8.10,.64,.13),(0,2.04,.73),'gray')
box('Console_rear_guard_cap',(8.19,.075,.20),(0,2.39,.74),'edge')
for x in [-2.4,2.4]:
 bevel('Rear_guard_slot_'+str(x),.39,.18,.04,.015,(x,2.18,.64),'trim')
# Centre sloped nameplate integrated into console body; no invented display.
name=trimesh.creation.box(extents=(2.1,.35,.075));name.apply_transform(trimesh.transformations.rotation_matrix(-.24,[1,0,0]));name.apply_translation([0,2.51,.77]);add('Power_console_nameplate_blank',name,'gray')
# Unlike the main console, this unit has no visible drawer bank in reference.
# Unreadable upper nameplate is left blank rather than guessed.
box('Upper_front_apron',(7.20,.52,.15),(0,1.30,-.71),'gray')
# Two dark service vents on end support front, visible from room.
for side in [-1,1]:
 x=side*3.86
 bevel('Leg_service_bezel_'+str(side),.31,.80,.04,.015,(x,.72,-.845),'edge')
 bevel('Leg_service_recess_'+str(side),.25,.70,.025,.01,(x,.72,-.87),'trim')
out=P/'REAKTOR_GUC_KONSOLU_GOVDE_20_ADAY.glb';s.export(out);print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry));loaded=trimesh.load(out,force='scene');print('REOPEN',len(loaded.geometry),'bounds',loaded.bounds.tolist())
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
for name,eye in [('ON',[0,4.0,-13.5]),('YAN',[7.5,4.6,-11.5])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,1.25,0]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,1.2,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
