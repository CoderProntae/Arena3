#!/usr/bin/env python3
"""Model 06 Rev02 — reference-guided OCTAGONAL METAL reactor side shell.

Rev01 was rejected: flat/too-close side slabs and fiber/wood-looking inherited
rear-wall texture. This is a *geometry/material* rebuild, not a tint change.
Keep the approved hatch, piston, emitter and rear bulkhead GLBs UNMODIFIED.
Only the two new side-shells are exported here. The true main through-ports
stay open through thickness; narrow pockets behind the sliding-leaf tracks
are metal backed, leaving +/-11.65 hatch travel unobstructed.

Axes X horizontal, Y depth (front -> rear), Z up. Octagonal rear wall's REAL
edge is X +/-24.5 at Z +/-12.5, tapering to X +/-17 at Z +/-21.5; its
front Y edge changes from ~12.93 to ~15.4 along this diagonal. These two
side shells continue THAT footprint into the room with wide sloped upper and
lower folded-steel facets, instead of being two flat sheets. Ceiling/floor
between the facets, front observation wall and back service facility are
separate later models; no fake surfaces fill those missing zones.

Reference image-3.png is a MELTDOWN frame; this candidate is rendered COLD
with no beam. No same-phase comparison, studio installation, VFX or physics.
"""
from __future__ import annotations
import argparse,math,os,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
from scipy.ndimage import gaussian_filter
os.environ['PYOPENGL_PLATFORM']='egl'
sys.path[:0]=['/home/user/.cache/modeldeps','/home/user/.cache/modelrender']
import trimesh,pyrender
ROOT=Path('/home/user');EXP=ROOT/'model_exports'
parser=argparse.ArgumentParser();parser.add_argument('--release',action='store_true');args=parser.parse_args()
OUT=EXP if args.release else ROOT/'.cache/side_walls_rev02_candidate';OUT.mkdir(parents=True,exist_ok=True)
DBG=ROOT/'.cache/model_debug';DBG.mkdir(parents=True,exist_ok=True)

# ISOTROPIC punched/oxidized METAL. No macro directional noise, inherited rear
# normal pattern or UV stretching. Physically metal at pixel level; rust flecks
# reduce metalness / increase roughness, exposed steel has bright cold edges.
W=H=512;rng=np.random.default_rng(602061)
def noise(sigma):
    q=gaussian_filter(rng.standard_normal((H,W)),sigma=sigma,mode='wrap')
    return q/(q.std()+1e-8)
macro=noise(14);micro=noise(2.6);grain=rng.standard_normal((H,W))
rust=np.clip(.44+.075*macro+.085*micro+.027*grain,.15,.72)
scars=rng.random((H,W))<.009
base=(1-rust[...,None])*np.array([88.,99.,107.])+rust[...,None]*np.array([139.,79.,56.])
base+=np.clip(grain,-2.5,2.5)[...,None]*1.5
base[scars]-=np.array([28.,23.,20.])
BASE=Image.fromarray(np.uint8(np.clip(base,8,245)),'RGB')
MR=np.empty((H,W,3),np.uint8);MR[:,:,0]=255
MR[:,:,1]=np.uint8(np.clip((.45+.24*rust+.025*np.abs(micro))*255,1,255))
MR[:,:,2]=np.uint8(np.clip((.93-.32*rust)*255,1,255))
METAL_ROUGH=Image.fromarray(MR,'RGB')
hmap=micro*.8+noise(.8)*.19+scars*.3
gy,gx=np.gradient(hmap);nx=-gx*.07;ny=-gy*.07;nz=np.ones_like(nx)
length=np.sqrt(nx*nx+ny*ny+nz*nz)
NORMAL=Image.fromarray(np.uint8(np.clip((np.stack((nx,ny,nz),2)/length[...,None]*.5+.5)*255,0,255)),'RGB')

def mat(name,color,met=.78,rough=.55,tex=None,mr=None,normal=None):
    return trimesh.visual.material.PBRMaterial(name=name,
        baseColorFactor=[*((255,255,255) if tex is not None else color),255],
        metallicFactor=met,roughnessFactor=rough,
        baseColorTexture=tex,metallicRoughnessTexture=mr,normalTexture=normal,
        doubleSided=True)
