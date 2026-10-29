#!/usr/bin/env python3
"""Containment wall emitter bay, replacement for the rejected wooden chamber.

A reference-observed, standalone machined-steel wall module with a real open
feed recess, bent-metal flanges, original abrasion maps, warning bands,
embossed label/bolts and vent microgeometry. No third-party models. Emission
from the reactor and room smoke are intentionally NOT baked into this asset.
Axis: +X faces INTO chamber; local Y is plate width; local Z is up.
"""
from __future__ import annotations
import os,sys,math,random
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
os.environ['PYOPENGL_PLATFORM']='egl'
sys.path[:0]=['/home/user/.cache/modeldeps','/home/user/.cache/modelrender']
import trimesh,pyrender
ROOT=Path('/home/user');OUT=ROOT/'model_exports';OUT.mkdir(exist_ok=True)
DB=ROOT/'.cache/model_debug';DB.mkdir(parents=True,exist_ok=True)
RNG=random.Random(62564)

# Brushed/scuffed STEEL, not blotchy orange noise that reads as wood.
def brushed_metal(rgb,seed,wear=.7,sz=1024):
    rng=np.random.default_rng(seed)
    y,x=np.mgrid[:sz,:sz]
    # Directional nanograin along U (image horizontal) + rare machining marks.
    scratches=rng.normal(0,1,(sz,sz))*4.0
    streak=rng.normal(0,1,sz)
    for _ in range(4):streak=(streak+np.roll(streak,1)+np.roll(streak,-1))/3
    scratches+=streak[y]*2.1
    base=np.empty((sz,sz,3),float);base[:]=rgb
    vignette=(x-sz*.5)**2/(sz*sz*.28)+(y-sz*.55)**2/(sz*sz*.65)
    base-=vignette[:,:,None]*np.array([2.0,2.5,3.0])*wear
    base+=scratches[:,:,None]*np.array([.70,.75,.82])*wear
    arr=np.uint8(np.clip(base,3,250));im=Image.fromarray(arr,'RGB')
    d=ImageDraw.Draw(im,'RGBA')
    for _ in range(185):
        u=int(rng.integers(0,sz));v=int(rng.integers(0,sz))
        w=int(rng.integers(6,124));a=int(rng.integers(8,29))
        d.line((u,v,u+w,v+int(rng.integers(-1,2))),fill=(193,195,195,a),width=1)
    for _ in range(30):
        u=int(rng.integers(0,sz));v=int(rng.integers(0,sz))
        d.line((u,v,u+int(rng.integers(15,83)),v),fill=(9,11,14,43),width=1)
    return im

DARK=brushed_metal((37,42,47),101,.42)
PAINT=brushed_metal((42,48,53),107,.25)
STEEL=brushed_metal((126,132,137),111,.36)
SOCKET=brushed_metal((114,43,25),120,.36)
# Compact normal map derived from fine rolling marks; slopes, not a wooden
# cellular pattern. glTF embeds this texture for physical metal relief.
noise=np.asarray(DARK.convert('L'),dtype=np.float32)
gx=(np.roll(noise,-1,axis=1)-np.roll(noise,1,axis=1))*.13
gy=(np.roll(noise,-1,axis=0)-np.roll(noise,1,axis=0))*.07
normal=np.dstack([np.uint8(np.clip(128-gx,0,255)),
                  np.uint8(np.clip(128-gy,0,255)),
                  np.uint8(np.full_like(gx,251))])
NORMAL=Image.fromarray(normal,'RGB')

def paint_sign():
    im=brushed_metal((18,21,29),209,.19).crop((0,0,1024,512))
    d=ImageDraw.Draw(im)
    d.rectangle((12,12,1011,499),outline=(84,81,77),width=4)
    try:
        small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',51)
        large=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',84)
    except OSError:small=large=ImageFont.load_default()
    d.text((363,117),'SL - 02',font=small,fill=(174,66,31))
    d.text((230,255),'Containment',font=large,fill=(210,103,47))
    return im
SIGN=paint_sign()

