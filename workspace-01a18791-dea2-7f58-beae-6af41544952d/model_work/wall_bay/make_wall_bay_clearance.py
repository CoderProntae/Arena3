#!/usr/bin/env python3
"""Wall-bay 03A rebuilt FROM ZERO after two rejected prop-like attempts.

Only forms visible in the user's frame are modeled: a continuous two-tone
facility wall, one nearly flush steel inset panel, one horizontal through
opening, a small integrated SL-02 sign and two painted warning bands.
The emitter is an *existing approved GLB*, shown in context but not included
in this deliverable. The optical axis and cut opening are at Z=0.
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
DEBUG=ROOT/'.cache/model_debug';DEBUG.mkdir(parents=True,exist_ok=True)
RNG=random.Random(89345)

# Matte painted STEEL, one subtle map per continuous panel; low-amplitude
# multi-scale wear avoids the tiled wood-grain effect of the rejected attempts.
def patinated(base,seed,size=(768,768),age=.25):
    w,h=size;rr=np.random.default_rng(seed)
    fine=rr.standard_normal((h,w))*2.6
    coarse=Image.fromarray(np.uint8(rr.integers(0,256,(38,38))),mode='L')
    coarse=np.asarray(coarse.resize((w,h),Image.Resampling.BICUBIC),float)-128
    smudge=(coarse*.075+fine*.25)*age
    y,x=np.mgrid[:h,:w]
    v=(x/w-.5)*1.6+(y/h-.5)*1.1
    arr=np.empty((h,w,3),float);arr[:]=base
    arr+=smudge[:,:,None]*np.array([1.,.87,.68])
    arr+=v[:,:,None]*np.array([2.1,1.3,.4])
    im=Image.fromarray(np.uint8(np.clip(arr,0,255)),'RGB')
    draw=ImageDraw.Draw(im,'RGBA')
    for _ in range(int(47*age)):
        u=int(rr.integers(0,w));v=int(rr.integers(0,h));length=int(rr.integers(8,61))
        draw.line((u,v,u+length,v+int(rr.integers(-1,2))),
                  fill=(16,17,21,int(rr.integers(7,24))),width=1)
    return im
UPPER=patinated((142,62,36),612,age=.20) # oxide-orange painted STEEL
WALL=patinated((77,77,80),613,age=.19)  # warm grey-gunmetal wall
LOWER=patinated((43,53,66),614,age=.16) # cobalt-shadowed steel
PLATE=patinated((72,83,93),615,age=.10) # cool unpainted machined steel
DARK=patinated((30,35,44),616,age=.12)
REAR=patinated((151,61,29),617,age=.17)


def make_label():
    im=patinated((21,24,33),660,size=(768,320),age=.13)
    d=ImageDraw.Draw(im)
    d.rectangle((9,10,757,309),outline=(52,51,57),width=3)
    try:
        f1=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',32)
        f2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',50)
    except OSError:f1=f2=ImageFont.load_default()
    for txt,font,cy,ink in [('SL-02',f1,93,(192,67,36)),
                            ('Containment',f2,210,(204,96,52))]:
        bb=d.textbbox((0,0),txt,font=font)
        ww=bb[2]-bb[0];hh=bb[3]-bb[1]
        d.text(((768-ww)//2,cy-hh//2-bb[1]),txt,font=font,fill=ink)
    return im
SIGN=make_label()
# Low-relief hammered metal normal, distinct from the old wood-like broad grain.
rr=np.random.default_rng(621)
h=rr.standard_normal((768,768)).astype('float32')
h=(h+np.roll(h,1,0)+np.roll(h,-1,0)+np.roll(h,1,1)+np.roll(h,-1,1))/5
nx=(np.roll(h,1,1)-np.roll(h,-1,1))*12
ny=(np.roll(h,1,0)-np.roll(h,-1,0))*8
NORMAL=Image.fromarray(np.uint8(np.clip(np.dstack((128+nx,128+ny,np.full_like(nx,250))),0,255)),'RGB')


def m(name,rgb=(255,255,255,255),texture=None,met=.3,rough=.77,emi=(0,0,0),bump=False):
    return trimesh.visual.material.PBRMaterial(name=name,baseColorFactor=rgb,
        baseColorTexture=texture,normalTexture=NORMAL if bump else None,
        metallicFactor=met,roughnessFactor=rough,
        emissiveFactor=emi,doubleSided=True)
MAT={
 'upper':m('01 - Patinated painted steel overhead',texture=UPPER,met=.48,rough=.54,bump=True),
 'wall':m('02 - Desaturated heat-tempered alloy',texture=WALL,met=.64,rough=.48,bump=True),
 'lower':m('03 - Cool oxidized lower metal',texture=LOWER,met=.69,rough=.50,bump=True),
 'panel':m('04 - Brushed steel flush containment plate',texture=PLATE,met=.84,rough=.31,bump=True),
 'dark':m('05 - Blackened structural steel',texture=DARK,met=.62,rough=.48),
 'rear':m('06 - Copper-orange feed cavity',texture=REAR,met=.49,rough=.54),
 'label':m('07 - Integrated equipment number',texture=SIGN,met=.20,rough=.80),
 'edge':m('08 - Satin steel weld edge',(82,77,80,255),met=.70,rough=.51),
 'hazard':m('09 - Worn amber warning enamel',(185,78,36,255),met=.18,rough=.77),
 'bolt':m('10 - Muted steel screw',(117,108,105,255),met=.68,rough=.55),
}
BUCKET={}
def mesh(zone,material,vertices,faces,uv=None):
    verts=np.asarray(vertices,float);tri=np.asarray(faces,int)
    if uv is None:uv=np.zeros((len(verts),2),float)
    uv=np.asarray(uv,float)
    parts=BUCKET.setdefault((zone,material),[[],[],[]])
    base=sum(len(x) for x in parts[0]);parts[0].append(verts)
    parts[1].append(tri+base);parts[2].append(uv)

def quad(zone,material,x,u0,u1,z0,z1,uv=None):
    if uv is None:uv=((0,0),(1,0),(1,1),(0,1))
    mesh(zone,material,[(x,u0,z0),(x,u1,z0),(x,u1,z1),(x,u0,z1)],
         ((0,1,2),(0,2,3)),uv)

def cylinder(zone,material,a,b,r,n=10):
    a=np.array(a,float);b=np.array(b,float);v=b-a;L=np.linalg.norm(v)
    if L<1e-6:return
    q=trimesh.creation.cylinder(radius=r,height=L,sections=n)
    q.apply_transform(trimesh.geometry.align_vectors((0,0,1),v/L))
    q.apply_translation((a+b)*.5)
    mesh(zone,material,q.vertices,q.faces)

def recess_rim(zone,material,front,back,outer,inner):
    # A four-faced real hole with shaped/tilted inner bevel. The flat wall is
    # NOT drawn over the opening (nor is any shutter drawn over the core).
    u0,u1,z0,z1=outer;p0,p1,q0,q1=inner
    for A,B in [((u0,z0),(u1,z0)),((u1,z0),(u1,z1)),
                ((u1,z1),(u0,z1)),((u0,z1),(u0,z0))]:
        # Mapping is by matching corresponding outer/inner corner.
        keys={(u0,z0):(p0,q0),(u1,z0):(p1,q0),
              (u1,z1):(p1,q1),(u0,z1):(p0,q1)}
        C,D=keys[B],keys[A]
        mesh(zone,material,[(front,*A),(front,*B),(back,*C),(back,*D)],
             ((0,1,2),(0,2,3)))

# This whole wall is one physical slice. Original screenshot's warm upper
# cladding, dark-red midline and blue-black lower panels remain continuous.
wall_x=-.40;A=10.1;H=10.25
# Upper wall slopes back to a ceiling joint; lower metal turns toward the floor.
# These are real depth-changing faces, not colored coplanar Part panels.
mesh('FACILITY_SHEET','upper',[(wall_x,-A,5.7),(wall_x,A,5.7),
                                (-3.22,A,H),(-3.22,-A,H)],
     ((0,1,2),(0,2,3)),((0,0),(1,0),(1,1),(0,1)))
quad('FACILITY_SHEET','wall',wall_x,-A,A,3.35,5.7)
quad('FACILITY_SHEET','wall',wall_x,-A,A,-6.3,-3.35)
mesh('FACILITY_SHEET','lower',[(-1.86,-A,-H),(-1.86,A,-H),
                                (wall_x,A,-6.3),(wall_x,-A,-6.3)],
     ((0,1,2),(0,2,3)),((0,0),(1,0),(1,1),(0,1)))
for a,b in [(-A,-6.05),(6.05,A)]:
    quad('FACILITY_SHEET','wall',wall_x,a,b,-3.35,3.35)
# One low-relief bent-steel inset. Its physically sized horizontal socket is
# reproduced once here; arbitrary knobs/vents/lamps were removed.
panel_x=.02;L=8.05;T=8.25
# Visible free clearance around the approved emitter's ~2.72 radius where it
# crosses the wall; do not make the beam/nozzle appear spawned inside steel.
opening_u=5.78;opening_z=3.57
quad('INSET_SHEET','panel',panel_x,-L,L,opening_z,T)
quad('INSET_SHEET','panel',panel_x,-L,L,-T,-opening_z)
for a,b in [(-L,-opening_u),(opening_u,L)]:
    quad('INSET_SHEET','panel',panel_x,a,b,-opening_z,opening_z)
# Thin folds/weld beads: low profile, not a thick sci-fi frame.
for yy in (-L,L):
    cylinder('WELD_SEAMS','dark',(panel_x,yy,-T),(panel_x,yy,T),.075,n=7)
for zz in (-T,T):
    cylinder('WELD_SEAMS','dark',(panel_x,-L,zz),(panel_x,L,zz),.075,n=7)
# Sign is integrated flush, proportionally narrower than the long feed slot.
quad('EQUIPMENT_LABEL','label',panel_x+.012,-3.72,3.72,4.02,6.18)
for zz in (3.98,6.23):
    cylinder('WELD_SEAMS','dark',(panel_x+.025,-3.80,zz),
             (panel_x+.025,3.80,zz),.035,n=6)
# Two painted warning strips. The stripes are nearly flush with the panel;
# the irregular ambient light and grime must come from Studio later.
for zc in (-7.43,7.23):
    quad('WARNING_BAND','dark',panel_x+.010,-7.54,7.54,zc-.38,zc+.38)
    for y in np.arange(-7.35,7.1,1.38):
        yz=[(y,zc-.34),(y+.63,zc-.34),
            (min(y+1.13,7.45),zc+.34),(min(y+.5,7.45),zc+.34)]
        mesh('WARNING_PAINT','hazard',[(panel_x+.025,u,z) for u,z in yz],
             [(0,1,2),(0,2,3)])
# Recessed feed rim = actual open path, not a dark decal on the surface.
recess_rim('FEED_INNER_WALL','dark',.06,-2.20,
           (-opening_u,opening_u,-opening_z,opening_z),
           (-5.23,5.23,-3.02,3.02))
quad('FEED_BACK','rear',-2.33,-5.25,5.25,-3.04,3.04)
# Front lip stays narrow so dark free space and depth remain visible.
for zc in (-opening_z,opening_z):
    cylinder('FEED_TRIM','edge',(.065,-5.80,zc),(.065,5.80,zc),.041,n=7)
for u in (-5.80,5.80):
    cylinder('FEED_TRIM','edge',(.065,u,-opening_z),(.065,u,opening_z),.039,n=7)
# A few realistic fasteners, not a repetitive decorative bolt field.
for yy in (-7.68,7.68):
    for zz in (-5.9,0,5.9):
        cylinder('JOINT_BOLTS','bolt',(.03,yy,zz),(.12,yy,zz),.085,n=10)
for zz in (-7.88,7.87):
    for yy in (-6.6,0,6.6):
        cylinder('JOINT_BOLTS','bolt',(.03,yy,zz),(.12,yy,zz),.073,n=9)
# Large sheet seam follows octagonal architecture rather than oversized rim.
for zz in (5.72,-6.32):
    cylinder('WALL_SHEET_SEAMS','dark',(-.38,-A,zz),(-.38,A,zz),.048,n=7)
for zz in (7.61,8.55,9.46):
    xx=wall_x+(zz-5.7)/(H-5.7)*(-3.22-wall_x)
    cylinder('UPPER_RACEWAYS','edge',(xx+.055,-A+.36,zz),
             (xx+.055,A-.36,zz),.043,n=7)
for side in (-1,1):
    cylinder('WALL_SHEET_SEAMS','dark',(wall_x,side*A,-6.3),
             (wall_x,side*A,5.7),.07,n=8)

scene=trimesh.Scene();triangle_count=0
for (zone,material),(v,f,u) in BUCKET.items():
    obj=trimesh.Trimesh(vertices=np.concatenate(v),faces=np.concatenate(f),process=False)
    obj.visual=trimesh.visual.texture.TextureVisuals(uv=np.concatenate(u),material=MAT[material])
    scene.add_geometry(obj,geom_name=f'{zone}__{material}')
    triangle_count+=len(obj.faces)
GLB=OUT/'REACTOR_WALL_CLEARANCE_REV05.glb';GLB.write_bytes(scene.export(file_type='glb'))

# The actual emitter cross section near the wall, not its much larger focusing
# head, is what determines port size. At the front wall plane X=0.06 it is
# local X=-8.27 with a radial mesh envelope ~2.72 < cut half-height 3.57.
EM=trimesh.load(OUT/'REACTOR_EMITTER_REV03.glb',force='scene')
emitter_world=trimesh.Scene()
for k,g in scene.geometry.items():emitter_world.add_geometry(g,geom_name='W_'+k)
T=np.eye(4);T[:3,3]=[8.33,0,0]
for k,g in EM.geometry.items():emitter_world.add_geometry(g,geom_name='E_'+k,transform=T)


def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    right=np.cross(f,(0,0,1.));right/=np.linalg.norm(right)
    up=np.cross(right,f)
    P=np.eye(4);P[:3,:3]=np.stack((right,up,-f),axis=1);P[:3,3]=eye
    return P

def view(ts):
    sc=pyrender.Scene.from_trimesh_scene(ts,bg_color=[.014,.012,.027,1],
                                        ambient_light=[.20,.17,.21])
    for pos,color,power in [((8,-8,8),(1.,.42,.15),225),
                            ((8,7,6),(.51,.40,.92),70),
                            ((13,-1,-9),(.32,.32,1.),49)]:
        t=np.eye(4);t[:3,3]=pos
        sc.add(pyrender.PointLight(color=np.array(color),intensity=power),pose=t)
    return sc
renderer=pyrender.OffscreenRenderer(1310,850)
def render(sc,eye,target,angle):
    cam=sc.add(pyrender.PerspectiveCamera(yfov=math.radians(angle)),pose=look(eye,target))
    rgb,_=renderer.render(sc,flags=pyrender.RenderFlags.RGBA)
    sc.remove_node(cam)
    return Image.fromarray(rgb,'RGBA').convert('RGB')
solo=view(scene);combo=view(emitter_world)
front=render(solo,(20,0,0),(0,0,0),49)
iso=render(solo,(19,-10,5),(0,0,0),49)
join=render(combo,(30,-17,7),(7,0,0),47)
renderer.delete()
front.save(DEBUG/'WALL_REV05_FRONT.png');iso.save(DEBUG/'WALL_REV05_ISO.png')
join.save(OUT/'REACTOR_WALL_REV05_WITH_EMITTER.png')

# Plain, honest comparison board: panel mesh from our GLB alongside the user's
# frame. Blue/purple smoke, bright beams and alarm lights are future Studio VFX.
board=Image.new('RGB',(1850,1280),(13,17,26));d=ImageDraw.Draw(board)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
    body=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
except OSError:title=body=small=ImageFont.load_default()
def panel(im,x,y,w,h,label):
    d.rectangle((x,y,x+w,y+h),fill=(23,27,41))
    t=ImageOps.contain(im,(w,h),Image.Resampling.LANCZOS)
    board.paste(t,(x+(w-t.width)//2,y+(h-t.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(75,84,108),width=2)
    d.text((x+13,y+12),label,font=body,fill=(243,244,250),stroke_width=1,stroke_fill=(10,12,19))
d.text((44,29),'MODEL 03A REV05 / YAYICI İÇİN GÖRÜNÜR DUVAR BOŞLUĞU',font=title,fill=(238,243,248))
d.text((44,77),'Korunan metal gövde  •  yayıcının çevresinde koyu boşluk  •  daha derin duvar tüneli  •  Studio görüntüsü değil',font=body,fill=(169,186,204))
panel(join,44,118,1080,660,'Birleşim: onaylı yayıcı + yeni duvar modeli (çevrimdışı)')
panel(front,1147,118,659,660,'Önden: duvara gömülü yatay yuva')
close=join.crop((352,262,766,560))
panel(close,44,815,575,394,'Yakın plan: yayıcının etrafındaki koyu açıklık')
ref=Image.open(ROOT/'model_work/reference_crops/ROOM_LEFT_1321.png').convert('RGB')
panel(ref,642,815,547,394,'Referans: SL-02 duvarı')
ref2=Image.open(ROOT/'model_work/reference_crops/ROOM_RIGHT_1321.png').convert('RGB')
panel(ref2,1212,815,594,394,'Referans: karşı duvar')
d.text((44,1238),f'GLB {GLB.stat().st_size/1e6:.2f} MB   /   {triangle_count:,} üçgen   /   yayıcı R~2.72, yuva yarı-yükseklik 3.57, en az 0.85 dikey görünür pay (ön yüz)',
       font=small,fill=(175,190,212))
PRE=OUT/'REACTOR_WALL_CLEARANCE_REV05_ONAY.png';board.save(PRE,optimize=True)
print('EXPORT',GLB,GLB.stat().st_size,'bytes',len(scene.geometry),'meshes',triangle_count,'triangles')
print('PREVIEW',PRE)