M={
 'iron':mat('01 Rolled brown oxidized IRON, isotropic punched surface',None,1.,1.,BASE,METAL_ROUGH,NORMAL),
 'frame':mat('02 Blackened wrought iron structural folds',(61,66,70),.88,.49),
 'edge':mat('03 Bright rubbed forged-steel bends',(142,148,148),.92,.33),
 'liner':mat('04 Heat darkened metallic steel behind pressed courses',(65,66,68),.77,.66),
 'pocket':mat('05 Satin folded steel in sliding-door side pockets',(85,89,91),.84,.50),
 'red':mat('06 Red enclosed unlit signal lens',(137,48,34),.56,.46),
}
BINS={}

def add(zone,kind,mesh,side):
    v=mesh.vertices
    # Both primary sheets and angled facets use actual Y/Z world scale.
    # 12-unit isotropic repeat; texture is WRAP-smoothed at every tile edge.
    u=(v[:,1]+18.)/12.
    if side<0:u=-u
    uv=np.stack((u,(v[:,2]+22.)/12.),axis=1)
    BINS.setdefault((zone,kind),[]).append((v,mesh.faces,uv))

def bar(a,b,r,zone,kind,side,sides=9):
    a=np.array(a,float);b=np.array(b,float);d=b-a;L=np.linalg.norm(d)
    if L<1e-6:return
    g=trimesh.creation.cylinder(radius=r,height=L,sections=sides)
    g.apply_transform(trimesh.geometry.align_vectors((0,0,1),d/L));g.apply_translation((a+b)*.5)
    add(zone,kind,g,side)

def box(c,size,zone,kind,side):
    g=trimesh.creation.box(extents=size);g.apply_translation(c);add(zone,kind,g,side)

YFRONT=-18.;YREAR=12.93
HATCH_Y=-2.70                      # hatch/piston/emitter move TOGETHER toward front
SHEETLO,SHEETHI=HATCH_Y-10.28,HATCH_Y+10.28  # approved sheet +/-10.10 plus .18
RAILLO,RAILHI=HATCH_Y-12.05,HATCH_Y+12.05    # approved rail +/-11.87, leaf +/-11.65
ZOLO,ZOHI=-10.42,10.42             # approved hatch +/-10.25 plus 0.17
SLIDELO,SLIDEHI=-4.10,4.10         # rail +/-3.86 and leaf +/-3.62
zbase=12.5;ztop=21.5;xin=24.5;xtop=17.0
uy=[YFRONT,RAILLO,SHEETLO,SHEETHI,RAILHI,9.70,10.45,11.55,YREAR]
zz=[-12.5,ZOLO,SLIDELO,-2.,SLIDEHI,8.5,ZOHI,12.5]

def waist_cells():
    for ya,yb in zip(uy[:-1],uy[1:]):
        for za,zb in zip(zz[:-1],zz[1:]):
            hatch=ya>=SHEETLO-1e-7 and yb<=SHEETHI+1e-7 and za>=ZOLO-1e-7 and zb<=ZOHI+1e-7
            slide=ya>=RAILLO-1e-7 and yb<=RAILHI+1e-7 and za>=SLIDELO-1e-7 and zb<=SLIDEHI+1e-7
            if not (hatch or slide):yield ya,yb,za,zb

def close_volume(vertices,front_faces,front_to_back,side):
    """Both skins + every *actual boundary* of their 2D tiled front faces."""
    fs=list(front_faces)
    for a,b,c in front_faces:
        fs.append((front_to_back[a],front_to_back[c],front_to_back[b]))
    edges={}
    for a,b,c in front_faces:
        for j,k in ((a,b),(b,c),(c,a)):
            p=(min(j,k),max(j,k));edges.setdefault(p,[]).append((j,k))
    for uses in edges.values():
        if len(uses)!=1:continue
        a,b=uses[0];A=front_to_back[a];B=front_to_back[b]
        fs.extend(((a,B,b),(a,A,B)))
    g=trimesh.Trimesh(vertices=np.asarray(vertices),faces=np.asarray(fs),process=False)
    g.remove_unreferenced_vertices();return g

def rear_y_x(ax):
    """Approved rear wall structural liner front Y outside the grille sockets."""
    t=np.clip((ax-16.14)/(24.5-16.14),0,1)
    return 15.48-2.55*t*t*(3-2*t)

