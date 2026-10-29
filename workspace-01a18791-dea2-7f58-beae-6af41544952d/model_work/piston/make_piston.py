#!/usr/bin/env python3
"""Original telescopic hydraulic piston + vented behind-wall guide sleeve.

This is the user's explicitly requested actuator: the piston telescopes while
its attached, already approved emitter moves as ONE rigid piece (never scales).
Behind-wall mechanics are not visible in the supplied reference screenshots;
these dimensions are an engineering interpretation, NOT a claim of original
hidden geometry. Motion is offline preview; Roblox scripting follows approval.
Axis: +X projects from the reactor wall into the chamber.
"""
from __future__ import annotations
import os,sys,math,random
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
os.environ['PYOPENGL_PLATFORM']='egl'
sys.path[:0]=['/home/user/.cache/modeldeps','/home/user/.cache/modelrender']
import trimesh,pyrender
ROOT=Path('/home/user');OUT=ROOT/'model_exports';OUT.mkdir(exist_ok=True)
DBG=ROOT/'.cache/model_debug';DBG.mkdir(parents=True,exist_ok=True)
PI=math.pi;TAU=2*PI;N=48

# Procedurally painted steel and genuinely metallic rod material.
rng=np.random.default_rng(72966)
base=np.empty((512,512,3),dtype=float);base[:]=(49,57,65)
noise=rng.standard_normal((512,512))*.95
base+=noise[:,:,None]*np.array([1.,1.05,1.12])
for i in range(36):
    y=int(rng.integers(0,512));base[y,:,:]+=(1.5 if i%3 else -2.2)
STEEL_MAP=Image.fromarray(np.uint8(np.clip(base,0,255)),'RGB')

def mat(name,rgb=(255,255,255),tex=None,met=.70,rough=.46):
    return trimesh.visual.material.PBRMaterial(name=name,
      baseColorFactor=[*rgb,255],baseColorTexture=tex,
      metallicFactor=met,roughnessFactor=rough,doubleSided=True)
M={
 'housing':mat('01 - Painted industrial steel cage',tex=STEEL_MAP,met=.68,rough=.60),
 'frame':mat('02 - Oxidized dark forging',(51,58,64),met=.72,rough=.55),
 'black':mat('03 - Carbon gasket and guide race',(9,13,20),met=.25,rough=.85),
 'rod':mat('04 - Hard chrome hydraulic shaft',(159,173,180),met=.86,rough=.27),
 'neck':mat('05 - Satin telescopic stage',(104,115,122),met=.82,rough=.38),
 'bronze':mat('06 - Piston oil-bushing bronze',(151,91,54),met=.75,rough=.40),
 'bolt':mat('07 - Gunmetal torque heads',(119,129,132),met=.74,rough=.45),
 'warning':mat('08 - Dull orange pressure indicators',(177,70,35),met=.36,rough=.66),
}
BUCKET={}
def add(zone,kind,mesh):
    assert len(mesh.faces)>0
    BUCKET.setdefault((zone,kind),[]).append(mesh)

def shell(outer,inner,zone,kind,n=N):
    """True annular machined shell: a through-bore, not a solid Part cylinder."""
    contour=outer+list(reversed(inner))
    V=[];F=[]
    for x,r in contour:
        for j in range(n):
            a=TAU*j/n;V.append((x,r*math.cos(a),r*math.sin(a)))
    for k in range(len(contour)):
        t=(k+1)%len(contour)
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n;c=t*n+j;d=t*n+(j+1)%n
            F.extend(((a,b,c),(b,d,c)))
    add(zone,kind,trimesh.Trimesh(vertices=np.asarray(V),faces=np.asarray(F),process=False))

