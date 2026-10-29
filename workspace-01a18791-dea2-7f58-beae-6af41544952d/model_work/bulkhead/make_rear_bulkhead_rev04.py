#!/usr/bin/env python3
"""Reactor rear wall Rev04 — coherent segmented BROWN IRON around two vents.

Lessons from rejected Rev01-03: no wood-colored large paint rectangles;
not a grey generic slab; not a polished chocolate single panel. This is
several globally aligned, weathered rolled-iron courses sitting on one
watertight liner, and a *gradual chamfered steel socket* from the wall into
each approved three-slot grille. Every course shares ONE world-mapped
material/texture; no sudden switch or central applique is possible.
Reference: image-3 / image-7; low-res reference can't reveal inner machinery.
The previously approved grille GLB is NOT edited or moved. The new sheet
pressing accommodates its existing shallow upper and deeper lower geometry.
No Studio integration, audio test, gameplay test or live physics is implied.
"""
from __future__ import annotations
import os,sys,math,argparse
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
os.environ['PYOPENGL_PLATFORM']='egl'
sys.path[:0]=['/home/user/.cache/modeldeps','/home/user/.cache/modelrender']
import trimesh,pyrender
ROOT=Path('/home/user');PERSIST=ROOT/'model_exports'
args=argparse.ArgumentParser();args.add_argument('--release',action='store_true');opts=args.parse_args()
OUT=PERSIST if opts.release else ROOT/'.cache/bulkhead_rev04_candidate'
OUT.mkdir(parents=True,exist_ok=True)
DBG=ROOT/'.cache/model_debug';DBG.mkdir(parents=True,exist_ok=True)

# World-aligned PBR texture. Brown oxide is interleaved with patches of exposed
# cold steel. Per-pixel glTF G=roughness and B=metalness vary *together* with
# the oxidation. This is matte/rough rusted iron, NOT smooth chocolate and NOT
# brown woodgrain. All four plate courses sample the same continuous image.
rng=np.random.default_rng(91919);W=H=1024
co=np.asarray(Image.fromarray(rng.integers(0,256,(43,43),dtype=np.uint8),'L').resize((W,H),Image.Resampling.BICUBIC),float)-128
mid=np.asarray(Image.fromarray(rng.integers(0,256,(210,210),dtype=np.uint8),'L').resize((W,H),Image.Resampling.BILINEAR),float)-128
speck=rng.standard_normal((H,W))*3.1
field=co*.63+mid*.26
# Oxidation lives mostly in *small* pits, not large camouflage patches.
# Low-frequency brown drift is only 4%; short wavelength wear is the texture.
oxid=.64+.035*np.tanh((co+8)/34)+.093*np.tanh(mid/32)
oxid=np.clip(oxid,.51,.75)
img=oxid[:,:,None]*np.array((153.,94.,59.))+(1-oxid)[:,:,None]*np.array((90.,101.,110.))
# The subtle warm roof / cooler foot modulation is continuous for all panels.
grad=np.linspace(1,-1,H)[:,None,None]
img+=grad*np.array((8.,4.,-1.))[None,None,:]
img+=speck[:,:,None]
pits=rng.random((H,W))<.010;img[pits]-=rng.uniform(5,24,pits.sum())[:,None]
texture=Image.fromarray(np.uint8(np.clip(img,3,250)),'RGB')
# Tangent-space *micro* pitting, far smaller than the panel seams; unlike a
# gloss effect it survives when the sheet is seen without meltdown lighting.
height=mid*.27+speck*.75
hgy,hgx=np.gradient(height)
nx=-hgx*.025;ny=-hgy*.025;nz=np.ones((H,W))
norm=np.sqrt(nx*nx+ny*ny+nz*nz)
normal=np.stack((nx/norm,ny/norm,nz/norm),axis=2)
NORMAL=Image.fromarray(np.uint8(np.clip((normal*.5+.5)*255,0,255)),'RGB')
# glTF metallic-roughness: R unused, G perceptual roughness, B metalness.
mr=np.empty((H,W,3),dtype=np.uint8)
mr[:,:,0]=255
mr[:,:,1]=np.uint8(np.clip((.46+.34*oxid+np.maximum(speck,0)*.003)*255,1,255))
mr[:,:,2]=np.uint8(np.clip((.93-.59*oxid)*255,1,255))
METAL_ROUGH=Image.fromarray(mr,'RGB')

def mat(name,rgb,met=.57,rough=.70,tex=None,mr=None,norm=None):
    return trimesh.visual.material.PBRMaterial(name=name,
      baseColorFactor=[*((255,255,255) if tex is not None else rgb),255],
      baseColorTexture=tex,metallicFactor=met,roughnessFactor=rough,
      metallicRoughnessTexture=mr,normalTexture=norm,doubleSided=True)
