#!/usr/bin/env python3
"""Reference-guided 3D plasma / magnetic confinement center for the reactor.

Not a flat star billboard: every beam is a triangulated 3D cylindrical field;
the turbulent core is a displaced icosphere, and orbit trails are curved 3D
swept tubes. Nothing in this script imports an asset from another creator.
Visible source: user-supplied image-3.png (13:21) and image-8.png (17:27).
Unseen space is an approximation. VFX/bloom in PREVIEW are not game effects.
Coordinates: X horizontal; Y depth; Z height; emitters meet at origin.
"""
from __future__ import annotations
import os,sys,math,random
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageChops
os.environ['PYOPENGL_PLATFORM']='egl'
sys.path[:0]=['/home/user/.cache/modeldeps','/home/user/.cache/modelrender']
import trimesh,pyrender
ROOT=Path('/home/user');OUT=ROOT/'model_exports';OUT.mkdir(exist_ok=True)
RAND=random.Random(13579)
TAU=math.tau


def make_mat(name,rgb,emission,alpha=1.,rough=.38):
    return trimesh.visual.material.PBRMaterial(
        name=name,baseColorFactor=[*rgb,round(alpha*255)],
        emissiveFactor=emission,metallicFactor=.03,roughnessFactor=rough,
        alphaMode='BLEND' if alpha<1 else 'OPAQUE',doubleSided=True)

MAT={
 'WHITE_CORE':make_mat('01 - White-hot plasma', (253,246,255),(.97,.92,1.)),
 'FUCHSIA_CORE':make_mat('02 - Ionization boundary', (205,58,162),(.72,.07,.43),.21),
 'VIOLET_VAPOR':make_mat('03 - Deep outer plasma', (61,26,134),(.16,.025,.32),.13),
 'WHITE_RAY':make_mat('04 - Focused six-way photon beam', (220,233,250),(.82,.84,.98)), 
 'WHITE_GLOW':make_mat('05 - Photon halo', (103,159,249),(.30,.40,.81),.14),
 'PINK_RAY':make_mat('06 - Thin electrical corona', (129,39,131),(.34,.018,.18),.11),
 'BLUE_RAY':make_mat('07 - Outer cobalt penumbra', (30,39,123),(.030,.05,.21),.08),
 'ORBIT_COPPER':make_mat('07 - Ruptured confinement orbit', (201,66,92),(.57,.035,.14),.82),
 'ORBIT_HOT':make_mat('08 - Ionized orbit highlights', (238,112,180),(.84,.24,.47),.93),
 'SPARK':make_mat('09 - Emitted incandescent fragments', (249,193,205),(.81,.40,.54)),
}
# Zones are separated, *not* one glued MeshPart: rays can switch on in a
# phased STARTUP and fail independently in MELTDOWN; orbits can spin.
PARTS={}
def add(mesh,zone,kind):
    assert mesh.is_volume or len(mesh.faces)>0
    PARTS.setdefault((zone,kind),[]).append(mesh)


def displaced_sphere(radius,seed,zone,kind,subdiv=3,wobble=.18):
    m=trimesh.creation.icosphere(subdivisions=subdiv,radius=1)
    V=np.asarray(m.vertices)
    f=(np.sin(V[:,0]*8.3+seed)*np.sin(V[:,1]*5.7-seed*.7)*
       np.cos(V[:,2]*9.7+seed*.8)+.52*np.sin(V[:,0]*13.5+V[:,2]*7.1+seed))
    m.vertices=V*(radius*(1+wobble*f))[:,None]
    add(m,zone,kind)

# Three independent shells. Displacement is geometric, not merely glow painted
# over an ordinary Part; white central pupil resembles saturated screenshot.
displaced_sphere(3.05,1.4,'CENTER','WHITE_CORE',subdiv=4,wobble=.22)
displaced_sphere(3.53,5.2,'CENTER','FUCHSIA_CORE',subdiv=4,wobble=.25)
displaced_sphere(4.39,9.4,'CENTER','VIOLET_VAPOR',subdiv=4,wobble=.29)


