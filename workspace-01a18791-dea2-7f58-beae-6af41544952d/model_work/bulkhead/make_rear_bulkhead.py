#!/usr/bin/env python3
"""Model 05: modular containment rear bulkhead around approved grille banks.

The previous wooden-looking chamber shell was rejected and is not loaded here.
This is only a NEW rear bulkhead, not the complete reactor room. True through
apertures receive the two approved vent-bank models; the spaces do not contain
an invisible opaque backing plane. Steel panels are distinct mesh nodes so
damage transitions can replace selected pieces later, not baked stage props.

Coordinate convention: X left/right, Y depth (camera -Y), Z up; bulkhead is
near Y=15.3. Dimensions are a reference-guided proportion, not hidden original
schematics. Ref: uploads/image-3.png, image-7.png, image-8.png.
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

def flake(rgb,seed,size=512):
    rng=np.random.default_rng(seed)
    co=np.array(Image.fromarray(rng.integers(0,256,(60,60),dtype=np.uint8),'L').resize((size,size),Image.Resampling.BICUBIC),dtype=float)-128
    mid=np.array(Image.fromarray(rng.integers(0,256,(190,190),dtype=np.uint8),'L').resize((size,size),Image.Resampling.BILINEAR),dtype=float)-128
    fine=rng.standard_normal((size,size))
    a=np.empty((size,size,3),dtype=float);a[:]=rgb
    # Fine, isotropic metal finish. Large rusty flakes looked like plywood at
    # this camera distance, so the paint wear is deliberately restrained.
    a+=(co*.025+mid*.012+fine*1.0)[:,:,None]*np.array((1.05,.9,.8))
    chips=rng.random((size,size))<.0007;a[chips]-=rng.uniform(4,12,chips.sum())[:,None]
    return Image.fromarray(np.uint8(np.clip(a,1,255)),'RGB')

def mat(name,rgb,met=.68,rough=.59,tex=None,emit=(0,0,0)):
    return trimesh.visual.material.PBRMaterial(name=name,
       baseColorFactor=[*((255,255,255) if tex else rgb),255],
       baseColorTexture=tex,metallicFactor=met,roughnessFactor=rough,
       emissiveFactor=emit,doubleSided=True)
# ONE consistent neutral steel across all sheet panels. The reactor's orange
# cast comes from its scene illumination, not a permanently brown wood-look
# material or an abrupt pasted-on center/lower color block.
STEEL_TEX=flake((92,102,112),91)
SHEET=mat('01 Continuous brushed containment alloy',(255,255,255),.80,.49,STEEL_TEX)
M={
 'warm':SHEET,
 'upper':SHEET,
 'lower':SHEET,
 'shadow':mat('04 Reinforced graphite gunmetal',(52,61,73),.75,.58),
 'rib':mat('05 Beveled structural iron',(78,90,99),.79,.47),
 'machined':mat('06 Polished steel tooth edges',(137,147,150),.81,.39),
 'gasket':mat('07 Compression seals',(13,17,22),.18,.88),
 'amber':mat('08 Orange refractory warning inlay',(196,102,52),.39,.60),
 'signal':mat('09 Narrow red service indicator',(132,46,37),.32,.54),
 'ceramic':mat('10 Blue-violet cooled steel on lower flange',(44,51,81),.63,.54),
}
BUCKET={}
def add(zone,kind,mesh,uv=None):
    if uv is None:
        v=mesh.vertices;uv=np.stack((v[:,0]*.094,v[:,2]*.078),axis=1)
    BUCKET.setdefault((zone,kind),[]).append((mesh.vertices,mesh.faces,uv))

def poly_plate(p,zone,kind):
    """Bevelled *solid metal plate* extruded normal to XZ, not a flat decal."""
    p=np.asarray(p,float);n=len(p);c=p.mean(axis=0)
    outer=p+(c-p)*.006     # small real seam to next piece
    inner=p+(c-p)*.047     # pressed-steel bevel width
    verts=[(x,15.67,z) for x,z in outer]
    verts+= [(x,15.26,z) for x,z in outer]
    verts+= [(x,14.97,z) for x,z in inner]
    faces=[]
    # back face and 2-ring front shoulder. The front is one convex polygon.
    for i in range(1,n-1):
        faces.append((0,i+1,i))
        faces.append((2*n,2*n+i,2*n+i+1))
    for i in range(n):
        j=(i+1)%n
        faces.extend(((i,j,n+j),(i,n+j,n+i),
                      (n+i,n+j,2*n+j),(n+i,2*n+j,2*n+i)))
    g=trimesh.Trimesh(vertices=np.asarray(verts),faces=np.asarray(faces),process=False)
    add(zone,kind,g)

def quad_rect(x1,x2,z1,z2,zone,kind):
    poly_plate([(x1,z1),(x2,z1),(x2,z2),(x1,z2)],zone,kind)

def block(cx,cy,cz,sx,sy,sz,zone,kind):
    g=trimesh.creation.box(extents=(sx,sy,sz));g.apply_translation((cx,cy,cz));add(zone,kind,g)

def tube(a,b,r,zone,kind,sections=8):
    a=np.asarray(a,float);b=np.asarray(b,float);u=b-a;n=np.linalg.norm(u)
    if n<1e-4:return
    g=trimesh.creation.cylinder(radius=r,height=n,sections=sections)
    g.apply_transform(trimesh.geometry.align_vectors((0,0,1),u/n))
    g.apply_translation((a+b)*.5);add(zone,kind,g)

def fasten(x,z,zone):
    g=trimesh.creation.cylinder(radius=.105,height=.11,sections=6)
    g.apply_transform(trimesh.geometry.align_vectors((0,0,1),(0,-1,0)))
    g.apply_translation((x,15.02,z));add(zone,'machined',g)
    tube((x-.043,14.955,z),(x+.043,14.955,z),.011,zone,'gasket',sections=6)

# TWO exact-sized holes, one for each *already approved* bank:
# -16.14..-5.36 and 5.36..16.14, Z=-7.18..17.16; no roof panels fill them.
# Center wall is BEHIND the star, never a shutter in front of the core.
# A SINGLE continuous-width core sheet rises from bottom to roof between the
# paired openings. The old version's six colored central squares were a fake
# looking afterthought. Here all surrounding steel shares the exact same PBR
# alloy and changes only at *real mechanical mounting edges*.
quad_rect(-5.35,5.35,-21.50,21.50,'CONTINUOUS_CENTER_WEBS','warm')
for i,(a,b) in enumerate([(-16.16,-5.35),(5.35,16.16)]):
    quad_rect(a,b,17.17,21.5,f'UPPER_FASCIA_{i+1}','upper')
    block((a+b)/2,15.04,17.35,b-a-.16,.16,.12,'UPPER_EAVE','rib')
# Below the cutouts are long roll-formed lower sheets; seams run directly
# beneath the centers of the grille banks, not randomly across the middle.
for ix,(a,b) in enumerate([(-16.16,-10.75),(-10.75,-5.35),
                            (5.35,10.75),(10.75,16.16)]):
    quad_rect(a,b,-21.50,-7.16,f'LOWER_BULKHEAD_{ix+1}','lower')
# Each outer wing is one continuous bent steel field, rather than 3 abrupt
# horizontally color-blocked rectangles. Side emitter ports are on later
# perpendicular walls, not these rear-wing fields.
for side in (-1,1):
    suffix='LEFT' if side<0 else 'RIGHT'
    lo,hi=(-24.5,-16.16) if side<0 else (16.16,24.5)
    quad_rect(lo,hi,-12.50,12.50,f'WING_{suffix}','warm')
    # Slanted octagonal upper/lower shoulders, integral in profile and metal.
    if side>0:
        top=[(16.16,12.5),(24.5,12.5),(17,21.5),(16.16,21.5)]
        bot=[(16.16,-21.5),(17,-21.5),(24.5,-12.5),(16.16,-12.5)]
    else:
        top=[(-24.5,12.5),(-16.16,12.5),(-16.16,21.5),(-17,21.5)]
        bot=[(-17,-21.5),(-16.16,-21.5),(-16.16,-12.5),(-24.5,-12.5)]
    poly_plate(top,f'UPPER_CHAMFER_{suffix}','upper')
    poly_plate(bot,f'LOWER_CHAMFER_{suffix}','lower')
    # Noisy wall-paint-free perimeter structural spine and amber danger rail.
    x=side*23.85
    tube((x,15.01,-11.0),(x,15.01,11.2),.12,f'WING_RIB_{suffix}','rib',10)
    block(side*20.85,15.01,3.5,.39,.26,14.2,f'SIGNAL_PYLON_{suffix}','rib')
    block(side*20.85,14.83,5.2,.19,.09,8.6,f'SIGNAL_PYLON_{suffix}','signal')
    for z in (-3.2,10.6):
        block(side*20.85,14.74,z,.55,.19,.31,f'SIGNAL_PYLON_{suffix}','machined')
    for z in (-11.7,11.9):
        block(side*23.8,14.99,z,.65,.39,.27,f'WING_RIB_{suffix}','shadow')

# The actual openings get a rim that meets approved grille-bank extents. It
# doesn't place a pane behind their dark duct throats, so a future service
# facility behind the wall is mechanically possible.
for side in (-1,1):
    c=side*10.75;suf='L' if side<0 else 'R'
    x1,x2=c-5.40,c+5.40;z1,z2=-7.20,17.18
    for x in (x1,x2):
        block(x,15.20,(z1+z2)/2,.28,.60,z2-z1+.50,f'BANK_SOCKET_{suf}','shadow')
        block(x,14.88,(z1+z2)/2,.083,.09,z2-z1+.04,f'BANK_SOCKET_{suf}','machined')
        for z in np.linspace(z1+.6,z2-.6,8):fasten(x,z,f'BANK_FASTENERS_{suf}')
    for z in (z1,z2):
        block(c,15.20,z,x2-x1+.4,.60,.29,f'BANK_SOCKET_{suf}','shadow')
        block(c,14.88,z,x2-x1+.22,.09,.08,f'BANK_SOCKET_{suf}','machined')
        for x in np.linspace(x1+.8,x2-.8,7):fasten(x,z,f'BANK_FASTENERS_{suf}')
# Segmented low hazard line beneath the ventilation banks (reference feature).
block(0,14.96,-8.43,32.0,.16,.22,'REAR_HAZARD_RAIL','gasket')
for i in range(-19,20):
    x=i*.79
    if abs(x)>15.6:continue
    # Slanted seam-distinct ceramic tabs, not a single painted hazard rectangle.
    tube((x-.23,14.84,-8.48),(x+.10,14.84,-8.30),.056,
         'REAR_HAZARD_TABS','amber',sections=5)
# Functional pressed-steel stringers, not extra randomly-placed blocks.
# They project from the sheet and terminate at precisely the panel seams.
for z in (-15.48,-11.97):
    block(0,14.92,z,31.95,.30,.16,'LOWER_STIFFENERS','rib')
    block(0,14.74,z+.085,31.65,.09,.047,'LOWER_STIFFENERS','machined')
    for x in np.arange(-14.4,14.5,4.8):fasten(float(x),z,'STIFFENER_FASTENERS')
# Base and roof eave channels provide actual junctions for *future* separately
# approved ceiling/floor modules. The ceiling/floor do not exist in this GLB.
for z in (-21.35,17.34,21.40):
    tube((-15.9,14.93,z),(15.9,14.93,z),.093,'BULKHEAD_RACEWAYS','rib',8)
for side in (-1,1):
    s='L' if side<0 else 'R'
    # Exposed rolled beam along the octagonal shoulder, distinct from the
    # metal cladding. Restrained in color; not a decorative bright neon bar.
    for z1,z2,x1,x2 in [(21.35,12.72,16.97,24.29),(-21.35,-12.72,16.97,24.29)]:
        tube((side*x1,14.90,z1),(side*x2,14.90,z2),.099,
             'ANGLED_SHOULDER_'+s,'rib',9)
        for tt in (.25,.72):
            fasten(side*(x1+(x2-x1)*tt),z1+(z2-z1)*tt,
                   'ANGLED_SHOULDER_'+s)
    for z in (-15.8,-11.5,-8.0,18.2,20.4):
        for x in (side*8.3,side*14.8):fasten(x,z,'PANEL_FASTENERS')

world=trimesh.Scene();tri=0
for (zone,kind),parts in BUCKET.items():
    vs=[];fs=[];us=[];shift=0
    for v,f,u in parts:
        vs.append(v);fs.append(f+shift);us.append(u);shift+=len(v)
    g=trimesh.Trimesh(vertices=np.concatenate(vs),faces=np.concatenate(fs),process=False)
    g.visual=trimesh.visual.texture.TextureVisuals(uv=np.concatenate(us),material=M[kind])
    world.add_geometry(g,geom_name=f'{zone}__{kind}')
    tri+=len(g.faces)
GLB=OUT/'REACTOR_REAR_BULKHEAD_STEEL_REV02.glb'
GLB.write_bytes(world.export(file_type='glb'))
reloaded=trimesh.load(GLB,force='scene')
assert len(reloaded.geometry)==len(world.geometry)
assert tri==sum(len(m.faces) for m in reloaded.geometry.values())
# center of both banks must be empty in the exported rear-wall mesh.
def blocked_in_xz(x,z):
    # Bounding boxes of merged rim meshes include the empty *middle*, so test
    # triangle projections, not a whole named node's bounding box.
    P=np.asarray((x,z),float)
    for g in reloaded.geometry.values():
        t=g.vertices[g.faces][:,:,[0,2]]
        a,b,c=t[:,0],t[:,1],t[:,2]
        v=b-a;w=c-a;q=P-a
        cross=lambda u,v:u[:,0]*v[:,1]-u[:,1]*v[:,0]
        det=cross(v,w);mask=np.abs(det)>1e-7
        sign=np.where(det>=0,1.,-1.)
        d=np.where(mask,det,1.)
        u=cross(q,w)*sign/d*sign
        v2=cross(v,q)*sign/d*sign
        if np.any(mask&(u>1e-5)&(v2>1e-5)&(u+v2<1-1e-5)):
            return True
    return False
for center_x in (-10.75,10.75):
    for dx in (-3.0,0.0,3.0):
        for z in (-5.0,3.0,15.0):
            assert not blocked_in_xz(center_x+dx,z),'blocked bank aperture'

bank=trimesh.load(OUT/'REACTOR_REAR_SERVICE_GRILLES_01.glb',force='scene')
context=trimesh.Scene()
for k,g in reloaded.geometry.items():context.add_geometry(g,geom_name='WALL_'+k)
for k,g in bank.geometry.items():context.add_geometry(g,geom_name='APPROVED_BANK_'+k)

def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    rt=np.cross(f,(0,0,1.));rt/=np.linalg.norm(rt)
    up=np.cross(rt,f)
    T=np.eye(4);T[:3,:3]=np.stack((rt,up,-f),axis=1);T[:3,3]=eye
    return T

def shot(scene,eye,target,fov,size=(1350,790)):
    p=pyrender.Scene.from_trimesh_scene(scene,bg_color=[.011,.016,.027,1],
                                        ambient_light=[.23,.22,.25])
    for pos,col,power in [((-11,-18,14),(1.0,.64,.42),430),
                          ((24,-7,7),(.45,.51,1.0),320),
                          ((0,4,-12),(.53,.62,1.),300),
                          ((-21,1,9),(1.,.39,.28),130)]:
        T=np.eye(4);T[:3,3]=pos
        p.add(pyrender.PointLight(color=np.asarray(col),intensity=power),pose=T)
    p.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)),pose=look(eye,target))
    r=pyrender.OffscreenRenderer(*size)
    a,_=r.render(p,flags=pyrender.RenderFlags.RGBA)
    r.delete()
    return Image.fromarray(a,'RGBA').convert('RGB')
front=shot(context,(0,-27,5),(0,15,0),58)
solo=shot(reloaded,(0,-27,5),(0,15,0),58)
# Tight crop only on the independent wall's panel; the actual GLB itself is
# unchanged. This makes the two through-holes legible rather than tiny.
solo=solo.crop((229,0,1121,790))
detail=shot(context,(12,-6,5),(10.7,15,6),61)
angle=shot(context,(-28,-13,14),(-4.5,15,1),63)
for name,im in [('FRONT',front),('SOLO',solo),('DETAIL',detail),('ANGLE',angle)]:
    im.save(DBG/f'REAR_BULKHEAD_{name}.jpg',quality=85)

board=Image.new('RGB',(1920,1400),(13,18,30));d=ImageDraw.Draw(board)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',30)
    label=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
except OSError:title=label=small=ImageFont.load_default()

def panel(im,x,y,w,h,s):
    d.rectangle((x,y,x+w,y+h),fill=(19,26,39),outline=(69,82,107),width=2)
    v=ImageOps.contain(im,(w-4,h-4),Image.Resampling.LANCZOS)
    board.paste(v,(x+(w-v.width)//2,y+(h-v.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(69,82,107),width=2)
    d.text((x+14,y+14),s,font=label,fill=(245,247,253),
           stroke_width=1,stroke_fill=(10,13,19))
d.text((38,20),'MODEL 05 REV02  /  SÜREKLİ ÇELİK ARKA ZIRHI',font=title,fill=(244,246,253))
d.text((38,65),'Tek tip nötr metal; orta parça boydan boya devam eder  •  onaylı ızgaralar için iki GERÇEK geçit  •  yan/tavan/zemin kabuğu henüz yok',
       font=label,fill=(175,194,216))
panel(front,38,107,1215,613,'BAĞLAM / yeni duvar + önce ONAYLANAN ızgaralar (çevrimdışı GLB)')
panel(solo,1277,107,604,613,'YALNIZ YENİ DUVAR / iki açık yuva')
panel(detail,38,752,900,572,'YAKIN / modül yuvası, çelik plaka ve bağlantı')
panel(angle,963,752,918,572,'YAN AÇI / arka duvar profili, parça derinliği')
d.text((38,1360),f'Yeni GLB {GLB.stat().st_size/1e6:.2f} MB  •  {len(reloaded.geometry)} bağımsız mesh  •  {tri:,} üçgen  •  render Studio değil; önceki ızgara yalnız bağlam panelinde.',
       font=small,fill=(160,184,212))
PRE=OUT/'REACTOR_REAR_BULKHEAD_STEEL_REV02_ONAY.png';board.save(PRE,optimize=True)
print('EXPORT',GLB,GLB.stat().st_size,'bytes',len(reloaded.geometry),'meshes',tri,'tris')
print('PREVIEW',PRE,PRE.stat().st_size,'bytes')