def warp_corner(y,z):
    """Bend the side STEEL ITSELF into the approved rear, never overlay a patch.

    Starts AFTER the real hatch rail (Y 9.35), reaches X +/-21.2 and
    Y 13.8 behind the portal. Upper/lower octagonal facets smoothly retain
    their approved rear edge X +/-17 at Z +/-21.5. The real moving-door
    corridor ends BEFORE any vertex in these bends shifts its position.
    """
    zt=np.clip((abs(z)-12.5)/9.,0,1)
    base=24.5-7.5*zt
    strength=1.-zt
    y0=rear_y_x(base)
    t=np.clip((y-9.7)/(y0-9.7),0,1)
    smooth=t*t*(3-2*t)
    inside=base-3.30*strength*smooth
    y_real=y+smooth*(rear_y_x(inside)-y0)
    return inside,y_real

def extrude_waist(rectangles,side,xfront,xback):
    verts=[];front={};back={};faces=[]
    def get(y,z,x,cache):
        key=(round(float(y),6),round(float(z),6))
        if key not in cache:
            ax,real_y=warp_corner(*key)
            displacement=x/side-24.5
            cache[key]=len(verts);verts.append((side*(ax+displacement),real_y,key[1]))
        return cache[key]
    for y0,y1,z0,z1 in rectangles:
        poly=[(y0,z0),(y1,z0),(y1,z1),(y0,z1)]
        q=[get(y,z,xfront,front) for y,z in poly]
        for i in (1,2):
            faces.append((q[0],q[i],q[i+1]) if side<0 else (q[0],q[i+1],q[i]))
        for y,z in poly:get(y,z,xback,back)
    paired={a:back[p] for p,a in front.items()}
    return close_volume(verts,faces,paired,side)

def facet_x(side,z):
    t=np.clip((abs(z)-zbase)/(ztop-zbase),0,1)
    return side*(xin+(xtop-xin)*t)

def front_y(z):
    t=np.clip((abs(z)-zbase)/(ztop-zbase),0,1)
    return YFRONT+2.35*t          # real diagonally raked front rim

def rear_y(z):
    # The rear edge of the sloping sheets must follow the already approved
    # cubic-bent steel rather than terminate in an unrelated vertical patch.
    return rear_y_x(abs(facet_x(1,z)))

def folded_facet(side,zlow,zhigh,front_push,back_push,trim0=0.,trim1=0.,steps=8):
    """Watertight pressed quadrilateral steel, x(z) ACTUALLY slopes inward.

    front_push goes TOWARD core (+ on left / - on right); back_push goes AWAY
    from core. Inner and outer returns are solids, not painted triangles.
    """
    verts=[];fidx={};bidx={};fs=[];ys=[0.,.25,.5,.7,.83,.9,.95,1.]
    zs=np.linspace(zlow,zhigh,steps+1)
    def get(i,j,back=False):
        D=bidx if back else fidx
        if (i,j) not in D:
            z=zs[j];yf=front_y(z)+trim0;yr=rear_y(z)-trim1
            y=yf+(yr-yf)*ys[i]
            mag,real_y=warp_corner(y,z)
            x=side*(mag+(back_push if back else -front_push))
            D[(i,j)]=len(verts);verts.append((x,real_y,z))
        return D[(i,j)]
    for i in range(len(ys)-1):
        for j in range(len(zs)-1):
            a,b,c,d=get(i,j),get(i+1,j),get(i+1,j+1),get(i,j+1)
            fs.extend(((a,b,c),(a,c,d)) if side<0 else ((a,c,b),(a,d,c)))
            for m,n in ((i,j),(i+1,j),(i+1,j+1),(i,j+1)):get(m,n,True)
    pairs={fidx[k]:bidx[k] for k in fidx}
    return close_volume(verts,fs,pairs,side)