def radial_beam(direction,outer_radius,zone,kind,layer=1.0):
    """Variable-radius genuinely volumetric shaft with slightly irregular wavefronts."""
    d=np.asarray(direction,float);d=d/np.linalg.norm(d)
    A=np.cross(d,[0,1,0]);A/=np.linalg.norm(A)
    B=np.cross(d,A);B/=np.linalg.norm(B)
    n_axial,n_circle=38,20
    pts=[]
    for k in range(n_axial+1):
        t=k/n_axial
        axial=.16+outer_radius*t
        narrow=.56-(.21*t)
        flare=.17*math.exp(-((t-.11)/.22)**2)
        r=(narrow+flare)*layer
        c=d*axial + A*(.038*math.sin(t*12.7+len(zone))*(1-t))
        for j in range(n_circle):
            theta=TAU*j/n_circle
            irregular=1+.07*math.sin(theta*3+t*19)+.035*math.sin(theta*7-t*11)
            p=c+(A*math.cos(theta)+B*math.sin(theta))*r*irregular
            pts.append(p)
    faces=[]
    for k in range(n_axial):
        for j in range(n_circle):
            a=k*n_circle+j;b=k*n_circle+(j+1)%n_circle
            c=(k+1)*n_circle+j;e=(k+1)*n_circle+(j+1)%n_circle
            faces.extend(((a,c,b),(b,c,e)))
    mesh=trimesh.Trimesh(vertices=np.asarray(pts),faces=np.asarray(faces),process=False)
    add(mesh,zone,kind)

# A Core Game frame shows six feeds: left/right/top/bottom and two lower
# diagonals, NOT a mathematically symmetric radial star with new upper spokes.
FEEDS={
    'LEFT':(-1,0,0),'RIGHT':(1,0,0),
    'TOP':(0,0,1),'BOTTOM':(0,0,-1),
    'LOWER_LEFT':(-.72,0,-.694),'LOWER_RIGHT':(.72,0,-.694),
}
for zone,v in FEEDS.items():
    for mat,scale in (('BLUE_RAY',3.00),('PINK_RAY',2.23),
                      ('WHITE_GLOW',1.48),('WHITE_RAY',1.0)):
        radial_beam(v,7.20,zone,mat,scale)


def swept_curve(samples,width,zone,mat,side=9):
    """Real smoothly swept circular cross-section along any 3D polyline."""
    ps=np.asarray(samples,float);verts=[]
    for i,p in enumerate(ps):
        tangent=ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]
        tangent/=np.linalg.norm(tangent)
        basis=np.cross(tangent,[0,1,0])
        if np.linalg.norm(basis)<.12:basis=np.cross(tangent,[0,0,1])
        basis/=np.linalg.norm(basis)
        other=np.cross(tangent,basis)
        r=width*(.73+.22*math.sin(i*.21)+.05*math.cos(i*.81))
        for j in range(side):
            t=TAU*j/side
            verts.append(p+r*(basis*math.cos(t)+other*math.sin(t)))
    faces=[]
    for i in range(len(ps)-1):
        for j in range(side):
            a=i*side+j;b=i*side+(j+1)%side
            c=(i+1)*side+j;d=(i+1)*side+(j+1)%side
            faces.extend(((a,b,c),(b,d,c)))
    add(trimesh.Trimesh(vertices=np.asarray(verts),faces=np.asarray(faces),process=False),zone,mat)


