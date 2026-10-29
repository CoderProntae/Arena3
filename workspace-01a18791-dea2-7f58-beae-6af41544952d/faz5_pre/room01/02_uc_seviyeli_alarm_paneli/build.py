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
# Reference: three round yellow, amber and red lamps beneath a red header.
# Named separate meshes so importer can map each lens to live game state.
bevel('Alarm_panel_rear_bracket',4.20,3.25,.30,.08,(0,1.65,.03),'edge')
bevel('Alarm_panel_front_plate',4.09,3.14,.17,.07,(0,1.65,-.20),'ivory')
bevel('Upper_alarm_header_bezel',3.72,.50,.09,.05,(0,2.91,-.32),'trim')
bevel('Upper_alarm_header_lens',3.55,.33,.06,.035,(0,2.91,-.39),'red')
box('Label_rail',(3.7,.34,.055),(0,2.19,-.32),'gray')
for j,x in enumerate([-1.24,0,1.24]):
 box('Label_cell_%d'%j,(1.12,.30,.035),(x,2.19,-.37),'ivory')

# Three individually isolated, multi-layer round lamp units. Camera views -Z.
for i,(x,key) in enumerate([(1.24,'yellow'),(0,'amber'),(-1.24,'red')]):
 box('Lamp_%d_engraved_mount'%i,(1.12,1.31,.10),(x,1.40,-.33),'edge')
 box('Lamp_%d_plate'%i,(1.01,1.19,.075),(x,1.40,-.40),'gray')
 cyl('Lamp_%d_rear_collar'%i,.49,.14,(x,1.39,-.48),'trim')
 cyl('Lamp_%d_metal_ring'%i,.42,.11,(x,1.39,-.56),'silver')
 cyl('Lamp_%d_shadow_gasket'%i,.36,.08,(x,1.39,-.63),'edge')
 cyl('Lamp_%d_%s_lens_base'%(i,key),.32,.085,(x,1.39,-.70),key)
 dome=trimesh.creation.icosphere(subdivisions=3,radius=1);dome.apply_scale([.315,.315,.085]);dome.apply_translation([x,1.39,-.735]);add('Lamp_%d_%s_lens_dome'%(i,key),dome,key)
 cyl('Lamp_%d_rim_upper'%i,.375,.035,(x,1.39,-.67),'edge')
 cyl('Lamp_%d_exposed_light'%i,.31,.045,(x,1.39,-.695),key)
 
 # Rim fasteners physically separate geometry.
 for dx in [-.43,.43]:
  for dy in [-.53,.53]:cyl('Lamp_%d_screw_%s_%s'%(i,dx,dy),.032,.035,(x+dx,1.40+dy,-.45),'silver')
 # Connection terminals are static, below panel like the video.
 cyl('Lamp_%d_terminal'%i,.13,.075,(x,.53,-.40),'trim')
 box('Lamp_%d_cable'%i,(.05,.43,.06),(x,.25,-.33),'edge')
for x in [-1.94,1.94]:
 for y in [.12,3.16]:cyl('Mount_fastener_%s_%s'%(x,y),.045,.04,(x,y,-.32),'silver')
# Reference wording is visible in the clearer 02_buhar_120 frame.
# Small textured front plates leave all lamp lenses as separate 3D meshes.
def text_plane(name,words,w,h,x,y,z,color):
 # Make texture dimensions match the physical aspect ratio, so letters do not stretch.
 width=1200;height=max(80,round(width*h/w))
 img=Image.new('RGBA',(width,height),(171,175,170,255));dr=ImageDraw.Draw(img)
 path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
 size=int(height*.85)
 while size>8:
  font=ImageFont.truetype(path,size);bb=dr.textbbox((0,0),words,font=font)
  if bb[2]-bb[0]<=width*.89 and bb[3]-bb[1]<=height*.78:break
  size-=2
 bb=dr.textbbox((0,0),words,font=font)
 dr.text(((width-(bb[2]-bb[0]))/2-bb[0],(height-(bb[3]-bb[1]))/2-bb[1]),words,font=font,fill=(*color,255))

 mt=PBRMaterial(name=name+'_ink',baseColorTexture=img,alphaMode='OPAQUE',metallicFactor=0,roughnessFactor=.85,doubleSided=True)
 vertices=[[x-w/2,y-h/2,z],[x+w/2,y-h/2,z],[x+w/2,y+h/2,z],[x-w/2,y+h/2,z]]
 m=trimesh.Trimesh(vertices=vertices,faces=[[0,2,1],[0,3,2]],process=False)
 m.visual=TextureVisuals(uv=np.array([[1,0],[0,0],[0,1],[1,1]]),material=mt);s.add_geometry(m,node_name=name,geom_name=name)
