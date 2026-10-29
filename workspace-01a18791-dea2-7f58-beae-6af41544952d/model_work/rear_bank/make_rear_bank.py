#!/usr/bin/env python3
"""Model 04: the paired tall *rear wall vent/service banks* seen behind the star.

Reference: uploads/image-3.png, image-7.png and ROOM_1727.png. Two separated
banks with THREE tall arched dark slots per side and four upper vents are visible;
we do not assert the exact hidden purpose or reproduce invisible machinery.
No rejected chamber shell is reused, and the center remains physically OPEN.
Each arch has true front-frame openings, depth, recess wall, interior louvers,
and a back surface, not a texture painted over a solid forward wall.

The GLB is a standalone rear-bank assembly in provisional reactor coordinates:
X horizontal, Y toward back wall (camera on -Y), Z up; mounting plane Y~14.
Not yet integrated into Roblox Studio. User approval of this individual model
is required before it is installed in the jointly approved reactor.
"""
from __future__ import annotations
import os,sys,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
os.environ['PYOPENGL_PLATFORM']='egl'
sys.path[:0]=['/home/user/.cache/modeldeps','/home/user/.cache/modelrender']
import trimesh,pyrender

ROOT=Path('/home/user');OUT=ROOT/'model_exports';OUT.mkdir(exist_ok=True)
DBG=ROOT/'.cache/model_debug';DBG.mkdir(parents=True,exist_ok=True)

# Uniform two-dimensional flake noise (not directional woodgrain) is mapped to
# real anodized steel faces. Steel is primarily metal; orange is worn primer.
def steel_paint(rgb,seed):
    rng=np.random.default_rng(seed);sz=512
    coarse=np.asarray(Image.fromarray(rng.integers(0,256,(45,45),dtype=np.uint8),'L').resize((sz,sz),Image.Resampling.BILINEAR),dtype=float)-128
    fine=rng.standard_normal((sz,sz))*2.3
    data=np.empty((sz,sz,3),dtype=float);data[:]=rgb
    data+=(coarse*.043+fine)[:,:,None]*np.array([1,.73,.65])
    # sparse scuffs make the finish machined, not organic grain
    wear=rng.random((sz,sz))<.0017;data[wear]+=rng.uniform(-13,10,wear.sum())[:,None]
    return Image.fromarray(np.uint8(np.clip(data,1,255)),'RGB')

def material(name,rgb,metal=.56,rough=.51,texture=None,emit=(0,0,0)):
    return trimesh.visual.material.PBRMaterial(
        name=name,baseColorFactor=[*((255,255,255) if texture else rgb),255],
        baseColorTexture=texture,metallicFactor=metal,roughnessFactor=rough,
        emissiveFactor=emit,doubleSided=True)
M={
 'paint':material('01 Cool rolled blue-black ferrochrome',(255,255,255),.76,.53,steel_paint((54,66,79),621)),
 'wall':material('00 Worn orange steel wall mounting sheet',(255,255,255),.58,.65,steel_paint((117,72,53),622)),
 'steel':material('02 Graphite rolled structural steel',(42,51,63),.74,.51),
 'edge':material('03 Machined gunmetal cut edges',(114,132,143),.79,.38),
 'recess':material('04 Deep actual duct cavity',(11,19,36),.20,.81),
 'slat':material('05 Cobalt ceramic-coated vent slats',(21,43,77),.47,.60),
 'spine':material('06 Embossed smoked titanium grille ribs',(61,83,108),.64,.42),
 'blue':material('07 Narrow passive blue enamel inlay',(41,88,131),.30,.58),
 'copper':material('08 Dark heat-stained brass conduit',(130,73,52),.68,.51),
 'seal':material('09 Flexible black compression seal',(10,13,19),.08,.95),
 'amber':material('10 Unlit orange inspection-mark paint',(159,79,43),.30,.65),
}
BUCKET={}

def add(zone,kind,mesh,uv=None):
    assert len(mesh.faces)>0
    if uv is None:
        # X/Z steel paint projection. The shell is not a single noisy decal.
        v=mesh.vertices;uv=np.stack((v[:,0]*.133,v[:,2]*.092),axis=1)
    BUCKET.setdefault((zone,kind),[]).append((mesh.vertices,mesh.faces,uv))

def block(cx,cy,cz,sx,sy,sz,zone,kind,rx=0):
    g=trimesh.creation.box(extents=(sx,sy,sz))
    if rx:g.apply_transform(trimesh.transformations.rotation_matrix(rx,(1,0,0)))
    g.apply_translation((cx,cy,cz));add(zone,kind,g)