# Fine twisting streamlines stop the six beams looking like six cut-off cones.
# Still true swept 3D fiber meshes, independently included in each feed zone.
for feed_index,(zone,direction) in enumerate(FEEDS.items()):
    d=np.asarray(direction,float);d/=np.linalg.norm(d)
    up=np.cross(d,[0,1,0]);up/=np.linalg.norm(up)
    side=np.cross(d,up)
    for strand in range(5):
        points=[];phase=(strand*TAU/5)+feed_index*.81
        for t in np.linspace(0,1,74):
            r=.21+.055*math.sin(t*10+strand)
            theta=phase+4.9*t+.18*math.sin(t*17+phase)
            p=d*(.46+t*6.45)+r*(up*math.cos(theta)+side*math.sin(theta))
            points.append(p)
        swept_curve(points,.012 if strand%2 else .018,zone,
                    'ORBIT_HOT' if strand==0 else 'WHITE_GLOW',side=6)


def ellipse_arc(start,stop,ring,rx,rz,ry,tilt,phase,width,zone,kind):
    R=np.array([[math.cos(tilt),-math.sin(tilt)],
                [math.sin(tilt),math.cos(tilt)]])
    path=[]
    for a in np.linspace(start,stop,127):
        v=R@np.array([rx*math.cos(a+phase),rz*math.sin(a+phase)])
        rr=1+.038*math.sin(5*a+ring)+.026*math.sin(11*a-ring)
        x,z=v*rr
        y=ry*math.sin(2*a+ring*.87)+.11*math.sin(5*a+ring)
        path.append((x,y,z))
    swept_curve(path,width,zone,kind,side=8)

# Only sparse broken energized orbits are actually visible behind the star;
# there is NO invented thick cage hiding the reference core.
ellipse_arc(.12,2.63,1,4.95,2.72,1.02,.17,.08,.042,
            'ORBIT_A','ORBIT_COPPER')
ellipse_arc(2.91,5.92,1,4.95,2.72,1.02,.17,.08,.033,
            'ORBIT_A','ORBIT_HOT')
ellipse_arc(.83,3.94,2,3.15,5.03,.91,-.43,.33,.031,
            'ORBIT_B','ORBIT_HOT')
ellipse_arc(4.10,6.61,2,3.15,5.03,.91,-.43,.33,.044,
            'ORBIT_B','ORBIT_COPPER')
ellipse_arc(.41,1.86,3,4.74,4.60,1.13,.64,1.17,.027,
            'ORBIT_C','ORBIT_COPPER')
ellipse_arc(3.91,5.12,3,4.74,4.60,1.13,.64,1.17,.022,
            'ORBIT_C','ORBIT_HOT')

# Small independent arcing filaments at the star edge. These are not fixed
# straight spokes; full-screen smoke and physics particles come later in Studio.
for i in range(20):
    a=RAND.uniform(0,TAU); rr=RAND.uniform(3.55,4.81)
    z=rr*math.sin(a);x=rr*math.cos(a)
    start=np.array([x,RAND.uniform(-.4,.4),z],float)
    fil=[]
    for j in range(12):
        t=j/11;angle=a+t*(.24+RAND.random()*.2)
        rad=rr+t*.37
        fil.append((rad*math.cos(angle),start[1]+.08*math.sin(t*10+i),rad*math.sin(angle)))
    swept_curve(fil,RAND.uniform(.009,.018),'ARCS','ORBIT_HOT',side=5)

for i in range(36):
    r=RAND.uniform(3.6,6.3);a=RAND.uniform(0,TAU)
    p=trimesh.creation.icosphere(subdivisions=1,radius=RAND.uniform(.015,.040))
    p.apply_translation((r*math.cos(a),RAND.uniform(-1.8,1.8),r*math.sin(a)))
    add(p,'SPARKS','SPARK')

# Export grouped 3D shell components and meaningful damage zones.
scene=trimesh.Scene();total=0
for (zone,kind),ms in PARTS.items():
    merged=trimesh.util.concatenate(ms);merged.remove_unreferenced_vertices()
    merged.visual=trimesh.visual.texture.TextureVisuals(
        uv=np.zeros((len(merged.vertices),2)),material=MAT[kind])
    scene.add_geometry(merged,geom_name=f'{zone}__{kind}')
    total+=len(merged.faces)
