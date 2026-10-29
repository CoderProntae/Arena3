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
           (-5.23,5.23,-3.31,3.31))
# Deliberately NO rear quad. This is a through-hole into the housing behind
# the wall. All 3D emitter geometry (max radius 3.07) can pass through it.
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

# Two actual, individually moveable shutter leaves. The COLD GLB stores them
# closed; in Studio their separate mesh nodes slide laterally along local Y.
# Neither leaf is a cover across the reactor's CENTRAL core, only a wall-port
# hatch for a single approved emitter.
for side in (-1,1):
    zone='HATCH_LEFT' if side==-1 else 'HATCH_RIGHT'
    y0,y1=(-5.80,.04) if side==-1 else (-.04,5.80)
    z0,z1=-3.62,3.62
    bevel=.18
    path=[(y0+bevel,z0),(y1-bevel,z0),(y1,z0+bevel),
          (y1,z1-bevel),(y1-bevel,z1),(y0+bevel,z1),
          (y0,z1-bevel),(y0,z0+bevel)]
    # Real thick chamfered slab; no opaque wall/back plane behind it.
    front_vs=[(.245,u,z) for u,z in path]
    back_vs=[(.055,u,z) for u,z in path]
    mesh(zone,'panel',front_vs,
         [(0,i,i+1) for i in range(1,len(path)-1)],
         [((u-y0)/(y1-y0),(z-z0)/(z1-z0)) for u,z in path])
    mesh(zone,'dark',back_vs,
         [(0,i+1,i) for i in range(1,len(path)-1)])
    for i in range(len(path)):
        j=(i+1)%len(path)
        mesh(zone,'edge',[front_vs[i],front_vs[j],back_vs[j],back_vs[i]],
             [(0,1,2),(0,2,3)])
    # A small gasket along the middle seam and one understated safety mark.
    center_edge=y1 if side==-1 else y0
    cylinder(zone,'dark',(.272,center_edge,-3.35),
             (.272,center_edge,3.35),.068,n=7)
    for zz in (-2.7,2.7):
        mesh(zone,'hazard',[(.267,y0+.70,zz-.14),(.267,y0+1.16,zz-.14),
                            (.267,y0+1.34,zz+.14),(.267,y0+.88,zz+.14)],
             [(0,1,2),(0,2,3)])
# Rails physically continue into adjacent wall segments. Left/right shutters
# each move 5.84 studs to clear the full 11.56-stud passage.
for zz in (-3.81,3.81):
    # Hidden guide track behind the face sheet; don't draw two gratuitous
    # rods across the closed doors like in an unfinished sci-fi prop.
    cylinder('HATCH_RAILS','dark',(-.12,-11.87,zz),(-.12,11.87,zz),.045,n=8)
for side in (-1,1):
    for zz in (-3.81,3.81):
        cylinder('HATCH_RAILS','edge',(-.11,side*7.63,zz),
                 (-.11,side*11.73,zz),.035,n=7)

scene=trimesh.Scene();triangle_count=0
for (zone,material),(v,f,u) in BUCKET.items():
    obj=trimesh.Trimesh(vertices=np.concatenate(v),faces=np.concatenate(f),process=False)
    obj.visual=trimesh.visual.texture.TextureVisuals(uv=np.concatenate(u),material=MAT[material])
    scene.add_geometry(obj,geom_name=f'{zone}__{material}')
    triangle_count+=len(obj.faces)
GLB=OUT/'REACTOR_WALL_HATCH_THROUGH_01.glb'
GLB.write_bytes(scene.export(file_type='glb'))

# Opening is a physical cut: there is no rear face. Approved emitter remains a
# distinct rigid model, moving as a whole; it is never stretched on startup.
EM=trimesh.load(OUT/'REACTOR_EMITTER_REV03.glb',force='scene')
DOOR_TRAVEL=5.85
PISTON_TRAVEL=19.80
EXTENDED_ORIGIN=8.33
RETRACTED_ORIGIN=EXTENDED_ORIGIN-PISTON_TRAVEL