M={
 'iron':mat('01 Continuously oxidized BROWN IRON with exposed cold steel',None,1.0,1.0,texture,METAL_ROUGH,NORMAL),
 'lining':mat('02 Darker welded liner brown iron',(82,66,59),.57,.78),
 'cut':mat('03 Exposed pale bare-metal plate edges',(125,133,136),.85,.42),
 'rib':mat('04 Forged dark support iron',(52,57,61),.79,.55),
 'oxide':mat('05 Heat-darkened weld metal',(105,65,51),.75,.57),
 'orange':mat('06 Warning enamel on separate small ceramic tabs',(190,93,45),.37,.65),
}
BUCKET={}
def add(zone,kind,mesh):
    v=mesh.vertices
    uv=np.stack(((v[:,0]+25)/50,(v[:,2]+22)/44),axis=1)
    BUCKET.setdefault((zone,kind),[]).append((v,mesh.faces,uv))
def bar(a,b,r,zone,kind,sections=8):
    a=np.asarray(a,float);b=np.asarray(b,float);d=b-a;L=np.linalg.norm(d)
    if L<1e-4:return
    g=trimesh.creation.cylinder(radius=r,height=L,sections=sections)
    g.apply_transform(trimesh.geometry.align_vectors((0,0,1),d/L))
    g.apply_translation((a+b)*.5);add(zone,kind,g)
def box(x,y,z,sx,sy,sz,zone,kind):
    g=trimesh.creation.box(extents=(sx,sy,sz));g.apply_translation((x,y,z));add(zone,kind,g)
def raised_quad(points,zone,kind,depth=.13):
    p=np.asarray(points,float);p[:,1]+=[bend_y(x) for x in p[:,0]]
    vs=np.vstack((p,p+np.array((0,depth,0))))
    fs=[(0,1,2),(0,2,3),(4,6,5),(4,7,6)]
    for i in range(4):
        j=(i+1)%4
        fs+= [(i,j,j+4),(i,j+4,i+4)]
    add(zone,kind,trimesh.Trimesh(vertices=vs,faces=fs,process=False))

def nut(x,y,z,zone):
    g=trimesh.creation.cylinder(radius=.072,height=.075,sections=6)
    g.apply_transform(trimesh.geometry.align_vectors((0,0,1),(0,-1,0)))
    g.apply_translation((x,y,z));add(zone,'cut',g)

# One outer octagonal contour and TWO approved vent-bank openings.
outer=[(-17.,-21.5),(17.,-21.5),(24.5,-12.5),(24.5,12.5),
       (17.,21.5),(-17.,21.5),(-24.5,12.5),(-24.5,-12.5)]
def bend_y(x):
    """Rear steel bends forward into future side walls, avoiding a flat prop."""
    t=np.clip((abs(x)-16.14)/(24.5-16.14),0,1)
    return -2.55*t*t*(3-2*t)
def aperture_weight(x,z):
    """Cubic curve shaping *the wall itself* into the approved bank opening."""
    distance=1e6
    for c in (-10.75,10.75):
        lo,hi=c-5.36,c+5.36
        dx=max(lo-x,0.,x-hi)
        dz=max(-7.18-z,0.,z-17.18)
        distance=min(distance,math.hypot(dx,dz))
    t=np.clip(1.-distance/1.65,0,1)
    return t*t*(3-2*t)

def wall_y(x,z):
    # The approved bank's lower slots project farther into the room than its
    # upper little vents. A Z-continuous pressing follows that original shape:
    # deep below, shallow at the top, *without translating* the approved GLB.
    q=np.clip((z-9.)/4.5,0,1);q=q*q*(3-2*q)
    depth=1.50*(1-q)+.12*q
    return bend_y(x)-depth*aperture_weight(x,z)
# Subcuts shape a smooth 1.65-stud roll into openings; no exposed vertical
# patch mesh on the border. The holes remain the exact approved dimensions.
xcuts=[-24.5,-17.74,-17.34,-17.,-16.74,-16.44,-16.14,
       -5.36,-5.06,-4.76,-4.36,-3.96,-3.76,0.,
       3.76,3.96,4.36,4.76,5.06,5.36,
       16.14,16.44,16.74,17.,17.34,17.74,24.5]
zcuts=[-21.5,-12.5,-8.78,-8.38,-7.98,-7.78,-7.48,-7.18,-2.0,8.5,
       9.5,11.0,12.5,13.5,17.18,17.48,17.78,18.18,18.78,21.5]