def quad(pts,zone,kind):
    g=trimesh.Trimesh(vertices=np.asarray(pts,float),faces=np.asarray([(0,1,2),(0,2,3)]),process=False)
    add(zone,kind,g)

def tube(a,b,r,zone,kind,sections=8):
    a=np.asarray(a,float);b=np.asarray(b,float);d=b-a
    n=np.linalg.norm(d)
    if n<.001:return
    g=trimesh.creation.cylinder(radius=r,height=n,sections=sections)
    g.apply_transform(trimesh.geometry.align_vectors((0,0,1),d/n))
    g.apply_translation((a+b)*.5);add(zone,kind,g)

def bolt(x,y,z,zone):
    # Hex nut is physical, visually small, repeated only at structural joints.
    g=trimesh.creation.cylinder(radius=.082,height=.08,sections=6)
    g.apply_transform(trimesh.geometry.align_vectors((0,0,1),(0,-1,0)))
    g.apply_translation((x,y,z));add(zone,'edge',g)
    tube((x-.025,y-.051,z),(x+.025,y-.052,z),.008,zone,'seal',sections=6)

def tilted_block(cx,cy,cz,sx,sy,sz,rx,zone,kind,ly=0,lz=0):
    R=trimesh.transformations.rotation_matrix(rx,(1,0,0))
    p=np.array((0,ly,lz,1.));p=(R@p)[:3]
    g=trimesh.creation.box(extents=(sx,sy,sz))
    g.apply_transform(R);g.apply_translation((cx+p[0],cy+p[1],cz+p[2]))
    add(zone,kind,g)