glb=OUT/'REACTOR_CORE_MANYETIK_01.glb'
glb.write_bytes(scene.export(file_type='glb'))
obj=ROOT/'.cache/model_obj/REACTOR_CORE_MANYETIK_01.obj'
obj.parent.mkdir(parents=True,exist_ok=True)
obj.write_text(trimesh.exchange.obj.export_obj(scene),encoding='utf-8')

# Render isolated real meshes, not fake painting or in-Studio gameplay. Emission
# and a small lens bloom are part of the preview's lighting, not hidden geometry.
view=pyrender.Scene.from_trimesh_scene(scene,
    bg_color=np.array([.018,.014,.038,1.0]),ambient_light=[.12,.13,.19])

def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    right=np.cross(f,[0,0,1.]);right/=np.linalg.norm(right)
    up=np.cross(right,f)
    pose=np.eye(4);pose[:3,:3]=np.stack([right,up,-f],axis=1);pose[:3,3]=eye
    return pose
for pos,rgb,energy in [((0,-6,7),(.54,.66,1.),68),((-5,2,1),(1.,.21,.47),43),
                       ((4,3,2),(.33,.20,1.),29)]:
    pose=np.eye(4);pose[:3,3]=pos
    view.add(pyrender.PointLight(color=np.array(rgb),intensity=energy),pose=pose)
renderer=pyrender.OffscreenRenderer(1160,760)
def render(eye,angle=48,bloom=.37):
    camera=view.add(pyrender.PerspectiveCamera(yfov=math.radians(angle)),pose=look(eye,(0,0,0)))
    rgba,_=renderer.render(view,flags=pyrender.RenderFlags.RGBA)
    view.remove_node(camera)
    img=Image.fromarray(rgba,'RGBA').convert('RGB')
    # Standard HDR-like lens bloom. Pixels are taken ONLY from the mesh render;
    # broad 3D photon-field glow is otherwise impossible in a flat GLB preview.
    if bloom:
        a=np.asarray(img,dtype=np.float32)
        hot=np.uint8(np.clip((a-75)*1.85,0,255))
        bright=Image.fromarray(hot,'RGB')
        halos=[np.asarray(bright.filter(ImageFilter.GaussianBlur(rad)),dtype=np.float32)
               for rad in (16,42,95)]
        a=np.clip(a+bloom*(1.2*halos[0]+.94*halos[1]+.46*halos[2]),0,255)
        img=Image.fromarray(np.uint8(a),'RGB')
    return img
front=render((0,-22,4),angle=41,bloom=1.30)
iso=render((9,-20,8),angle=42,bloom=1.20)
center=render((0,-10,3),angle=37,bloom=1.08)
renderer.delete()
DEBUG=ROOT/'.cache/model_debug';DEBUG.mkdir(parents=True,exist_ok=True)
front.save(DEBUG/'REACTOR_CORE_FRONTAL_01.png')
iso.save(DEBUG/'REACTOR_CORE_THREEQUARTER_01.png')
center.save(DEBUG/'REACTOR_CORE_CENTRE_01.png')

# Context preview uses ONLY the already-approved emitter REV03, placed six
# times in a temporary offline 3D scene. This is not Studio integration,
# and no new chamber asset is passed off as approved.
emitter=trimesh.load(OUT/'REACTOR_EMITTER_REV03.glb',force='scene')
context=trimesh.Scene()
for k,g in scene.geometry.items():context.add_geometry(g,geom_name='CORE_'+k)
for zone,direction in FEEDS.items():
    direction=np.asarray(direction,float);direction/=np.linalg.norm(direction)
    T=trimesh.geometry.align_vectors((1,0,0),-direction)
    T[:3,3]=direction*(7.20+8.55)
    for name,g in emitter.geometry.items():
        context.add_geometry(g,geom_name=f'{zone}_{name}',transform=T)