# Physical raised lettering with thin, non-bold monospaced glyphs on the panel.
# No opaque rectangular texture patch behind the text.
def raised_legend(text):
    font=ImageFont.truetype('/home/user/faz5_pre/fonts/Teko.ttf',80)
    measure=font.getbbox(text); img=Image.new('L',(measure[2]+4,measure[3]-measure[1]+4),0)
    ImageDraw.Draw(img).text((2,-measure[1]+2),text,font=font,fill=255)
    # Aged factory stencil: mildly irregular printed outline, chipped paint and
    # short scratches. Work on the actual letters, not the surrounding plaque.
    import cv2
    arr=np.asarray(img).copy(); hh,ww=arr.shape
    yy,xx=np.mgrid[0:hh,0:ww].astype(np.float32)
    mapx=xx+0.85*np.sin(yy*.32+xx*.057)+.35*np.sin(xx*.18)
    mapy=yy+0.65*np.sin(xx*.105)+.35*np.cos(yy*.21)
    arr=cv2.remap(arr,mapx,mapy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
    mask=arr>100
    rng=np.random.default_rng(153); ys,xs=np.where(mask)
    for _ in range(65):
        k=int(rng.integers(0,len(xs)));x=int(xs[k]);y=int(ys[k])
        rx=int(rng.integers(1,4));ry=int(rng.integers(1,3))
        cv2.ellipse(mask.view(np.uint8),(x,y),(rx,ry),float(rng.integers(-30,31)),0,360,0,-1)
    # Small random gaps at edges produce uneven old ink rather than modern type.
    for _ in range(12):
        k=int(rng.integers(0,len(xs)));x=int(xs[k]);y=int(ys[k]);length=int(rng.integers(3,10))
        cv2.line(mask.view(np.uint8),(x,y),(min(ww-1,x+length),max(0,y-int(rng.integers(0,3)))),0,1)
    rows,cols=mask.shape
    max_width=1.75; pixel=max_width/cols
    center_y=2.52; meshes=[]
    for y in range(rows):
        line=mask[y]; start=None
        for x in range(cols+1):
            hit=x<cols and bool(line[x])
            if hit and start is None:start=x
            if not hit and start is not None:
                length=x-start
                # viewer sees +X on left when facing the -Z front
                xc=(cols/2-(start+x)/2)*pixel
                yc=center_y+(rows/2-y-.5)*pixel
                tile=trimesh.creation.box(extents=[length*pixel,pixel,.012]);tile.apply_translation([xc,yc,-.298]);meshes.append(tile);start=None
    if meshes:
        letters=trimesh.util.concatenate(meshes);add('Shield_state_raised_lettering',letters,'legend')
raised_legend('Kalkan etkisiz')
for x,t,c in [(1.24,'OV',(239,221,73)),(0,'OT',(255,159,60)),(-1.24,'SI',(195,29,46))]:
 text_plane('Lamp_label_'+t,t,1.02,.25,x,2.19,-.414,c)
# Fine metal framing and lower cable path grooves, depth and physical fasteners.
for x in [-1.91,1.91]:box('Housing_edge_rail_'+str(x),(.065,3.0,.055),(x,1.65,-.32),'silver')
for y in [.08,.15,.22]:box('Lower_panel_service_seam_'+str(y),(3.72,.025,.035),(0,y,-.33),'gray')
for x in [-1.24,0,1.24]:
 box('Terminal_wire_upper_'+str(x),(.045,.33,.045),(x,.73,-.36),'edge')
 box('Terminal_wire_lower_'+str(x),(.045,.32,.045),(x,.25,-.36),'edge')
out=P/'UC_SEVIYELI_ALARM_PANELI_02_REV7.glb';s.export(out)
print('GLB',out,'bytes',out.stat().st_size,'meshes',len(s.geometry))
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
for name,eye in [('ON',[0,1.8,-8.0]),('YAN',[4.0,3.2,-8.0])]:
 cam=pyrender.PerspectiveCamera(yfov=np.deg2rad(32));node=render.add(cam,pose=look_at(eye,[0,1.55,-.2]));lights=[]
 for loc,intensity in [([-5,7,-7],4.0),([6,4,-5],2.5),([0,1,-6],1.0)]:
  l=pyrender.DirectionalLight(color=[1,1,1],intensity=intensity);lights.append(render.add(l,pose=look_at(loc,[0,1.55,0])))
 r=pyrender.OffscreenRenderer(1200,720);color,_=r.render(render,flags=pyrender.RenderFlags.RGBA);r.delete();Image.fromarray(color).convert('RGB').save(P/f'GLB_{name}.jpg',quality=93);render.remove_node(node)
 for l in lights:render.remove_node(l)