# Two independent rear modules: central background will be constructed later
# as part of the *actual* assembled chamber wall, not an opaque reactor shutter.
for side in (-1,1):
    cx=side*10.75
    zone=('REAR_BANK_LEFT' if side==-1 else 'REAR_BANK_RIGHT')
    # Back carrier is genuinely behind the holes; never spans their front.
    block(cx,15.02,2.36,9.65,.20,18.5,zone,'wall')
    block(cx,14.77,2.36,9.37,.12,18.18,zone,'steel')
    # The high vents actually mount to the same structural back-wall sheet,
    # rather than floating on isolated thin rods above the bank.
    block(cx,15.10,13.93,9.64,.22,5.86,zone,'wall')
    block(cx,14.88,11.65,9.80,.18,.29,zone,'steel')
    for x in (cx-4.62,cx+4.62):
        block(x,14.86,13.92,.14,.19,5.63,zone,'steel')
    # Three deep slots. Borders and webs form a true holed front face.
    bottom=-5.45;spring=8.30;r=1.07
    for j,off in enumerate((-2.67,0,2.67)):
        sx=cx+off
        slot=f'{zone}_SLOT_{j+1}'
        # Dark cavity back, side reveals and threshold at a real 1.38 depth.
        block(sx,14.58,1.45,2*r,.17,14.75,slot,'recess')
        for sg in (-1,1):
            x=sx+sg*r
            quad([(x,13.37,bottom),(x,14.70,bottom),
                  (x,14.70,spring),(x,13.37,spring)],slot,'steel')
            # Machined vertical throat edge and small enamel guide inlay.
            tube((x,13.29,bottom),(x,13.29,spring),.052,slot,'edge',10)
            block(x-sg*.15,14.44,1.58,.105,.09,13.08,slot,'blue')
        quad([(sx-r,13.37,bottom),(sx+r,13.37,bottom),
              (sx+r,14.75,bottom),(sx-r,14.75,bottom)],slot,'edge')
        # Curved top tunnel: the front and rear are joined by a sequence of
        # actual curved surfaces around the arch, not a flat arch sticker.
        arc=[]
        for k in range(15):
            theta=math.pi*k/14
            arc.append((sx+r*math.cos(theta),spring+r*math.sin(theta)))
        for (ax,az),(bx,bz) in zip(arc,arc[1:]):
            quad([(ax,13.38,az),(bx,13.38,bz),
                  (bx,14.75,bz),(ax,14.75,az)],slot,'steel')
            quad([(ax,13.32,9.88),(bx,13.32,9.88),
                  (bx,13.32,bz),(ax,13.32,az)],zone,'paint')
            tube((ax,13.22,az),(bx,13.22,bz),.059,slot,'edge',9)
        # An inner set of eight cobalt slats with physical depth and little
        # transverse separators, matching tall blue/black radiator silhouettes.
        for sd in (-1,0,1):
            dx=sd*.52
            block(sx+dx,14.38,1.40,.255,.21,12.9,slot,'slat')
            block(sx+dx-.04,14.16,1.40,.046,.05,12.75,slot,'spine')
        for z in np.arange(-4.25,8.18,1.82):
            block(sx,14.06,z,1.72,.12,.072,slot,'steel')
        # Deeply nested hand-service track rather than glowing active reactor ray.
        for z in (-4.65,7.95):
            block(sx,14.00,z,1.72,.11,.08,slot,'edge')
    # Solid structural columns around the real separate slot cutouts.
    for x in (cx-4.83,cx-1.335,cx+1.335,cx+4.83):
        w=.35 if abs(x-cx)<2 else .58
        block(x,13.64,1.68,w,.69,14.27,zone,'paint')
        tube((x,13.25,-5.46),(x,13.25,8.95),.045,zone,'edge',8)
        for z in (-4.9,-1.25,2.4,6.05,8.6):
            bolt(x,13.21,z,zone)
    # Pressure-resisting horizontal sills with inset bands and proper depth.
    block(cx,13.69,-5.99,9.65,.82,1.16,zone,'paint')
    block(cx,13.64,10.50,9.65,.87,1.80,zone,'paint')
    block(cx,13.11,-6.30,9.15,.17,.12,zone,'edge')
    block(cx,13.12,11.03,9.05,.15,.11,zone,'edge')
    for z in (-6.46,11.49):
        block(cx,14.66,z,9.87,.64,.34,zone,'steel')
    # Bronze elbow conduits only at frame edges, never overlaying the vent holes.
    for sg in (-1,1):
        x=cx+sg*4.44
        tube((x,13.76,-4.77),(x,13.76,9.3),.068,zone,'copper',10)
        for z in (-3.55,1.33,6.22):
            block(x,13.60,z,.37,.25,.28,zone,'steel')
        for z in (-6.11,10.7):bolt(x,13.15,z,zone)
    # Narrow reference-motivated amber warning pillar on *inner* side of banks.
    inner=cx-side*5.30
    block(inner,14.19,2.65,.43,.38,15.35,zone,'steel')
    block(inner,13.91,4.48,.18,.07,7.65,zone,'amber')
    for z in (-4.45,9.90):
        block(inner,13.80,z,.64,.16,.52,zone,'edge')
    # Smaller high-level square vents in the angled upper rear wall surface.
    # A local X-axis rotation slopes the surfaces toward the operator's camera.
    rx=math.radians(-23)
    for n,dx in enumerate((-2.55,2.55)):
        xx=cx+dx;zz=15.10;yy=14.57
        up=f'UPPER_GRILLE_{"LEFT" if side<0 else "RIGHT"}_{n+1}'
        tilted_block(xx,yy,zz,2.92,.20,2.72,rx,up,'paint')
        tilted_block(xx,yy,zz,2.52,.11,2.32,rx,up,'seal',ly=-.151)
        tilted_block(xx,yy,zz,2.25,.09,2.04,rx,up,'recess',ly=-.221)
        for z in (-1.20,1.20):
            tilted_block(xx,yy,zz,2.98,.24,.17,rx,up,'edge',ly=-.155,lz=z)
        for x in (-1.34,1.34):
            tilted_block(xx+x,yy,zz,.18,.22,2.57,rx,up,'edge',ly=-.151)
        for z in np.arange(-.78,.90,.31):
            tilted_block(xx,yy,zz,2.17,.13,.075,rx,up,'spine',ly=-.320,lz=z)
        for x in (-1.28,1.28):
            for z in (-1.16,1.16):
                tilted_block(xx+x,yy,zz,.12,.09,.12,rx,up,'copper',ly=-.32,lz=z)
        # Dark steel mount brackets connect the top grille to the tall bank.
        for x in (-.90,.90):
            tube((xx+x,14.88,11.51),(xx+x,14.44,13.57),.065,up,'steel')

scene=trimesh.Scene();tris=0
for (zone,kind),parts in BUCKET.items():
    vertices=[];faces=[];uv=[];offset=0
    for v,f,u in parts:
        vertices.append(v);faces.append(f+offset);uv.append(u);offset+=len(v)
    m=trimesh.Trimesh(vertices=np.concatenate(vertices),faces=np.concatenate(faces),process=False)
    m.visual=trimesh.visual.texture.TextureVisuals(uv=np.concatenate(uv),material=M[kind])
    scene.add_geometry(m,geom_name=f'{zone}__{kind}')
    tris+=len(m.faces)