def variant(open_fraction,extension_fraction):
    sc=trimesh.Scene()
    for key,g in scene.geometry.items():
        T=np.eye(4)
        if key.startswith('HATCH_LEFT'):T[1,3]=-DOOR_TRAVEL*open_fraction
        if key.startswith('HATCH_RIGHT'):T[1,3]=DOOR_TRAVEL*open_fraction
        sc.add_geometry(g,geom_name='W_'+key,transform=T)
    e=np.eye(4)
    e[0,3]=RETRACTED_ORIGIN+PISTON_TRAVEL*extension_fraction
    for key,g in EM.geometry.items():
        sc.add_geometry(g,geom_name='EM_'+key,transform=e)
    return sc

def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    right=np.cross(f,(0,0,1.));right/=np.linalg.norm(right)
    up=np.cross(right,f)
    P=np.eye(4);P[:3,:3]=np.stack((right,up,-f),axis=1);P[:3,3]=eye
    return P

def lit(ts):
    p=pyrender.Scene.from_trimesh_scene(ts,bg_color=[.012,.012,.026,1],
        ambient_light=[.22,.20,.23])
    for pos,color,power in [((8,-8,9),(1.,.42,.17),230),
                            ((10,6,6),(.46,.49,.96),80),
                            ((13,-3,-9),(.30,.32,.99),53)]:
        T=np.eye(4);T[:3,3]=pos
        p.add(pyrender.PointLight(color=np.asarray(color),intensity=power),pose=T)
    return p

R=pyrender.OffscreenRenderer(1240,810)
def shot(state,eye=(28,-15,6),target=(1,0,0),fov=53):
    sc=lit(state)
    cam=sc.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)),
               pose=look(eye,target))
    rgba,_=R.render(sc,flags=pyrender.RenderFlags.RGBA)
    return Image.fromarray(rgba,'RGBA').convert('RGB')
cold=shot(variant(0,0),eye=(24,-13,5),target=(0,0,0))
open_wait=shot(variant(1,0),eye=(24,-13,5),target=(0,0,0))
emerged=shot(variant(1,1),eye=(31,-17,6),target=(7,0,0),fov=54)
R.delete()
cold.save(DEBUG/'HATCH_CLOSED.png')
open_wait.save(DEBUG/'HATCH_OPEN_BEFORE_PISTON.png')
emerged.save(DEBUG/'HATCH_OPEN_EMITTER_OUT.png')

board=Image.new('RGB',(1870,1430),(13,18,27));d=ImageDraw.Draw(board)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',31)
    label=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
    foot=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
except OSError:title=label=foot=ImageFont.load_default()
def panel(img,x,y,w,h,text):
    d.rectangle((x,y,x+w,y+h),fill=(22,27,41))
    a=ImageOps.contain(img,(w,h),Image.Resampling.LANCZOS)
    board.paste(a,(x+(w-a.width)//2,y+(h-a.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(75,84,108),width=2)
    d.text((x+14,y+12),text,font=label,fill=(240,244,251),stroke_width=1,stroke_fill=(12,15,21))
d.text((43,24),'MODEL 03A / GERÇEK DELİK + İKİ HAREKETLİ DUVAR KAPAĞI',font=title,fill=(241,245,253))
d.text((43,77),'Kapaklar yanlara kayar → piston tüm yayıcıyı ittirir → ışın daha sonra açılır; çevrimdışı 3B durum önizlemesi',font=label,fill=(172,190,209))
panel(cold,43,124,869,537,'COLD — çift kapak kapalı / yayıcı içeride')
panel(open_wait,941,124,885,537,'STARTUP 1 — kapaklar açıldı / yayıcı içeride')
panel(emerged,43,706,1055,637,'STARTUP 2 — piston itti / yayıcı dışarıda')
ref=Image.open(ROOT/'model_work/reference_crops/ROOM_LEFT_1321.png').convert('RGB')
panel(ref,1125,706,701,637,'Referans — yan duvar (aktif an)')
d.text((43,1381),f'GLB {GLB.stat().st_size/1e6:.2f} MB  /  {triangle_count:,} üçgen  /  açık port 11.56 x 7.14 birim  /  kapak ve yayıcı ayrı hareketli düğümler',
       font=foot,fill=(172,190,211))
PRE=OUT/'REACTOR_WALL_HATCH_THROUGH_01_ONAY.png';board.save(PRE,optimize=True)
print('EXPORT',GLB,GLB.stat().st_size,'bytes',len(scene.geometry),'meshes',triangle_count,'triangles')
print('PREVIEW',PRE)