for side in (-1,1):
    tag='LEFT' if side<0 else 'RIGHT'
    # ONE REAL HOLE in each thick vertical structural shell. This is the
    # static mounting wall, NOT a rectangular opaque backplate behind hatch.
    waist=extrude_waist(list(waist_cells()),side,side*24.5,side*27.72)
    assert waist.is_watertight and waist.euler_number==0,(tag,'waist portal',waist.euler_number)
    add(tag+'_STRUCTURAL_WAIST_TRUE_PORT','liner',waist,side)
    # Plates are separate rolled steel courses, with just narrow weld valleys;
    # upper+lower rails occur only where the already-approved hatch needs them.
    course_edges=[(-12.5,-2.),(-2.,8.5),(8.5,12.5)]
    for k,(low,high) in enumerate(course_edges):
        items=[]
        for y0,y1,z0,z1 in waist_cells():
            zc=(z0+z1)/2
            if not low<=zc<=high:continue
            za=z0+(.065 if k>0 and abs(z0-low)<1e-7 else 0.)
            zb=z1-(.065 if k<2 and abs(z1-high)<1e-7 else 0.)
            items.append((y0,y1,za,zb))
        p=extrude_waist(items,side,side*(24.5-.40),side*(24.5-.09))
        assert p.is_watertight,(tag,'course',k)
        add(tag+f'_STAMPED_WAIST_COURSE_{k+1}','iron',p,side)
    # Four VOLUMETRIC diagonal wall sections: upper/lower steel shell and
    # matching stamped face. These connect precisely to the APPROVED rear
    # octagon at (X +/-17,Z +/-21.5); no fake roof/floor cap is inserted.
    for top in (False,True):
        label='UPPER' if top else 'LOWER'
        lo,hi=(12.5,21.5) if top else (-21.5,-12.5)
        g=folded_facet(side,lo,hi,0.,3.22,steps=12)
        assert g.is_watertight and g.euler_number==2,(tag,label,'structure',g.euler_number)
        add(tag+f'_{label}_DIAGONAL_STRUCTURAL_BLOCK','liner',g,side)
        intervals=[(12.5,18.65),(18.65,21.5)] if top else [(-21.5,-18.65),(-18.65,-12.5)]
        for i,(a,b) in enumerate(intervals):
            shrink=.055
            a+=shrink if a!=lo else 0
            b-=shrink if b!=hi else 0
            p=folded_facet(side,a,b,.41,-.105,trim0=.06,trim1=.08,steps=8)
            assert p.is_watertight and p.euler_number==2,(tag,label,i,'iron plate')
            add(tag+f'_{label}_SLOPED_ROLLED_IRON_{i+1}','iron',p,side)
        # Sloping reinforcement of the *front observation return* is a real
        # diagonal on all 4 corners, not a drawn-on stripe or rectangular bar.
        z0,z1=(12.5,21.5) if top else (-12.5,-21.5)
        a=(facet_x(side,z0)-side*.54,front_y(z0)+.42,z0)
        b=(facet_x(side,z1)-side*.54,front_y(z1)+.42,z1)
        bar(a,b,.22,tag+f'_{label}_FRONT_DIAGONAL_CORNER_GUSSET','frame',side,10)
        a2=(facet_x(side,z0)-side*.62,front_y(z0)+.46,z0)
        b2=(facet_x(side,z1)-side*.62,front_y(z1)+.46,z1)
        bar(a2,b2,.065,tag+f'_{label}_FRONT_DIAGONAL_CORNER_GUSSET','edge',side,8)
        # The deliberate 0.11-unit DARK valley between two rolled sheets is
        # visible by geometry alone. No segment-by-segment bright seam rods:
        # their broken white highlights previously read like cheap trim.
    # The front-/back-surface normals themselves show the real, continuous
    # fold from waist to steep diagonal plate. Do not glue bright rods on it.
    # Stepped steel gasket follows the *actual* portal outline. Narrow leaf
    # travel pockets are metal-backed at X local -0.61, never behind its
    # central clear-through opening, locally +/-10.28 about HATCH_Y.
    outline=[(SHEETLO,ZOLO),(SHEETHI,ZOLO),
             (SHEETHI,SLIDELO),(RAILHI,SLIDELO),
             (RAILHI,SLIDEHI),(SHEETHI,SLIDEHI),
             (SHEETHI,ZOHI),(SHEETLO,ZOHI),
             (SHEETLO,SLIDEHI),(RAILLO,SLIDEHI),
             (RAILLO,SLIDELO),(SHEETLO,SLIDELO)]
    for (ya,za),(yb,zb) in zip(outline,outline[1:]+outline[:1]):
        bar((side*(24.5-.435),ya,za),(side*(24.5-.435),yb,zb),.055,
            tag+'_HATCH_STEEL_INTERFACE','frame',side,8)
    for sign in (-1,1):
        y=(SHEETLO+RAILLO)*.5 if sign<0 else (SHEETHI+RAILHI)*.5
        box((side*25.11,y,0),(.16,RAILHI-SHEETHI,SLIDEHI-SLIDELO),
            tag+'_RECESSED_METAL_SLIDER_POCKET','pocket',side)
    # The belt and BOTH angled shells have already been continuously bent
    # into the rear approved wall by warp_corner(). No glued-on corner panel.
    # Narrow side warning lens seen on reference beside each port. OFFLINE
    # lens is unlit; game-state light/VFX is a later, separate task.
    sy=9.58
    box((side*24.11,sy,6.55),(.22,.27,10.55),tag+'_CORNER_WARNING','frame',side)
    box((side*23.97,sy,7.55),(.08,.12,4.05),tag+'_CORNER_WARNING','red',side)
    for z in (1.15,11.91):box((side*23.97,sy,z),(.20,.37,.26),tag+'_CORNER_WARNING','edge',side)
    # Approved rear wall extends physically to the raked end of all sloped
    # sides; front rim remains open for later window module.
    bar((side*24.28,YFRONT,-12.4),(side*24.28,YFRONT,12.4),.12,
        tag+'_FRONT_WINDOW_FUTURE_JOINT','frame',side)

