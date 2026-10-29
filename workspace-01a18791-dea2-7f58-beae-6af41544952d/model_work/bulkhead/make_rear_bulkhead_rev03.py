#!/usr/bin/env python3
"""Reactor rear bulkhead, Rev03: one continuous, holed brown-steel shell.

User REJECTED Rev01 (wooden color, discontinuous lower/center color blocks)
and Rev02 (uniform grey rather than brown METAL, center still a grafted patch).
This is rebuilt as ONE watertight non-tiled steel shell with two actual
through-holes for the already-approved tall grilles. No visible center patch,
no abrupt lower color split, no fake filled openings or rejected old shell.
No claim of exact hidden machinery. Offline GLB preview only; not in Studio.
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

# Controlled micro-pitting on *metal*, not broad brown textured paint or
# directional woodgrain. Saturated reactor-orange comes from colored lights.
rng=np.random.default_rng(51);wh=512
noise=rng.standard_normal((wh,wh))*1.27
coarse=np.array(Image.fromarray(rng.integers(0,256,(91,91),dtype=np.uint8),'L').resize((wh,wh),Image.Resampling.BILINEAR),float)-128
tex=np.empty((wh,wh,3),float);tex[:]=(109,85,71)
tex+=(noise+coarse*.011)[:,:,None]*np.array((1.,1.,1.))
# A few tiny metallic scratches but no long parallel organic stripes.
chips=rng.random((wh,wh))<.00034;tex[chips]+=rng.uniform(-10,10,chips.sum())[:,None]
BROWN_STEEL=Image.fromarray(np.uint8(np.clip(tex,1,255)),'RGB')

def mat(name,rgb,met,rough,texture=None):
    return trimesh.visual.material.PBRMaterial(name=name,
       baseColorFactor=[*((255,255,255) if texture else rgb),255],
       baseColorTexture=texture,metallicFactor=met,roughnessFactor=rough,
       doubleSided=True)
M={
 'shell':mat('01 Brown-gunmetal homogeneous shell',None,.88,.43,BROWN_STEEL),
 'edge':mat('02 Machined smoky steel',(115,121,126),.82,.39),
 'dark':mat('03 Inset load-bearing iron',(49,57,67),.78,.57),
 'black':mat('04 True rubber compression seal',(14,16,21),.12,.85),
 'copper':mat('05 Heat-affected oxide on fasteners',(130,79,56),.73,.54),
 'warning':mat('06 Orange inspection tabs only',(191,99,48),.49,.55),
}
BUCKET={}
def add(zone,kind,g):
    v=g.vertices
    # One global UV projection, so even texture microstructure is continuous
    # across the entire shell surface. UV of side ribs is inconspicuous.
    uv=np.stack(((v[:,0]+25)/50,(v[:,2]+22)/44),axis=1)
    BUCKET.setdefault((zone,kind),[]).append((v,g.faces,uv))

def bar(a,b,r,zone,kind,sections=8):
    a=np.array(a,float);b=np.array(b,float);d=b-a;l=np.linalg.norm(d)
    if l<1e-4:return
    g=trimesh.creation.cylinder(radius=r,height=l,sections=sections)
    g.apply_transform(trimesh.geometry.align_vectors((0,0,1),d/l))
    g.apply_translation((a+b)/2);add(zone,kind,g)

def box(x,y,z,w,d,h,zone,kind):
    g=trimesh.creation.box(extents=(w,d,h));g.apply_translation((x,y,z));add(zone,kind,g)

def bolt(x,y,z,zone):
    g=trimesh.creation.cylinder(radius=.070,height=.075,sections=6)
    g.apply_transform(trimesh.geometry.align_vectors((0,0,1),(0,-1,0)))
    g.apply_translation((x,y,z));add(zone,'edge',g)

# Clip a grid cell against an EXACT octagonal outer boundary. The rectangular
# negative areas are discarded; all kept vertices are welded across cell
# boundaries. The grid is a hidden triangulation aid, NOT paneled geometry.
outer=[(-17.,-21.5),(17.,-21.5),(24.5,-12.5),(24.5,12.5),
       (17.,21.5),(-17.,21.5),(-24.5,12.5),(-24.5,-12.5)]
xcuts=[-24.5,-17.,-16.14,-5.36,5.36,16.14,17.,24.5]
zcuts=[-21.5,-12.5,-7.18,12.5,17.18,21.5]

def clip(poly,a,b):
    def cross(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    out=[]
    for s,e in zip(poly,poly[1:]+poly[:1]):
        ds,de=cross(s),cross(e)
        sin,e_in=ds>=-1e-9,de>=-1e-9
        if sin != e_in:
            t=ds/(ds-de)
            out.append((s[0]+(e[0]-s[0])*t,s[1]+(e[1]-s[1])*t))
        if e_in:out.append(e)
    return out
verts=[];front={};back={};faces=[]
def vindex(x,z,which):
    key=(round(float(x),6),round(float(z),6))
    cache=front if which=='front' else back
    if key not in cache:
        cache[key]=len(verts);verts.append((key[0],15.28 if which=='front' else 15.89,key[1]))
    return cache[key]

for i in range(len(xcuts)-1):
    x1,x2=xcuts[i],xcuts[i+1]
    for j in range(len(zcuts)-1):
        z1,z2=zcuts[j],zcuts[j+1]
        hole=((x1>=5.36-1e-6 and x2<=16.14+1e-6) or
              (x1>=-16.14-1e-6 and x2<=-5.36+1e-6)) and z1>=-7.18-1e-6 and z2<=17.18+1e-6
        if hole:continue
        poly=[(x1,z1),(x2,z1),(x2,z2),(x1,z2)]
        for a,b in zip(outer,outer[1:]+outer[:1]):
            if not poly:break
            poly=clip(poly,a,b)
        # Clip can produce duplicate collinear points at chamfer vertices.
        clean=[]
        for q in poly:
            if not clean or math.dist(q,clean[-1])>1e-6:clean.append(q)
        if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-6:clean.pop()
        if len(clean)<3:continue
        fv=[vindex(x,z,'front') for x,z in clean]
        bv=[vindex(x,z,'back') for x,z in clean]
        for k in range(1,len(clean)-1):
            faces.append((fv[0],fv[k],fv[k+1]))
            faces.append((bv[0],bv[k+1],bv[k]))

# A single physical steel sheet with sidewalls around both openings. Boundary
# extraction closes the extrusion only on truly exposed outer/hole edges.
counts={}
for a,b,c in faces[::2]:
    for u,v in ((a,b),(b,c),(c,a)):
        key=(min(u,v),max(u,v));counts.setdefault(key,[]).append((u,v))
# Front and back vertex indices are independent but share XZ keys.
back_of={front[k]:back[k] for k in front}
for uv,uses in counts.items():
    if len(uses)!=1:continue
    a,b=uses[0];A=back_of[a];B=back_of[b]
    faces.extend(((a,b,B),(a,B,A)))
shell=trimesh.Trimesh(vertices=np.asarray(verts),faces=np.asarray(faces),process=False)
shell.remove_unreferenced_vertices()
add('ONE_CONTINUOUS_REAR_SHELL','shell',shell)
# Count hole-wall edges via front/back projection; this also detects leaks
# caused by mismatched clip-cell triangulations.
print('SHELL QA',len(shell.faces),'triangles','watertight=',shell.is_watertight,
      'euler=',shell.euler_number)

# Integrating the APPROVED grille is a welded rim around an EXISTING HOLE, not
# another plate across it. Same side tones as the brown-gunmetal shell.
for side in (-1,1):
    cx=side*10.75;tag='LEFT' if side<0 else 'RIGHT'
    x1,x2=cx-5.39,cx+5.39;z1,z2=-7.20,17.20
    for x in (x1,x2):
        box(x,15.14,(z1+z2)/2,.13,.28,z2-z1+.20,f'GRILLE_WELD_{tag}','edge')
        box(x,15.009,(z1+z2)/2,.045,.042,z2-z1+.04,f'GRILLE_GASKET_{tag}','black')
        for z in np.linspace(z1+.8,z2-.8,6):bolt(x,14.95,float(z),f'GRILLE_BOLTS_{tag}')
    for z in (z1,z2):
        box(cx,15.14,z,x2-x1+.12,.28,.13,f'GRILLE_WELD_{tag}','edge')
        for x in np.linspace(x1+1,x2-1,5):bolt(float(x),14.95,z,f'GRILLE_BOLTS_{tag}')
# Narrow reference-grounded danger ticks under the bank, not a solid color band.
for side in (-1,1):
    cx=side*10.75
    for k in range(12):
        x=cx-4.65+k*.84
        bar((x-.16,15.086,-8.05),(x+.12,15.086,-7.91),.055,
            'LOWER_WARNING_TABS','warning',sections=6)
# Continuous, subtle reinforcement follows the outer OCTAGON contour; it
# does not outline or visually box in the central region.
for a,b in zip(outer,outer[1:]+outer[:1]):
    bar((a[0],15.05,a[1]),(b[0],15.05,b[1]),.13,'PERIMETER_ROLLED_LIP','dark',9)
# Only the two side hazard markers clearly seen on rear-room wings. Signals
# are dim/unlit material, not baked star rays or active game VFX.
for side in (-1,1):
    tag='L' if side<0 else 'R'
    x=side*21.3
    box(x,15.04,3.4,.33,.31,12.85,'REAR_SERVICE_PYLON_'+tag,'dark')
    box(x,14.86,5.7,.13,.071,6.70,'REAR_SERVICE_PYLON_'+tag,'copper')
    for z in (-2.9,10.0):
        box(x,14.75,z,.55,.16,.28,'REAR_SERVICE_PYLON_'+tag,'edge')
# A lightly cut sheet weld line exists along the *outer lower octagon corner*,
# not across center, so it doesn't read as a pasted-on middle panel.
for side in (-1,1):
    bar((side*17.0,15.09,-21.4),(side*24.40,15.09,-12.56),.049,
        'LOWER_CORNER_WELD','dark',7)

world=trimesh.Scene();tris=0
for (zone,kind),pieces in BUCKET.items():
    vv=[];ff=[];uu=[];offset=0
    for v,f,uv in pieces:
        vv.append(v);ff.append(f+offset);uu.append(uv);offset+=len(v)
    g=trimesh.Trimesh(vertices=np.concatenate(vv),faces=np.concatenate(ff),process=False)
    g.visual=trimesh.visual.texture.TextureVisuals(uv=np.concatenate(uu),material=M[kind])
    world.add_geometry(g,geom_name=f'{zone}__{kind}')
    tris+=len(g.faces)
GLB=OUT/'REACTOR_REAR_BULKHEAD_BRONZE_STEEL_REV03.glb'
GLB.write_bytes(world.export(file_type='glb'))
reloaded=trimesh.load(GLB,force='scene')
assert len(reloaded.geometry)==len(world.geometry)
assert tris==sum(len(g.faces) for g in reloaded.geometry.values())
# A real continuous front shell: all center, wing and upper cells belong to
# this ONE mesh, with no material or panel node suddenly changing in the center.
assert len([s for s in reloaded.geometry if s.startswith('ONE_CONTINUOUS')])==1

# Exact triangle-projection test for holes and filled center, rather than one
# combined-node AABB (which would wrongly report that the hole is obstructed).
def projected_shell_covered(x,z):
    g=next(g for n,g in reloaded.geometry.items() if n.startswith('ONE_CONTINUOUS'))
    t=g.vertices[g.faces][:,:,[0,2]]
    a,b,c=t[:,0],t[:,1],t[:,2];p=np.asarray((x,z))
    e=b-a;f=c-a;q=p-a
    cross=lambda u,v:u[:,0]*v[:,1]-u[:,1]*v[:,0]
    det=cross(e,f);d=np.where(abs(det)>1e-7,det,1.)
    u=cross(q,f)/d;v=cross(e,q)/d
    return bool(np.any((abs(det)>1e-7)&(u>1e-5)&(v>1e-5)&(u+v<1-1e-5)))
for side in (-1,1):
    for dx in (-3,0,3):
        for z in (-5,3,15):assert not projected_shell_covered(side*10.75+dx,z),'hole blocked'
for p in ((0,0),(0,19),(19,0),(0,-18),(-19,0)):
    assert projected_shell_covered(*p),'continuous shell gap'

approved=trimesh.load(OUT/'REACTOR_REAR_SERVICE_GRILLES_01.glb',force='scene')
context=trimesh.Scene()
for name,g in reloaded.geometry.items():context.add_geometry(g,geom_name='NEW_WALL_'+name)
for name,g in approved.geometry.items():context.add_geometry(g,geom_name='APPROVED_GRILLE_'+name)

def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    right=np.cross(f,(0,0,1.));right/=np.linalg.norm(right)
    up=np.cross(right,f)
    T=np.eye(4);T[:3,:3]=np.stack((right,up,-f),axis=1);T[:3,3]=eye
    return T

def shot(t,eye,target,fov):
    scene=pyrender.Scene.from_trimesh_scene(t,bg_color=[.012,.016,.023,1],
                                           ambient_light=[.22,.22,.24])
    for pos,col,power in [((-13,-16,13),(1.,.74,.57),440),
                          ((23,-9,8),(.57,.66,1.),350),
                          ((1,1,-10),(.56,.59,.77),200),
                          ((-22,4,6),(1.,.46,.29),80)]:
        T=np.eye(4);T[:3,3]=pos
        scene.add(pyrender.PointLight(color=np.asarray(col),intensity=power),pose=T)
    scene.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)),pose=look(eye,target))
    renderer=pyrender.OffscreenRenderer(1350,790)
    pixels,_=renderer.render(scene,flags=pyrender.RenderFlags.RGBA)
    renderer.delete()
    return Image.fromarray(pixels,'RGBA').convert('RGB')
context_front=shot(context,(0,-27,5),(0,15,0),58)
new_alone=shot(reloaded,(0,-27,5),(0,15,0),58).crop((229,0,1121,790))
close=shot(context,(4,-7,5),(0,15,3),53)
angle=shot(context,(-27,-12,12),(-4,15,1),63)
for name,img in [('CONTEXT',context_front),('ALONE',new_alone),('CLOSE',close),('ANGLE',angle)]:
    img.save(DBG/f'REAR_BULKHEAD_REV03_{name}.jpg',quality=86)

board=Image.new('RGB',(1920,1400),(13,18,30));d=ImageDraw.Draw(board)
try:
    ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',28)
    label=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
except OSError:ft=label=small=ImageFont.load_default()
def panel(im,x,y,w,h,caption):
    d.rectangle((x,y,x+w,y+h),fill=(18,25,38),outline=(71,87,106),width=2)
    q=ImageOps.contain(im,(w-4,h-4),Image.Resampling.LANCZOS)
    board.paste(q,(x+(w-q.width)//2,y+(h-q.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(71,87,106),width=2)
    d.text((x+14,y+13),caption,font=label,fill=(243,245,249),stroke_width=1,stroke_fill=(9,12,19))
d.text((40,18),'MODEL 05 REV03  /  KESİNTİSİZ KAHVERENGİ ÇELİK ARKA DUVAR',font=ft,fill=(243,246,252))
d.text((40,62),'Tek yüzey, tek PBR metal  •  sonradan eklenmiş orta parça YOK  •  onaylı ızgaralar için iki gerçekten açık geçit',font=label,fill=(178,195,218))
panel(context_front,36,103,1216,616,'BAĞLAM: yeni tek parça duvar + önceki ONAYLI ızgaralar (çevrimdışı render)')
panel(new_alone,1276,103,608,616,'YALNIZ YENİ MODEL / açık delikler')
panel(close,36,750,901,572,'ORTA DETAY / herhangi bir orta yama, panel değişimi yok')
panel(angle,963,750,921,572,'YAN AÇI / metal gövde, ızgara yuvasının derinliği')
d.text((40,1355),f'GLB {GLB.stat().st_size/1e6:.2f} MB  •  {len(reloaded.geometry)} adlandırılmış mesh (arka kabuk TEK mesh)  •  {tris:,} üçgen  •  Studio/oyun testi değildir.',
       font=small,fill=(165,184,207))
PRE=OUT/'REACTOR_REAR_BULKHEAD_BRONZE_STEEL_REV03_ONAY.png';board.save(PRE,optimize=True)
print('EXPORT',GLB,GLB.stat().st_size,'bytes',len(reloaded.geometry),'nodes',tris,'tris')
print('PREVIEW',PRE,PRE.stat().st_size,'bytes')