def pbr(name,rgba=(255,255,255,255),image=None,rough=.52,metal=.7,
        emiss=(0.,0.,0.),use_normal=False):
    return trimesh.visual.material.PBRMaterial(name=name,
       baseColorFactor=rgba,baseColorTexture=image,
       normalTexture=NORMAL if use_normal else None,
       roughnessFactor=rough,metallicFactor=metal,emissiveFactor=emiss,
       doubleSided=True)
M={
 'body':pbr('01 - Brushed oxidized structural steel',image=DARK,rough=.67,metal=.69,use_normal=True),
 'paint':pbr('02 - Heat aged dark enamel',image=PAINT,rough=.70,metal=.55,use_normal=True),
 'edge':pbr('03 - Scraped machined steel',image=STEEL,rough=.47,metal=.82),
 'socket':pbr('04 - Heat soaked steel inner cup',image=SOCKET,rough=.64,metal=.65),
 'sign':pbr('05 - Equipment number on inset plate',image=SIGN,rough=.69,metal=.35),
 'black':pbr('06 - Actual recessed aperture',(9,11,16,255),rough=.85,metal=.27),
 'red':pbr('07 - Warning enamel',(151,53,24,255),rough=.64,metal=.34),
 'lamp':pbr('08 - Narrow containment status lamp',(186,72,32,255),rough=.42,metal=.17,emiss=(.42,.045,.008)),
 'bolt':pbr('09 - Hardened fasteners',(120,128,133,255),rough=.39,metal=.82),
}
# Avoid importing a Blender/canvas placeholder: every region below becomes a
# named true triangle mesh. Shared material textures embed ONCE into GLB.
G={}
def add(zone,kind,v,f,uv=None):
    v=np.asarray(v,float);f=np.asarray(f,int)
    if uv is None:uv=np.zeros((len(v),2),float)
    uv=np.asarray(uv,float)
    items=G.setdefault((zone,kind),[[],[],[]])
    offset=sum(len(a) for a in items[0]);items[0].append(v)
    items[1].append(f+offset);items[2].append(uv)

def face(zone,kind,p,uv=None):
    f=[(0,i,i+1) for i in range(1,len(p)-1)]
    if uv is None:
        uv=[((a[1]+7.6)/15.2,(a[2]+9.2)/18.4) for a in p]
    add(zone,kind,p,f,uv)

def box(zone,kind,center,extent):
    m=trimesh.creation.box(extents=extent);m.apply_translation(center)
    add(zone,kind,m.vertices,m.faces)

def rod(zone,kind,a,b,r,n=10):
    a=np.asarray(a,float);b=np.asarray(b,float);vec=b-a
    L=np.linalg.norm(vec)
    if L<.00001:return
    m=trimesh.creation.cylinder(radius=r,height=L,sections=n)
    m.apply_transform(trimesh.geometry.align_vectors([0,0,1],vec/L))
    m.apply_translation((a+b)/2)
    add(zone,kind,m.vertices,m.faces)

# Twelve-sided stamp cut with real bevels: the front is not a giant box.
P=np.array([(-6.35,-8.75),(6.35,-8.75),(7.15,-8.25),(7.15,-7.25),
            (7.38,-6.90),(7.38,6.90),(7.15,7.25),(7.15,8.25),
            (6.35,8.75),(-6.35,8.75),(-7.15,8.25),(-7.15,7.25),
            (-7.38,6.90),(-7.38,-6.90),(-7.15,-7.25),(-7.15,-8.25)],float)
# Actual folded rim has a crenellated four-step cross section.
for x0,s0,x1,s1,kind in [
    (-.62,1.0,-.25,1.0,'black'),
    (-.25,1.0,.18,.984,'body'),
    (.18,.984,.37,.955,'edge'),
    (.37,.955,.48,.924,'black'),
    (.48,.924,.67,.895,'edge'),
]:
    for i in range(len(P)):
        q=(i+1)%len(P)
        a,b=P[i]*s0,P[q]*s0;c,d=P[q]*s1,P[i]*s1
        face('OUTER_FOLDED_RIM',kind,[(x0,*a),(x0,*b),(x1,*c),(x1,*d)])