bands=[-21.5,-12.5,-2.0,8.5,21.5]

def clip(poly,a,b):
    def signed(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    out=[]
    for s,e in zip(poly,poly[1:]+poly[:1]):
        ds,de=signed(s),signed(e)
        ins,ine=ds>=-1e-9,de>=-1e-9
        if ins!=ine:
            q=ds/(ds-de);out.append((s[0]+(e[0]-s[0])*q,s[1]+(e[1]-s[1])*q))
        if ine:out.append(e)
    return out

def clip_to_octagon(poly):
    for a,b in zip(outer,outer[1:]+outer[:1]):
        if not poly:break
        poly=clip(poly,a,b)
    out=[]
    for q in poly:
        if not out or math.dist(q,out[-1])>1e-6:out.append(q)
    if len(out)>1 and math.dist(out[0],out[-1])<1e-6:out.pop()
    return out

def cells():
    for i in range(len(xcuts)-1):
        x1,x2=xcuts[i],xcuts[i+1]
        for j in range(len(zcuts)-1):
            z1,z2=zcuts[j],zcuts[j+1]
            hole=((x1>=5.36-1e-6 and x2<=16.14+1e-6) or
                  (x1>=-16.14-1e-6 and x2<=-5.36+1e-6)) and z1>=-7.18-1e-6 and z2<=17.18+1e-6
            if not hole:yield x1,x2,z1,z2

def extruded_cells(items,front_y,back_y,liner=False):
    verts=[];fidx={};bidx={};face=[]
    def get(x,z,which):
        key=(round(float(x),6),round(float(z),6))
        cache=fidx if which==0 else bidx
        if key not in cache:
            cache[key]=len(verts)
            y=(front_y if which==0 else back_y)+wall_y(*key)
            if liner and which==0:y-=.35*aperture_weight(*key)
            verts.append((key[0],y,key[1]))
        return cache[key]
    for poly in items:
        if len(poly)<3:continue
        a=[get(x,z,0) for x,z in poly]
        b=[get(x,z,1) for x,z in poly]
        for j in range(1,len(poly)-1):
            face.append((a[0],a[j],a[j+1]))
            face.append((b[0],b[j+1],b[j]))
    edges={}
    for a,b,c in face[::2]:
        for u,v in ((a,b),(b,c),(c,a)):
            k=(min(u,v),max(u,v));edges.setdefault(k,[]).append((u,v))
    back_of={fidx[k]:bidx[k] for k in fidx}
    for key,uses in edges.items():
        if len(uses)!=1:continue
        a,b=uses[0];A=back_of[a];B=back_of[b]
        face.extend(((a,b,B),(a,B,A)))
    m=trimesh.Trimesh(vertices=np.asarray(verts),faces=np.asarray(face),process=False)
    m.remove_unreferenced_vertices()
    return m

# Load-bearing backing spans the entire field, without an inserted central
# patch. Through-holes remain open through the y-thickness.
liner_polys=[]
for x1,x2,z1,z2 in cells():
    q=clip_to_octagon([(x1,z1),(x2,z1),(x2,z2),(x1,z2)])
    if len(q)>=3:liner_polys.append(q)
liner=extruded_cells(liner_polys,15.48,16.12,liner=True)
assert liner.is_watertight and liner.euler_number==-2,(liner.is_watertight,liner.euler_number)
add('REAR_LOAD_BEARING_LINER','lining',liner)

# Four cross-chamber courses, NEVER individually drawn center rectangles.
# Their seams have the exact same world Z throughout the wall; the open banks
# simply interrupt the physical sheet. A single global UV texture continues
# from one panel to the next (no independent coloring per panel).
course_polys=[[] for _ in range(4)]
for x1,x2,z1,z2 in cells():
    mid=(z1+z2)/2
    band=next(i for i in range(4) if bands[i]-1e-6<=mid<=bands[i+1]+1e-6)
    margin=.066
    lo=z1+(margin if abs(z1-bands[band])<1e-5 and z1>bands[0] else 0)
    hi=z2-(margin if abs(z2-bands[band+1])<1e-5 and z2<bands[-1] else 0)
    q=clip_to_octagon([(x1,lo),(x2,lo),(x2,hi),(x1,hi)])
    if len(q)>=3:course_polys[band].append(q)
for i,polys in enumerate(course_polys):
    p=extruded_cells(polys,15.13,15.40)
    assert p.is_watertight,(i,p.euler_number)
    add(f'ROLLED_IRON_COURSE_{i+1}','iron',p)
# Welds follow a COURSE seam at one global Z, in the same restrained brown
# metal everywhere. Where a grille occupies the wall the weld naturally stops;
# no stroke appears out of nowhere exclusively around the middle section.
for z in bands[1:-1]:
    spans=[(-23.8,23.8)] if z<-7.18 else [(-23.8,-16.35),(-5.10,5.10),(16.35,23.8)]
    for lo,hi in spans:
        for x0,x1 in zip(np.linspace(lo,hi,9)[:-1],np.linspace(lo,hi,9)[1:]):
            bar((x0,15.17+bend_y(x0),z),(x1,15.17+bend_y(x1),z),
                .023,'STAMPED_COURSE_WELDS','oxide',sections=6)
    if z<-7.18:
        for x in (-14.,-7.,0.,7.,14.):nut(x,15.05,z,'SEAM_FASTENERS')
    else:
        for x in (-21.,0.,21.):nut(x,15.05+bend_y(x),z,'SEAM_FASTENERS')
# Side corner is folded sheet metal, with an actual rolled hinge rather than
# an abrupt color seam between the rear and the future perpendicular wall.
for sgn in (-1,1):
    x=sgn*17.0
    bar((x,15.04+bend_y(x),-12.45),(x,15.04+bend_y(x),12.45),.067,
        'OCTAGON_WING_FOLD','cut',sections=8)

# No grafted cheeks or mid-wall cover strips. The separate APPROVED banks are
# kept at their authentic existing coordinates and the metal sheet courses
# themselves follow the lower-mouth versus high-vent projection continuously.

# Forged perimeter follows outer octagon; sparse industrial service indicators
# appear on reference side wings. No stage rays/energy are modeled here.
for a,b in zip(outer,outer[1:]+outer[:1]):
    bar((a[0],15.03+bend_y(a[0]),a[1]),
        (b[0],15.03+bend_y(b[0]),b[1]),.096,'BENT_EDGE_IRON','rib',9)
for side in (-1,1):
    x=side*21.12;tag='L' if side<0 else 'R';bend=bend_y(x)
    box(x,15.08+bend,3.4,.30,.33,13.8,'SERVICE_MARKER_'+tag,'rib')
    box(x,14.88+bend,5.5,.115,.075,7.5,'SERVICE_MARKER_'+tag,'oxide')
    for z in (-3.3,10.3):box(x,14.76+bend,z,.53,.16,.30,'SERVICE_MARKER_'+tag,'cut')
    # Small dashed hazard cadence observed below the banks, not a new stripe
    # splitting the whole wall into bright-colored material blocks.
    for k in range(10):
        xx=side*10.75-3.97+k*.85
        bar((xx-.14,15.03,-8.07),(xx+.10,15.03,-7.94),.047,
            'REAR_SAFETY_TABS','orange',6)

world=trimesh.Scene();numfaces=0
for (zone,kind),pieces in BUCKET.items():
    vv=[];ff=[];uu=[];offset=0
    for v,f,u in pieces:
        vv.append(v);ff.append(f+offset);uu.append(u);offset+=len(v)
    g=trimesh.Trimesh(vertices=np.concatenate(vv),faces=np.concatenate(ff),process=False)
    g.visual=trimesh.visual.texture.TextureVisuals(uv=np.concatenate(uu),material=M[kind])
    world.add_geometry(g,geom_name=f'{zone}__{kind}')
    numfaces+=len(g.faces)
GLB=OUT/'REACTOR_REAR_BULKHEAD_IRON_REV04.glb';GLB.write_bytes(world.export(file_type='glb'))
reloaded=trimesh.load(GLB,force='scene')
assert len(reloaded.geometry)==len(world.geometry)
assert numfaces==sum(len(g.faces) for g in reloaded.geometry.values())
assert sum(n.startswith('ROLLED_IRON_COURSE') for n in reloaded.geometry)==4
assert reloaded.geometry['REAR_LOAD_BEARING_LINER__lining'].is_watertight

approved=trimesh.load(PERSIST/'REACTOR_REAR_SERVICE_GRILLES_01.glb',force='scene')
joined=trimesh.Scene()
for name,g in reloaded.geometry.items():joined.add_geometry(g,geom_name='NEW_WALL_'+name)
T=np.eye(4)  # approved bank coordinates unchanged
for name,g in approved.geometry.items():
    joined.add_geometry(g,geom_name='APPROVED_GRILLE_'+name,transform=T)

def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    rt=np.cross(f,(0,0,1.));rt/=np.linalg.norm(rt)
    up=np.cross(rt,f)
    a=np.eye(4);a[:3,:3]=np.stack((rt,up,-f),axis=1);a[:3,3]=eye
    return a

def render(t,eye,target,fov,lighting='work'):
    scene=pyrender.Scene.from_trimesh_scene(t,bg_color=[.013,.014,.022,1],
                                           ambient_light=[.24,.22,.22])
    cfg=[((-10,-14,14),(1.,.71,.54),410),
         ((23,-10,8),(.60,.67,.92),260),
         ((-22,-3,0),(1.,.46,.31),80),
         ((1,1,-8),(.55,.53,.68),170)]
    if lighting=='emergency':
        # Only a material relighting test. Not a powered Studio reactor state.
        cfg=[((0,-5,6),(1.,.29,.12),540),
             ((13,-4,-6),(.47,.31,.98),420),
             ((-18,-12,15),(1.,.40,.20),210)]
    for pos,col,power in cfg:
        T=np.eye(4);T[:3,3]=pos
        scene.add(pyrender.PointLight(color=np.asarray(col),intensity=power),pose=T)
    scene.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)),pose=look(eye,target))
    r=pyrender.OffscreenRenderer(1400,840)
    rgba,_=r.render(scene,flags=pyrender.RenderFlags.RGBA)
    r.delete()
    return Image.fromarray(rgba,'RGBA').convert('RGB')