scene=trimesh.Scene();ntri=0
for (zone,kind),parts in BINS.items():
    V=[];F=[];UV=[];off=0
    for v,f,u in parts:
        V.append(v);F.append(f+off);UV.append(u);off+=len(v)
    g=trimesh.Trimesh(vertices=np.concatenate(V),faces=np.concatenate(F),process=False)
    g.visual=trimesh.visual.texture.TextureVisuals(uv=np.concatenate(UV),material=M[kind])
    scene.add_geometry(g,geom_name=zone+'__'+kind);ntri+=len(g.faces)
NAME='REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV02'
GLB=OUT/(NAME+'.glb');GLB.write_bytes(scene.export(file_type='glb'))
reloaded=trimesh.load(GLB,force='scene')
assert len(scene.geometry)==len(reloaded.geometry)
assert ntri==sum(len(g.faces) for g in reloaded.geometry.values())
for word in ('LEFT','RIGHT'):
    core=reloaded.geometry[word+'_STRUCTURAL_WAIST_TRUE_PORT__liner']
    assert core.is_watertight and core.euler_number==0
    # A projection against front-plane triangles demonstrates a TRUE aperture
    # through the actual reloaded GLB, not just an Euler/genus label. Side
    # slider pockets have backing, but the center is NEVER given a backplate.
    cx=-24.5 if word=='LEFT' else 24.5
    q=core.vertices[core.faces]
    q=q[np.all(np.abs(q[:,:,0]-cx)<1e-4,axis=1)][:,:,[1,2]]
    def front_covers(y,z):
        p=np.array([y,z]);a,b,c=q[:,0],q[:,1],q[:,2]
        e=b-a;f=c-a;d=p-a
        cross=lambda u,v:u[:,0]*v[:,1]-u[:,1]*v[:,0]
        den=cross(e,f);den=np.where(np.abs(den)>1e-9,den,1.)
        t=cross(d,f)/den;u=cross(e,d)/den
        return bool(np.any((t>1e-6)&(u>1e-6)&(t+u<1-1e-6)))
    for yy,zz in ((HATCH_Y,0),(HATCH_Y,8),(RAILHI-.7,0),(RAILLO+.7,0)):
        assert not front_covers(yy,zz),(word,'blocked actual port',yy,zz)
    for yy,zz in ((HATCH_Y,11.8),(SHEETHI+.65,7.),(YFRONT+.5,0)):
        assert front_covers(yy,zz),(word,'missing surrounding steel',yy,zz)
    assert 9.7>RAILHI and RAILLO>YFRONT
    for zpart in ('UPPER','LOWER'):
        g=reloaded.geometry[f'{word}_{zpart}_DIAGONAL_STRUCTURAL_BLOCK__liner']
        assert g.is_watertight and g.euler_number==2
        for i in (1,2):
            p=reloaded.geometry[f'{word}_{zpart}_SLOPED_ROLLED_IRON_{i}__iron']
            assert p.is_watertight
    # Every deformed rear endpoint agrees with the approved outer octagon.
    s=-1 if word=='LEFT' else 1
    assert np.allclose((facet_x(s,ztop),rear_y(ztop)),(s*17.,15.48-2.55*((17.-16.14)/(24.5-16.14))**2*(3-2*((17.-16.14)/(24.5-16.14)))),atol=1e-7)
iron=reloaded.geometry['LEFT_UPPER_SLOPED_ROLLED_IRON_1__iron'].visual.material
assert iron.baseColorTexture.size==(512,512) and iron.normalTexture.size==(512,512)