# Inset continuous panel with a TRUE central hole. Four separate strips around
# its aperture keep the reactor socket open to a 1.3-stud-deep interior.
Y=6.35;Z=7.80;x=.50
hole_u=4.65;hole_z0=-3.08;hole_z1=1.50
face('FRONT_PANEL','paint',[(x,-Y,hole_z1),(x,Y,hole_z1),(x,Y,Z),(x,-Y,Z)])
face('FRONT_PANEL','paint',[(x,-Y,-Z),(x,Y,-Z),(x,Y,hole_z0),(x,-Y,hole_z0)])
face('FRONT_PANEL','paint',[(x,-Y,hole_z0),(x,-hole_u,hole_z0),
                           (x,-hole_u,hole_z1),(x,-Y,hole_z1)])
face('FRONT_PANEL','paint',[(x,hole_u,hole_z0),(x,Y,hole_z0),
                           (x,Y,hole_z1),(x,hole_u,hole_z1)])
# A shallow dark surround raised above the paint + three full-depth folds.
for u0,u1,z0,z1 in [(-5.15,5.15,1.52,1.96),
                     (-5.15,5.15,-3.55,-3.06),
                     (-5.15,-4.65,-3.55,1.96),
                     (4.65,5.15,-3.55,1.96)]:
    box('FEED_BEZEL','black',(.61,(u0+u1)*.5,(z0+z1)*.5),(.17,u1-u0,z1-z0))
for depth,w,h,kind in ((.57,4.63,3.06,'edge'),
                       (.14,4.31,2.75,'body'),
                       (-.63,4.07,2.52,'socket'),
                       (-1.20,3.76,2.27,'black')):
    pass
# Intricate four annular corners with inner sloping metal surfaces.
outer=[(-4.64,-3.07),(4.64,-3.07),(4.64,1.49),(-4.64,1.49)]
inner=[(-3.92,-2.65),(3.92,-2.65),(3.92,1.11),(-3.92,1.11)]
for i in range(4):
    j=(i+1)%4
    oa,ob=outer[i],outer[j];ia,ib=inner[i],inner[j]
    face('FEED_TAPER','edge',[(.56,*oa),(.56,*ob),(-.87,*ib),(-.87,*ia)])
    face('FEED_TAPER','socket',[(-.87,*ia),(-.87,*ib),(-1.53,*ib),(-1.53,*ia)])
face('HOT_FEED_BACK','socket',[(-1.56,-3.93,-2.68),(-1.56,3.93,-2.68),
                              (-1.56,3.93,1.12),(-1.56,-3.93,1.12)])
# Concentric machined grills at back of feeder opening; the approved emitter
# tail plugs into this cavity later, not simply overlays a flat orange sticker.
for yy in np.arange(-3.75,3.75,.67):
    rod('HOT_FEED_BACK','black',(-1.54,yy,-2.47),(-1.54,yy,.92),.045,n=7)
for zz in (-2.1,-.95,.22,1.0):
    rod('HOT_FEED_BACK','red',(-1.51,-3.78,zz),(-1.51,3.78,zz),.062,n=7)
# Extra folded inner socket lip with machine-cut diagonal welds and fasteners.
for s in (-1,1):
    for z in (-2.83,1.29):
        rod('FEED_BEZEL','edge',(.72,s*4.77,z),(.72,s*5.10,z),.062,n=8)
        rod('FEED_BEZEL','bolt',(.76,s*4.91,z),(.92,s*4.91,z),.092,n=9)

# Two narrow side heat vent banks flank the socket, giving true visible depth.
for s in (-1,1):
    yy=s*5.70
    box('SIDE_VENTS','black',(.54,yy,-.85),(.18,.77,6.22))
    for k in range(10):
        z=-3.44+k*.57
        rod('SIDE_VENTS','body',(.76,yy-.39,z),(.76,yy+.39,z+.075),.064,n=6)
    for z in (-4.15,2.22):
        rod('SIDE_VENTS','edge',(.76,yy-.50,z),(.76,yy+.5,z),.057,n=8)