front=render(joined,(0,-27,5),(0,15,0),57)
only=render(reloaded,(0,-27,5),(0,15,0),57).crop((250,0,1150,840))
close=render(joined,(3,-7,5),(0,15,4),51)
oblique=render(joined,(-26,-14,12),(-5,15,0),64)
relit=render(joined,(0,-27,5),(0,15,0),57,lighting='emergency')
for name,im in [('FRONT',front),('ONLY',only),('CLOSE',close),('OBLIQUE',oblique),('RELIT',relit)]:
    im.save(DBG/f'QA_REV04_{name}.jpg',quality=83)
# Reference remains SEPARATE from the GLB renders, never pasted into scene.
ref=Image.open(ROOT/'uploads/image-3.png').convert('RGB').crop((130,9,777,436))
board=Image.new('RGB',(1920,1680),(13,18,30));d=ImageDraw.Draw(board)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',28)
    label=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
except OSError:title=label=small=ImageFont.load_default()
def panel(im,x,y,w,h,s):
    d.rectangle((x,y,x+w,y+h),fill=(17,24,38),outline=(73,87,108),width=2)
    q=ImageOps.contain(im,(w-4,h-4),Image.Resampling.LANCZOS)
    board.paste(q,(x+(w-q.width)//2,y+(h-q.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(73,87,108),width=2)
    d.text((x+13,y+12),s,font=label,fill=(244,244,247),stroke_width=1,stroke_fill=(7,10,14))
d.text((38,22),'MODEL 05 REV04  /  PARÇALI AMA UYUMLU KAHVERENGİ DEMİR',font=title,fill=(245,248,254))
d.text((38,64),'Aynı yüzey dokusu tüm şeritlerde devam eder; ortada ayrı yama yok; menfeze geçiş eğimli metal yuva ile yapılır.',font=label,fill=(181,196,215))
panel(front,38,106,1170,576,'GERÇEK GLB BAĞLAM / yeni duvar + onaylı ızgaralar (koordinatları değişmedi)')
panel(ref,1230,106,652,576,'REFERANS / özgün görsel; aynı kare iddiası yok')
panel(only,38,715,870,575,'YALNIZ YENİ MODEL / açık yuvalar, hizalı çelik şeritler')
panel(close,934,715,948,575,'GERÇEK GLB YAKIN / sol ızgaranın SAĞ kenarı ve uyumlu duvar kıvrımı')
panel(oblique,38,1322,898,312,'YAN AÇI / bükülmüş sac ve gerçek boşluk')
panel(relit,961,1322,921,312,'AYNI GLB / yalnız kırmızı-mor ışık altında malzeme testi; Studio değil')
d.text((38,1651),f'Yeni GLB {GLB.stat().st_size/1e6:.2f} MB   •   {len(reloaded.geometry)} mesh   •   {numfaces:,} üçgen   •   Studio/ses/damage/oyun testi henüz yok.',
       font=small,fill=(161,182,208))
PRE=OUT/'REACTOR_REAR_BULKHEAD_IRON_REV04_ONAY.png';board.save(PRE,optimize=True)
print('OUTPUT',OUT,'glb',GLB.stat().st_size,'preview',PRE.stat().st_size,
      'triangles',numfaces,'meshes',len(reloaded.geometry))
print('LINER WATERTIGHT',liner.is_watertight,'EULER',liner.euler_number)