# Context: only NEW sides export; everything below remains approved separate
# source GLBs placed without changing their geometry or shrinking emitters.
rear=trimesh.load(EXP/'REACTOR_REAR_BULKHEAD_IRON_REV04.glb',force='scene')
vent=trimesh.load(EXP/'REACTOR_REAR_SERVICE_GRILLES_01.glb',force='scene')
closed=trimesh.load(EXP/'REACTOR_WALL_HATCH_THROUGH_01.glb',force='scene')
opened=trimesh.load(EXP/'REACTOR_WALL_HATCH_OPEN_INSPECTION_01.glb',force='scene')
emitter=trimesh.load(EXP/'REACTOR_EMITTER_REV03.glb',force='scene')
piston=trimesh.load(EXP/'REACTOR_PISTON_GUIDE_01.glb',force='scene')

def place(dst,src,prefix,T):
    for node in src.graph.nodes_geometry:
        local,geom=src.graph[node]
        dst.add_geometry(src.geometry[geom],geom_name=f'{prefix}_{node}_{geom}',transform=T@local)

def assembly(with_emitter=False,open_hatches=False,deployed=False):
    assert not deployed or open_hatches
    s=trimesh.Scene();place(s,reloaded,'NEW_SIDE',np.eye(4))
    place(s,rear,'APPROVED_REAR',np.eye(4));place(s,vent,'APPROVED_GRILLES',np.eye(4))
    for sign in (-1,1):
        T=np.eye(4)
        if sign>0:T=trimesh.transformations.rotation_matrix(math.pi,(0,0,1))
        T[:3,3]=[sign*24.5,HATCH_Y,0]
        place(s,opened if open_hatches else closed,'LEFT_HATCH' if sign<0 else 'RIGHT_HATCH',T)
        if deployed:
            D=np.eye(4);D[0,3]=8.33  # 19.80 from original -11.47; NO stretching
            place(s,emitter,'APPROVED_RIGID_ADVANCED_EMITTER',T@D)
        elif sign<0 and with_emitter:
            D=np.eye(4);D[0,3]=-11.47
            place(s,emitter,'APPROVED_RETRACTED_EMITTER',T@D)
            if open_hatches:place(s,piston,'APPROVED_HYDRAULIC_GUIDE',T)
    return s
cold=assembly(False,False);through=assembly(False,True)
mechanism=assembly(True,True);deployed=assembly(False,True,True)
solo=trimesh.Scene();place(solo,reloaded,'ONLY_NEW_SIDES',np.eye(4))

def camera(eye,target):
    e=np.array(eye,float);t=np.array(target,float);f=t-e;f/=np.linalg.norm(f)
    right=np.cross(f,(0,0,1.));right/=np.linalg.norm(right)
    up=np.cross(right,f)
    p=np.eye(4);p[:3,:3]=np.stack((right,up,-f),axis=1);p[:3,3]=e
    return p

def render(src,eye,target,fov):
    s=pyrender.Scene.from_trimesh_scene(src,bg_color=[.016,.019,.025,1.],ambient_light=[.15,.16,.18])
    for where,color,intensity in [((-17,-20,17),(1.,.79,.64),600),
                                  ((18,-17,8),(.58,.69,1.),430),
                                  ((0,5,17),(1.,.55,.38),225),
                                  ((-31,-6,-2),(.71,.80,1.),165),
                                  ((-13,6,-15),(.90,.59,.45),140)]:
        pose=np.eye(4);pose[:3,3]=where
        s.add(pyrender.PointLight(color=np.asarray(color),intensity=intensity),pose=pose)
    s.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)),pose=camera(eye,target))
    r=pyrender.OffscreenRenderer(1380,820)
    frame,_=r.render(s,flags=pyrender.RenderFlags.RGBA);r.delete()
    return Image.fromarray(frame,'RGBA').convert('RGB')
front=render(cold,(0,-41,5),(0,3,0),64)
side=render(cold,(6,-19,12),(-24.,-1,3),64)
standalone=render(solo,(0,-40,9),(0,-1,0),66)
texture_view=render(cold,(-1,-10,14),(-24.,-3,13),60)
rear_open=render(through,(-39,-8,6),(-22,1,0),62)
rear_guide=render(mechanism,(-38,-10,10),(-24.5,0,0),66)
stage=render(deployed,(0,-41,5),(0,3,0),64)
for name,im in [('FRONT',front),('SIDE',side),('ONLY',standalone),('METAL',texture_view),
                ('THROUGH',rear_open),('MECHANISM',rear_guide),('DEPLOYED',stage)]: 
    im.save(DBG/(NAME+'_'+name+'.jpg'),quality=89)