cv=pyrender.Scene.from_trimesh_scene(context,bg_color=[.016,.013,.035,1],
                                     ambient_light=[.18,.17,.24])
for pos,color,power in [((0,-5,7),(.65,.78,1.),75),
                        ((-13,-9,3),(1.,.23,.08),145),
                        ((13,-5,3),(.32,.32,1.),65),
                        ((0,0,0),(1.,.64,.91),255)]:
    pose=np.eye(4);pose[:3,3]=pos
    cv.add(pyrender.PointLight(color=np.array(color),intensity=power),pose=pose)
camera=cv.add(pyrender.PerspectiveCamera(yfov=math.radians(45)),
              pose=look((0,-41,6),(0,0,0)))
r=pyrender.OffscreenRenderer(1320,780)
raw,_=r.render(cv,flags=pyrender.RenderFlags.RGBA)
r.delete()
a=np.asarray(Image.fromarray(raw,'RGBA').convert('RGB'),dtype=np.float32)
bright=Image.fromarray(np.uint8(np.clip((a-85)*1.65,0,255)),'RGB')
g1=np.asarray(bright.filter(ImageFilter.GaussianBlur(21)),dtype=np.float32)
g2=np.asarray(bright.filter(ImageFilter.GaussianBlur(68)),dtype=np.float32)
a=np.clip(a+.88*g1+.41*g2,0,255)
context_image=Image.fromarray(np.uint8(a),'RGB')
context_image.save(OUT/'REACTOR_CORE_WITH_APPROVED_EMITTERS_01.png')

board=Image.new('RGB',(1890,1330),(13,17,28));d=ImageDraw.Draw(board)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',32)
    head=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
    body=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
except OSError:title=head=body=ImageFont.load_default()
def panel(img,x,y,w,h,label):
    d.rectangle((x,y,x+w,y+h),fill=(23,27,42))
    r=ImageOps.contain(img,(w,h),Image.Resampling.LANCZOS)
    board.paste(r,(x+(w-r.width)//2,y+(h-r.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(73,80,108),width=2)
    d.text((x+15,y+12),label,font=head,fill=(239,244,255),stroke_width=1,stroke_fill=(10,12,19))
d.text((46,25),'MODEL 02   /   MERKEZ ÇEKİRDEK + MANYETİK YÖRÜNGELER',font=title,fill=(242,244,253))
d.text((46,77),'Altı ışın + plazma  •  onaylı yayıcıyla yalnızca çevrimdışı bağlam önizlemesi  •  Studio görüntüsü değildir',font=head,fill=(175,189,216))
panel(context_image,45,117,1115,715,'Altı onaylı yayıcı + yeni çekirdek — gerçek meshlerin çevrimdışı renderı')
panel(iso,1183,117,663,715,'Yalnız çekirdek / 3B açı')
panel(center,45,865,665,400,'Merkez ayrıntı — uzamsal yüzey')
ref=Image.open(ROOT/'model_work/reference_crops/CORE_REF_1321.png').convert('RGB')
panel(ref,735,865,547,400,'Referans — 13:21 (meltdown +92 s)')
ref2=Image.open(ROOT/'model_work/reference_crops/CORE_REF_1727.png').convert('RGB')
panel(ref2,1307,865,539,400,'Referans — 17:27 (meltdown +338 s)')
d.text((46,1290),f'GLB + OBJ   /   {total:,} üçgen   /   {len(scene.geometry)} ayrı mesh bölgesi   /   bu renderda ışık patlaması önizleme işlemidir',font=body,fill=(173,190,214))
preview=OUT/'REACTOR_CORE_MODEL_ONAY_01.png'
board.save(preview,optimize=True)
print('EXPORT:',glb,'meshes',len(scene.geometry),'triangles',total,'bytes',glb.stat().st_size)
print('PREVIEW:',preview)