# The dark equipment sign is inset metal with a fine exterior border, not an
# artificially glowing cartoon panel. It sits above the plugged-in emitter.
box('SIGN_FRAME','black',(.56,0,4.91),(.19,9.7,3.73))
box('SIGN_FRAME','edge',(.67,0,4.91),(.12,9.40,3.42))
face('EQUIPMENT_LABEL','sign',[(.745,-4.56,3.37),(.745,4.56,3.37),
                               (.745,4.56,6.45),(.745,-4.56,6.45)],
     uv=[(0,0),(1,0),(1,1),(0,1)])
for side in (-1,1):
    for z in (3.48,6.36):
        rod('SIGN_FRAME','bolt',(.79,side*4.36,z),(.93,side*4.36,z),.073,n=9)
# Warning bands: real parallel inset channels with machine-cut red slanted
# enamel inlays (actual separate triangles, not a pre-printed strip wallpaper).
for zc in (-7.24,7.20):
    box('HAZARD_RECESS','black',(.54,0,zc),(.14,12.65,1.04))
    for u in np.arange(-6.10,6.0,1.21):
        # Hand-clipped parallelograms, including imperfect burnt edges.
        ux=min(6.11,u+.57)
        face('WARNING_INLAYS','red',[(.624,u,zc-.42),(.624,ux,zc-.42),
                                    (.624,min(6.20,ux+.52),zc+.42),
                                    (.624,min(6.20,u+.52),zc+.42)])
    rod('HAZARD_RECESS','edge',(.69,-6.37,zc-.52),(.69,6.37,zc-.52),.035,n=6)
    rod('HAZARD_RECESS','edge',(.69,-6.37,zc+.52),(.69,6.37,zc+.52),.035,n=6)
# Four vertical side closures, thermocouple lamps and physical witness marks.
for s in (-1,1):
    for yy in (s*6.16,s*6.56):
        rod('WELDED_SEAMS','edge',(.64,yy,-6.58),(.64,yy,6.60),.055,n=7)
    box('STATUS_PIP','black',(.73,s*6.38,4.66),(.13,.33,1.36))
    box('STATUS_PIP','lamp',(.82,s*6.38,4.66),(.10,.17,.72))
    for z in (-6.10,-4.7,1.98,3.1,6.99):
        rod('PERIMETER_FASTENERS','black',(.63,s*6.66,z),(.69,s*6.66,z),.125,n=12)
        rod('PERIMETER_FASTENERS','bolt',(.67,s*6.66,z),(.79,s*6.66,z),.083,n=12)
        rod('PERIMETER_FASTENERS','black',(.79,s*6.66-.052,z),(.8,s*6.66+.052,z),.015,n=6)
for zz in (-8.0,8.02):
    for yy in (-5.5,-3.6,-1.7,1.7,3.6,5.5):
        rod('PERIMETER_FASTENERS','bolt',(.59,yy,zz),(.74,yy,zz),.085,n=10)
# Micro-scrapes have material rather than symmetric decorative symmetry.
for _ in range(55):
    u=RNG.uniform(-5.0,5.0);z=RNG.choice([-1,1])*RNG.uniform(3.45,6.8)
    length=RNG.uniform(.09,.46)
    rod('SURFACE_SCORING','black',(.51,u,z),(.51,u+length,z+RNG.uniform(-.04,.04)),
        .006,n=5)

scene=trimesh.Scene();count=0
for (zone,kind),(vs,fs,uvs) in G.items():
    mesh=trimesh.Trimesh(vertices=np.concatenate(vs),faces=np.concatenate(fs),process=False)
    mesh.visual=trimesh.visual.texture.TextureVisuals(uv=np.concatenate(uvs),material=M[kind])
    scene.add_geometry(mesh,geom_name=f'{zone}__{kind}');count+=len(mesh.faces)
GLB=OUT/'REACTOR_WALL_FEED_BAY_01.glb';GLB.write_bytes(scene.export(file_type='glb'))

# Render isolated mesh and its interaction with the approved emitter. All
# right-hand renders are created from exported mesh data; no concept art.
def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    rt=np.cross(f,[0,0,1.]);rt/=np.linalg.norm(rt)
    up=np.cross(rt,f)
    T=np.eye(4);T[:3,:3]=np.stack([rt,up,-f],axis=1);T[:3,3]=eye
    return T