sheet=Image.new('RGB',(1920,1535),(12,19,29));d=ImageDraw.Draw(sheet)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',29)
    text=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
except OSError:title=text=small=ImageFont.load_default()
def panel(im,x,y,w,h,label,fill_crop=False):
    d.rectangle((x,y,x+w,y+h),fill=(17,25,37),outline=(69,89,112),width=2)
    target=(w-4,h-4)
    fit=ImageOps.fit(im,target,Image.Resampling.LANCZOS) if fill_crop else ImageOps.contain(im,target,Image.Resampling.LANCZOS)
    sheet.paste(fit,(x+(w-fit.width)//2,y+(h-fit.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(69,89,112),width=2)
    d.text((x+11,y+9),label,font=text,fill=(241,248,252),stroke_width=2,stroke_fill=(9,14,22))
d.text((39,16),'MODEL 06 REV02 / ÇAPRAZ OKTAGONAL DEMİR YAN GÖVDE',font=title,fill=(243,247,253))
d.text((40,59),'Düz/kumaş görünümlü önceki model REDDEDİLDİ. Bu GLB: gerçek eğimli kabuk + içe dönen köşe + yeni metal PBR.',font=text,fill=(184,207,228))
ref=Image.open(ROOT/'uploads/image-3.png').convert('RGB').crop((8,5,890,428))
panel(ref,40,102,902,416,'REFERANS 13:21 / MELTDOWN, ışın + VFX var',True)
panel(stage,978,102,902,416,'3B MEKANİK POZ / kapak açık, yayıcı rijit ileride; ışın/VFX YOK',True)
panel(front,40,545,902,430,'COLD / üst-alt gerçek eğimli çelik ve iki yana açılabilir yuva')
panel(side,978,545,902,430,'YAN AÇI / reaktör kesiti, arka köşede metalin sürekli kıvrımı')
panel(texture_view,40,1002,902,430,'MALZEME DETAYI / metalik yansıma + küçük izotropik pas çukurları')
panel(rear_open,978,1002,902,430,'ARKADAN / gerçek delik, onaylı kapaklar açık; tesis daha yapılmadı')
d.text((42,1484),f'Yeni GLB {GLB.stat().st_size/1e6:.2f} MB • {len(reloaded.geometry)} mesh • {ntri:,} üçgen • çatı, zemin, camlı oda, durum-VFX, Studio entegrasyonu ve oyun testleri HENÜZ YOK.',font=small,fill=(165,188,208))
preview=OUT/(NAME+'_ONAY.png');sheet.save(preview,optimize=True)
# Supplemental ONLY-new-GLB outline, retained separately so the mechanical
# context does not make the actual through-ports look like painted backplates.
proof=Image.new('RGB',(1710,645),(12,19,29));pd=ImageDraw.Draw(proof)
for im,x,label in ((standalone,22,'YALNIZ YENİ YAN-DUVAR GLB / iki port fiziksel delik'),
                   (rear_guide,866,'ARKA YÜZ / onaylı piston, henüz servis binası yok')):
    thumb=ImageOps.contain(im,(818,532),Image.Resampling.LANCZOS)
    proof.paste(thumb,(x+(818-thumb.width)//2,62+(532-thumb.height)//2))
    pd.rectangle((x,62,x+818,594),outline=(69,89,112),width=2)
    pd.text((x+8,67),label,font=text,fill=(240,247,252),stroke_width=1,stroke_fill=(8,13,19))
pd.text((23,16),'MODEL 06 / GEÇİT VE PİSTONUN ARKADAN TEKNİK KONTROLÜ',font=title,fill=(242,246,251))
pd.text((24,612),'Piston ve kapak daha önce onaylanan ayrı GLB’lerdir; yalnız yeni yan duvarlar bu pakette.',font=small,fill=(176,197,214))
proof_path=OUT/(NAME+'_PORT_QA.png');proof.save(proof_path,optimize=True)
print('MODEL',GLB,GLB.stat().st_size,'bytes;',len(reloaded.geometry),'meshes;',ntri,'triangles')
print('PREVIEW',preview,preview.stat().st_size,'bytes; PORT QA',proof_path,proof_path.stat().st_size,'bytes')