GLB=OUT/'REACTOR_REAR_SERVICE_GRILLES_01.glb';GLB.write_bytes(scene.export(file_type='glb'))

# Render *reloaded* GLB, so the approval preview can be checked against the
# deliverable. No rejected chamber is smuggled into this preview's geometry.
check=trimesh.load(GLB,force='scene')
assert len(check.geometry)==len(scene.geometry)
assert all(np.isfinite(g.bounds).all() for g in check.geometry.values())
assert sum(len(g.faces) for g in check.geometry.values())==tris

def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    rt=np.cross(f,[0,0,1.]);rt/=np.linalg.norm(rt)
    up=np.cross(rt,f)
    p=np.eye(4);p[:3,:3]=np.stack((rt,up,-f),axis=1);p[:3,3]=eye
    return p
p=pyrender.Scene.from_trimesh_scene(check,bg_color=[.013,.019,.029,1],
                                    ambient_light=[.22,.22,.24])
for pos,color,power in [((0,-13,15),(.96,.75,.61),370),
                        ((-18,2,13),(.48,.65,.91),170),
                        ((18,7,1),(1.,.43,.28),255),
                        ((1,2,-6),(.50,.61,1.),135)]:
    pose=np.eye(4);pose[:3,3]=pos
    p.add(pyrender.PointLight(color=np.asarray(color),intensity=power),pose=pose)
r=pyrender.OffscreenRenderer(1320,690)
def snap(eye,target,fov):
    c=p.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)),pose=look(eye,target))
    px,_=r.render(p,flags=pyrender.RenderFlags.RGBA)
    p.remove_node(c)
    return Image.fromarray(px,'RGBA').convert('RGB')
overall=snap((0,-11,4),(0,14,4.3),56)
close=snap((-18,-2,6),(-10.75,14,4),38)
oblique=snap((27,-2,9),(10.75,14,3),56)
r.delete()
# Voluminous raw images aren't persisted; approval sheet is the only PNG.
for name,im in [('OVERVIEW',overall),('DETAIL',close),('ANGLE',oblique)]:
    im.save(DBG/f'REAR_BANK_{name}.jpg',quality=83)

W,H=1920,1320
board=Image.new('RGB',(W,H),(13,19,31));d=ImageDraw.Draw(board)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',29)
    label=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
except OSError:title=label=small=ImageFont.load_default()

def panel(image,x,y,w,h,caption):
    d.rectangle((x,y,x+w,y+h),fill=(19,26,39),outline=(69,82,107),width=2)
    frame=ImageOps.contain(image,(w-4,h-4),Image.Resampling.LANCZOS)
    board.paste(frame,(x+(w-frame.width)//2,y+(h-frame.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(69,82,107),width=2)
    d.text((x+13,y+12),caption,font=label,fill=(243,243,248),
           stroke_width=1,stroke_fill=(6,9,18))

d.text((38,18),'MODEL 04  /  ARKA REAKTÖR SERVİS IZGARALARI',font=title,fill=(240,245,253))
d.text((38,63),'Referanstaki çift üçlü uzun ızgara + üst menfezler  •  derin, açık ağızlı çelik taşıyıcı  •  merkez kesintisiz açık',
       font=label,fill=(174,193,216))
panel(overall,38,102,1240,555,'GERÇEK GLB RENDERİ / ön görünüm, iki ayrı bank')
ref=Image.open(ROOT/'uploads/image-3.png').convert('RGB')
# The reference is visibly separate from the model renders (not composited).
ref=ref.crop((195,40,693,385))
panel(ref,1303,102,576,555,'YÜKLEDİĞİN REFERANS / arka duvar')
panel(close,38,689,902,548,'GERÇEK GLB RENDERİ / üç oluk yakından')
panel(oblique,968,689,911,548,'GERÇEK GLB RENDERİ / yan açı, oyuk derinliği')
d.text((38,1263),f'GLB {GLB.stat().st_size/1e6:.2f} MB   •   {len(check.geometry)} adlandırılmış mesh   •   {tris:,} üçgen   •   sadece bu iki bank/üst ızgaralar modellenmiştir; oda kabuğu henüz yok.',
       font=small,fill=(163,185,211))
PRE=OUT/'REACTOR_REAR_SERVICE_GRILLES_01_ONAY.png';board.save(PRE,optimize=True)
print('EXPORT',GLB,GLB.stat().st_size,'bytes',len(check.geometry),'meshes',tris,'triangles',check.bounds)
print('PREVIEW',PRE,PRE.stat().st_size,'bytes')