def make_view(ts,bg=(.016,.020,.029,1),ambient=(.23,.24,.27)):
    p=pyrender.Scene.from_trimesh_scene(ts,bg_color=bg,ambient_light=ambient)
    for pos,col,intensity in [((9,-6,11),(.86,.91,1.),140),
                              ((4,7,4),(1.,.48,.20),67),
                              ((8,1,-10),(.18,.43,.84),43)]:
        T=np.eye(4);T[:3,3]=pos
        p.add(pyrender.PointLight(color=np.array(col),intensity=intensity),pose=T)
    return p

ren=pyrender.OffscreenRenderer(1260,820)
def shot(view,eye,target=(0,0,0),fov=42):
    node=view.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)),pose=look(eye,target))
    rgba,_=ren.render(view,flags=pyrender.RenderFlags.RGBA)
    view.remove_node(node)
    return Image.fromarray(rgba,'RGBA').convert('RGB')
view=make_view(scene)
frontal=shot(view,(21,0,2),fov=42)
oblique=shot(view,(20,-11,7),fov=43)
# Since the verified emitter REV03 is an approved *different* asset,
# contextual assembly is shown but it is not quietly bundled into the bay GLB.
assembly=trimesh.Scene()
for name,g in scene.geometry.items():assembly.add_geometry(g,geom_name='BAY_'+name)
em=trimesh.load(OUT/'REACTOR_EMITTER_REV03.glb',force='scene')
X=np.eye(4);X[:3,3]=[8.33,0,0]
for name,g in em.geometry.items():assembly.add_geometry(g,geom_name='EM_'+name,transform=X)
combined=shot(make_view(assembly), (28,-15,7),target=(7,0,0),fov=42)
ren.delete()
frontal.save(DB/'WALL_BAY_FRONT_01.png');oblique.save(DB/'WALL_BAY_OBLIQUE_01.png')
combined.save(OUT/'REACTOR_WALL_BAY_WITH_APPROVED_EMITTER_01.png')

board=Image.new('RGB',(1810,1300),(13,18,27));d=ImageDraw.Draw(board)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',29)
    label=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    foot=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
except OSError:title=label=foot=ImageFont.load_default()
def panel(im,x,y,w,h,text):
    d.rectangle((x,y,x+w,y+h),fill=(25,31,44))
    a=ImageOps.contain(im,(w,h),Image.Resampling.LANCZOS)
    board.paste(a,(x+(w-a.width)//2,y+(h-a.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(75,88,109),width=2)
    d.text((x+13,y+11),text,font=label,fill=(243,244,246),stroke_width=1,stroke_fill=(10,12,19))
d.text((43,28),'MODEL 03A / YAYICI MONTAJ YUVASI — METAL 3B MODÜL',font=title,fill=(239,243,250))
d.text((43,76),'Reddedilen tahtamsı oda yerine: katlanmış metal, gerçek açık oyuk, işlenmiş çerçeve, fiziksel vida ve şeritler',font=label,fill=(177,190,207))
panel(oblique,42,118,1034,610,'3/4 açı — tek başına gerçek .glb mesh')
panel(frontal,1100,118,663,610,'Ön açı — açık yuva / metal işçiliği')
panel(combined,42,766,760,462,'Onaylı yayıcıyla geçici çevrimdışı yerleşim')
ref=Image.open(ROOT/'model_work/reference_crops/ROOM_LEFT_1321.png').convert('RGB')
panel(ref,823,766,449,462,'Referans: yan duvar • 13:21')
ref2=Image.open(ROOT/'model_work/reference_crops/ROOM_RIGHT_1321.png').convert('RGB')
panel(ref2,1290,766,473,462,'Referans: karşı duvar • 13:21')
d.text((43,1257),f'GLB {GLB.stat().st_size/1e6:.2f} MB  /  {count:,} üçgen  /  {len(scene.geometry)} adlandırılmış mesh  /  tam oda bu modele dahil değil',font=foot,fill=(173,186,206))
PRE=OUT/'REACTOR_WALL_FEED_BAY_ONAY_01.png';board.save(PRE,optimize=True)
print('EXPORT',GLB,GLB.stat().st_size,'bytes,',len(scene.geometry),'meshes,',count,'triangles')
print('PREVIEW',PRE)