def torus_hoop(x,r,tube_r,zone,kind,segments=12):
    outer=[];inner=[]
    for k in range(segments//2+1):
        t=-PI/2+PI*k/(segments//2)
        outer.append((x+tube_r*math.sin(t),r+tube_r*math.cos(t)))
    for k in range(segments//2+1):
        t=PI/2+PI*k/(segments//2)
        inner.append((x+tube_r*math.sin(t),r+tube_r*math.cos(t)))
    # Simpler beveled annular collar is manufacturable and cheaper in Studio.
    shell([(x-.11,r-.05),(x-.04,r+tube_r),(x+.04,r+tube_r),(x+.11,r-.05)],
          [(x-.11,r-.17),(x+.11,r-.17)],zone,kind)

def rod(a,b,r,zone,kind,sections=10):
    a=np.asarray(a,float);b=np.asarray(b,float);d=b-a
    L=np.linalg.norm(d)
    if L<1e-5:return
    g=trimesh.creation.cylinder(radius=r,height=L,sections=sections)
    g.apply_transform(trimesh.geometry.align_vectors((0,0,1),d/L))
    g.apply_translation((a+b)/2);add(zone,kind,g)

def sphere(x,r,angle,zone,kind,size=.09):
    g=trimesh.creation.icosphere(radius=size,subdivisions=1)
    g.apply_translation((x,r*math.cos(angle),r*math.sin(angle)))
    add(zone,kind,g)

# REAR FIXED HYDRAULIC CYLINDER. Stroke isn't faked by scaling the emitter.
shell([(-33.80,2.52),(-33.55,2.61),(-21.33,2.61),(-20.93,2.43)],
      [(-33.80,1.42),(-20.93,1.51)],'BASE','housing')
for x in (-33.43,-32.78,-31.96,-22.0,-21.47,-21.04):
    torus_hoop(x,2.67,.11,'BASE','frame')
for i in range(8):
    a=TAU*i/8
    rod((-31.55,2.7*math.cos(a),2.7*math.sin(a)),
        (-22.21,2.7*math.cos(a),2.7*math.sin(a)),.038,'BASE','frame',sections=6)
for x in (-32.8,-21.5):
    for i in range(8):sphere(x,2.77,TAU*i/8,'BASE','bolt',size=.073)
# Oil feed flange + visible central gland around inner retracting cylinders.
shell([(-21.05,2.40),(-20.83,2.42),(-20.65,2.18)],
      [(-21.05,1.66),(-20.65,1.64)],'BASE','bronze')
torus_hoop(-20.67,1.83,.11,'BASE','black')

# STAGE1 travels +6.60; stage2 +13.20; stage3 +19.80. Their respective
# front/back axial overlaps at full extension are 2.0, 1.8 and 1.85 studs.
shell([(-29.50,1.61),(-29.27,1.68),(-20.82,1.68),(-20.62,1.57)],
      [(-29.50,1.32),(-20.62,1.29)],'STAGE1','neck')
for x in (-29.17,-20.72):torus_hoop(x,1.72,.08,'STAGE1','bronze')
shell([(-29.00,1.17),(-28.82,1.24),(-20.78,1.24),(-20.58,1.13)],
      [(-29.00,.92),(-20.58,.89)],'STAGE2','rod')
for x in (-28.78,-20.63):torus_hoop(x,1.31,.07,'STAGE2','black')
shell([(-29.00,.75),(-28.80,.81),(-20.77,.81),(-20.55,.75)],
      [(-29.00,.24),(-20.55,.24)],'STAGE3','rod')
for x in (-28.85,-20.61):torus_hoop(x,.84,.056,'STAGE3','bronze')

# Coupling moves WITH stage 3 and bears against the stationary emitter's rear
# flange. It is not a photographic overlay. Rigid transform X+19.80 takes this
# cap from -20.55 in COLD to -0.75 when the emitter back is -0.82.
shell([(-20.71,1.09),(-20.59,2.32),(-20.49,2.43),(-20.43,2.38)],
      [(-20.71,.28),(-20.43,.27)],'PUSHER','frame')
for i in range(10):
    a=TAU*i/10
    sphere(-20.48,2.31,a,'PUSHER','bolt',size=.072)
for i in range(4):
    a=TAU*(i+.5)/4
    rod((-21.05,1.02*math.cos(a),1.02*math.sin(a)),
        (-20.54,2.10*math.cos(a),2.10*math.sin(a)),
        .081,'PUSHER','neck',sections=8)

# Vented structural guide cage starts behind wall at X=-2.65, enclosing the
# emitter at COLD and centering it while it emerges. Interior radius 3.56 >
# approved emitter's maximum radius 3.07, leaving real physical clearance.
for x in (-22.70,-20.15,-16.30,-12.3,-8.3,-4.8,-2.64):
    shell([(x-.15,4.00),(x-.06,4.24),(x+.06,4.24),(x+.15,4.0)],
          [(x-.15,3.57),(x+.15,3.57)],'GUIDE_HOOPS','frame')
for k in range(8):
    a=TAU*k/8
    y,z=3.82*math.cos(a),3.82*math.sin(a)
    rod((-22.5,y,z),(-2.92,y,z),.095,'GUIDE_CAGE','housing',sections=9)
for x in (-20.15,-12.3,-4.8):
    for k in range(12):sphere(x,4.27,TAU*k/12,'GUIDE_HOOPS','bolt',size=.062)
# Symmetric 4 dark sliding surfaces - cannot collide with a 3.07-radius emitter.
for a in (PI/4,3*PI/4,5*PI/4,7*PI/4):
    rad=3.43
    rod((-21.35,rad*math.cos(a),rad*math.sin(a)),
        (-3.55,rad*math.cos(a),rad*math.sin(a)),.075,'GUIDE_INTERIOR','black',sections=7)
# Behind-wall mount and hydraulic-fluid return lines, not new reactor arms.
for x in (-30.50,-24.0,-15.5,-7.5):
    for a in (PI/4,3*PI/4,5*PI/4,7*PI/4):
        r=3.96 if x>-22 else 2.8
        rod((x,r*math.cos(a),r*math.sin(a)),
            (x-1,r*1.15*math.cos(a),r*1.15*math.sin(a)),
            .102,'BRACKETS','frame',sections=8)
for a in (PI/3,5*PI/3):
    s=math.sin(a);c=math.cos(a)
    rod((-33.17,3.04*c,3.04*s),(-22.0,3.04*c,3.04*s),
        .075,'OIL_FEED','bronze',sections=8)
for x in (-22.28,-2.67):
    for k in range(8):
        a=TAU*k/8
        sphere(x,4.18,a,'GUIDE_HOOPS','bolt',size=.075)

scene=trimesh.Scene();faces=0
for (zone,kind),pieces in BUCKET.items():
    merged=trimesh.util.concatenate(pieces)
    merged.remove_unreferenced_vertices()
    merged.visual=trimesh.visual.texture.TextureVisuals(
        uv=np.zeros((len(merged.vertices),2)),material=M[kind])
    scene.add_geometry(merged,geom_name=f'{zone}__{kind}')
    faces+=len(merged.faces)
GLB=OUT/'REACTOR_PISTON_GUIDE_01.glb';GLB.write_bytes(scene.export(file_type='glb'))

WALL=trimesh.load(OUT/'REACTOR_WALL_HATCH_THROUGH_01.glb',force='scene')
EM=trimesh.load(OUT/'REACTOR_EMITTER_REV03.glb',force='scene')

def joined(frac,door=1.):
    s=trimesh.Scene()
    for k,g in scene.geometry.items():
        T=np.eye(4)
        if k.startswith('STAGE1'):T[0,3]=6.6*frac
        if k.startswith('STAGE2'):T[0,3]=13.2*frac
        if k.startswith('STAGE3') or k.startswith('PUSHER'):T[0,3]=19.8*frac
        s.add_geometry(g,geom_name='PISTON_'+k,transform=T)
    for k,g in WALL.geometry.items():
        T=np.eye(4)
        if k.startswith('HATCH_LEFT'):T[1,3]=-5.85*door
        if k.startswith('HATCH_RIGHT'):T[1,3]=5.85*door
        s.add_geometry(g,geom_name='WALL_'+k,transform=T)
    T=np.eye(4);T[0,3]=-11.47+19.8*frac
    for k,g in EM.geometry.items():s.add_geometry(g,geom_name='EM_'+k,transform=T)
    return s

# Authentically render these real 3D meshes. The rear view shows the cylinder
# stages and guide; chamber front shows the previously approved rigid emitter.
def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    right=np.cross(f,(0,0,1.));right/=np.linalg.norm(right)
    up=np.cross(right,f)
    pose=np.eye(4);pose[:3,:3]=np.stack((right,up,-f),axis=1);pose[:3,3]=eye
    return pose

def scene_lit(t):
    pr=pyrender.Scene.from_trimesh_scene(t,bg_color=[.012,.015,.025,1],
                                       ambient_light=[.19,.20,.23])
    for pos,col,power in [((-18,-12,9),(.80,.85,1.),170),
                          ((-29,6,2),(1.,.43,.19),68),
                          ((9,-8,8),(.80,.66,.91),135),
                          ((10,5,-7),(.30,.39,.91),70)]:
        P=np.eye(4);P[:3,3]=pos
        pr.add(pyrender.PointLight(color=np.array(col),intensity=power),pose=P)
    return pr
render=pyrender.OffscreenRenderer(1300,790)
def shot(world,eye,target,fov):
    p=scene_lit(world)
    p.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)),pose=look(eye,target))
    pixels,_=render.render(p,flags=pyrender.RenderFlags.RGBA)
    return Image.fromarray(pixels,'RGBA').convert('RGB')
retracted=shot(joined(0,1),(-18,-18,9),(-16,0,0),51)
extended=shot(joined(1,1),(-18,-19,10),(-13,0,0),51)
front=shot(joined(1,1),(31,-17,7),(6,0,0),54)
mechanism=shot(scene,(-19,-15,8),(-17,0,0),52)
render.delete()
retracted.save(DBG/'PISTON_COLD_01.png')
extended.save(DBG/'PISTON_EXTENDED_01.png')
mechanism.save(DBG/'PISTON_ONLY_01.png')
front.save(DBG/'PISTON_FRONT_01.png')

board=Image.new('RGB',(1920,1370),(13,18,29));d=ImageDraw.Draw(board)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
    label=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    foot=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
except OSError:title=label=foot=ImageFont.load_default()
def panel(im,x,y,w,h,caption):
    d.rectangle((x,y,x+w,y+h),fill=(21,27,43))
    v=ImageOps.contain(im,(w,h),Image.Resampling.LANCZOS)
    board.paste(v,(x+(w-v.width)//2,y+(h-v.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(70,84,108),width=2)
    d.text((x+12,y+12),caption,font=label,fill=(245,245,250),stroke_width=1,stroke_fill=(10,14,20))
d.text((43,24),'MODEL 03B / ARKA KILAVUZ VE TELESKOPİK HİDROLİK PİSTON',font=title,fill=(242,246,253))
d.text((43,76),'Piston kademeleri açılır; yayıcının geometrisi hiç esnemez  •  arkadaki görünmeyen mühendislik özgün yorumdur',font=label,fill=(171,188,211))
panel(retracted,43,115,914,567,'ARKA 1 — COLD: piston kapalı, yayıcı içeride')
panel(extended,983,115,891,567,'ARKA 2 — piston çıktı, yayıcı ileri itildi')
panel(mechanism,43,715,919,573,'Piston modeli tek başına — delikli kafes / üç kademe')
panel(front,985,715,889,573,'Ön bakış — duvar kapakları açık, yayıcı çıktı')
d.text((43,1320),f'GLB {GLB.stat().st_size/1e6:.2f}MB  •  {faces:,} üçgen  •  {len(scene.geometry)} ayrı mesh  •  kademeler +6.6/+13.2/+19.8  •  yayıcı hep 19.8 birim tek parça gider',font=foot,fill=(169,189,211))
PRE=OUT/'REACTOR_PISTON_GUIDE_01_ONAY.png';board.save(PRE,optimize=True)
print('EXPORT',GLB,GLB.stat().st_size,'bytes',len(scene.geometry),'meshes',faces,'tris')
print('PREVIEW',PRE)
