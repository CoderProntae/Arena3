#!/usr/bin/env python3
"""Model 06: left+right reactor side cladding with REAL hatch-sized portals.

Uses the APPROVED Rev04 back-wall brown iron PBR maps unchanged. The two side
walls are physically segmented steel structures with full-thickness holes.
The already-approved sliding-door hatch, emitter and rear hydraulic guide are
SEPARATE assets. This GLB does not re-export them or fill their openings;
context previews load those approved GLBs only for truthful fit inspection.

Local reactor axes: X horizontal, Y front-to-back, Z up. Left wall inside
X=-24.5; right inside X=+24.5. Rear edge Y=12.93 meets the approved curved
back wall. Front edge Y=-18. The cutout follows the approved hatch's 20.20x20.50
facade, widening locally to 24.10 only where doors/rails slide. Behind each real hole stays open for the user's
later piston-side service facility. No Studio writes, VFX or sound tests.
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
parser=argparse.ArgumentParser();parser.add_argument('--release',action='store_true');args=parser.parse_args()
OUT=PERSIST if args.release else ROOT/'.cache/side_walls_candidate';OUT.mkdir(parents=True,exist_ok=True)
DBG=ROOT/'.cache/model_debug';DBG.mkdir(parents=True,exist_ok=True)

approved_bulk=trimesh.load(PERSIST/'REACTOR_REAR_BULKHEAD_IRON_REV04.glb',force='scene')
BROWN=approved_bulk.geometry['ROLLED_IRON_COURSE_2__iron'].visual.material
LINING=approved_bulk.geometry['REAR_LOAD_BEARING_LINER__lining'].visual.material
CUT=approved_bulk.geometry['OCTAGON_WING_FOLD__cut'].visual.material if 'OCTAGON_WING_FOLD__cut' in approved_bulk.geometry else None
# The approved rear wall has a steel cut-edge material in M, but if not in its
# export the same restrained alloy is defined explicitly for the weld bead.
if CUT is None:
    CUT=trimesh.visual.material.PBRMaterial(name='Forged side-rear edge iron',
        baseColorFactor=[128,135,136,255],metallicFactor=.81,roughnessFactor=.43,doubleSided=True)
DARK=trimesh.visual.material.PBRMaterial(name='Folded compression liner steel',
    baseColorFactor=[50,59,68,255],metallicFactor=.75,roughnessFactor=.60,doubleSided=True)
RED=trimesh.visual.material.PBRMaterial(name='Unlit red warning lens',
    baseColorFactor=[127,49,37,255],metallicFactor=.33,roughnessFactor=.46,doubleSided=True)
M={'iron':BROWN,'liner':LINING,'edge':CUT,'dark':DARK,'signal':RED}
BUCKET={}

def add(zone,kind,g,side):
    v=g.vertices
    # Side-to-rear UV alignment: at the rear corners U matches the rear wall's
    # U=0 left / U=1 right. The same roughness/oxide map continues in Z.
    u=(v[:,1]+18)/(12.93+18)
    if side<0:u=1-u
    uv=np.stack((u,(v[:,2]+22)/44),axis=1)
    BUCKET.setdefault((zone,kind),[]).append((v,g.faces,uv))

def rod(a,b,r,zone,kind,side,segments=9):
    a=np.asarray(a,float);b=np.asarray(b,float);vec=b-a;length=np.linalg.norm(vec)
    if length<1e-4:return
    g=trimesh.creation.cylinder(radius=r,height=length,sections=segments)
    g.apply_transform(trimesh.geometry.align_vectors((0,0,1),vec/length))
    g.apply_translation((a+b)/2)
    add(zone,kind,g,side)

def block(center,size,zone,kind,side):
    g=trimesh.creation.box(extents=size);g.apply_translation(center);add(zone,kind,g,side)

U0,U1=-18.0,12.93
V0,V1=-12.5,12.5
hU0,hU1=-12.05,12.05  # wide ONLY where the two hatch leaves slide
hV0,hV1=-10.42,10.42
sheetU0,sheetU1=-10.28,10.28  # approved solid facade is +/-10.10
railV0,railV1=-4.10,4.10   # doors and rail extents stay within +/-3.86
ucuts=[U0,hU0,sheetU0,sheetU1,hU1,U1]
vcuts=[V0,hV0,railV0,-2.0,railV1,8.5,hV1,V1]
bands=[V0,-2.0,8.5,V1]  # rear-wall seams are at these SAME global Z levels.

def cells():
    for i in range(len(ucuts)-1):
        u0,u1=ucuts[i],ucuts[i+1]
        for j in range(len(vcuts)-1):
            v0,v1=vcuts[j],vcuts[j+1]
            inside_sheet=u0>=sheetU0-1e-8 and u1<=sheetU1+1e-8 and v0>=hV0-1e-8 and v1<=hV1+1e-8
            inside_rails=u0>=hU0-1e-8 and u1<=hU1+1e-8 and v0>=railV0-1e-8 and v1<=railV1+1e-8
            if not (inside_sheet or inside_rails):yield u0,u1,v0,v1

def extrude(rects,side,front,back):
    # One physically thick sheet, UV coordinates are Y/Z. All equal neighbor
    # vertices welded: real continuous volume; only the central portal remains.
    V=[];f_cache={};b_cache={};faces=[]
    def get(y,z,which):
        key=(round(y,6),round(z,6));D=f_cache if which==0 else b_cache
        if key not in D:
            D[key]=len(V);V.append((front if which==0 else back,key[0],key[1]))
        return D[key]
    for y0,y1,z0,z1 in rects:
        q=[(y0,z0),(y1,z0),(y1,z1),(y0,z1)]
        a=[get(y,z,0) for y,z in q];b=[get(y,z,1) for y,z in q]
        if side<0:
            faces.extend(((a[0],a[1],a[2]),(a[0],a[2],a[3]),
                          (b[0],b[2],b[1]),(b[0],b[3],b[2])))
        else:
            faces.extend(((a[0],a[2],a[1]),(a[0],a[3],a[2]),
                          (b[0],b[1],b[2]),(b[0],b[2],b[3])))
    # Find all front boundary edges, not whole merged-mesh bounding boxes.
    edge={}
    for face in faces:
        if all(p in f_cache.values() for p in face):
            a,b,c=face
            for m,n in ((a,b),(b,c),(c,a)):
                edge.setdefault((min(m,n),max(m,n)),[]).append((m,n))
    back_of={f_cache[k]:b_cache[k] for k in f_cache}
    for idx,uses in edge.items():
        if len(uses)==1:
            a,b=uses[0];A=back_of[a];B=back_of[b]
            if side<0:faces.extend(((a,b,B),(a,B,A)))
            else:faces.extend(((a,B,b),(a,A,B)))
    g=trimesh.Trimesh(vertices=np.asarray(V),faces=np.asarray(faces),process=False)
    g.remove_unreferenced_vertices();return g

for side in (-1,1):
    tag='LEFT' if side<0 else 'RIGHT'
    # Site thickness follows approved local hatch X range (-3.22..+.34).
    # Front shell is at +/-24.5, behind-wall face at +/-27.72.
    xinner=side*24.5;xouter=side*27.72
    foundation=extrude(list(cells()),side,xinner,xouter)
    assert foundation.is_watertight and foundation.euler_number==0,(tag,foundation.euler_number)
    add(tag+'_SIDE_THROUGH_SHELL','liner',foundation,side)
    # Three aligned rolled sheet courses, separated by thin intentional welds.
    for i in range(3):
        pieces=[]
        for u0,u1,v0,v1 in cells():
            mid=(v0+v1)/2
            if bands[i]<=mid<=bands[i+1]:
                a=v0+(.06 if abs(v0-bands[i])<1e-6 and i>0 else 0)
                b=v1-(.06 if abs(v1-bands[i+1])<1e-6 and i<2 else 0)
                pieces.append((u0,u1,a,b))
        cover=extrude(pieces,side,side*(24.5-.34),side*(24.5-.10))
        assert cover.is_watertight,(tag,i,cover.euler_number)
        add(tag+f'_ROLLED_SIDE_COURSE_{i+1}','iron',cover,side)
    # Light, physically present compressed gasket follows the port outline;
    # the opening itself stays open in all states and is never a black backplate.
    xlip=side*(24.5-.36)
    outline=[(sheetU0,hV0),(sheetU1,hV0),
             (sheetU1,railV0),(hU1,railV0),
             (hU1,railV1),(sheetU1,railV1),
             (sheetU1,hV1),(sheetU0,hV1),
             (sheetU0,railV1),(hU0,railV1),
             (hU0,railV0),(sheetU0,railV0)]
    for (y0,z0),(y1,z1) in zip(outline,outline[1:]+outline[:1]):
        rod((xlip,y0,z0),(xlip,y1,z1),.063,
            tag+'_PORT_WELD','dark',side,segments=8)
    # The short travel bays are backed INSIDE the wall by inset folded-steel
    # pockets. Without these, the rail clearance reads as a huge black tear.
    # They cannot block the central Y +/-10.28 passage or touch the door leaf
    # at X local +0.05..+0.34, Y +/-11.65 while it opens.
    for sign in (-1,1):
        center_y=sign*(sheetU1+hU1)/2
        block((side*(24.5+.61),center_y,0),(.16,hU1-sheetU1,railV1-railV0),
              tag+'_RECESSED_DOOR_TRAVEL_POCKET','liner',side)
    # This rear seam is a single forged joint, not an inserted middle patch.
    rod((side*24.47,U1,-12.30),(side*24.47,U1,12.30),.086,
        tag+'_REAR_CROSS_WELD','edge',side)
    # Reference-visible narrow signal pylon beside the wall port; lens is
    # passive/unlit in this GLB and game-state lights are a future Studio task.
    sigY=12.37
    block((side*24.16,sigY,6.6),(.22,.28,10.6),tag+'_SIDE_WARNING_PYLON','dark',side)
    block((side*24.02,sigY,7.65),(.08,.135,4.3),tag+'_SIDE_WARNING_PYLON','signal',side)
    for z in (1.25,11.95):
        block((side*24.02,sigY,z),(.22,.39,.26),tag+'_SIDE_WARNING_PYLON','edge',side)
    # Front joint awaits the actual observation-window module; top/bottom
    # rolled lips await separately reviewed roof/floor. No fake completion.
    for z in (V0+.13,V1-.13):
        rod((side*24.33,U0,z),(side*24.33,U1,z),.083,
            tag+'_ROOF_FLOOR_JOINT','edge',side)
    rod((side*24.34,U0,V0+.12),(side*24.34,U0,V1-.12),.099,
        tag+'_FRONT_WINDOW_JOINT','dark',side)

wall=trimesh.Scene();tris=0
for (zone,kind),parts in BUCKET.items():
    vv=[];ff=[];uvs=[];shift=0
    for v,f,uv in parts:
        vv.append(v);ff.append(f+shift);uvs.append(uv);shift+=len(v)
    mesh=trimesh.Trimesh(vertices=np.concatenate(vv),faces=np.concatenate(ff),process=False)
    mesh.visual=trimesh.visual.texture.TextureVisuals(uv=np.concatenate(uvs),material=M[kind])
    wall.add_geometry(mesh,geom_name=f'{zone}__{kind}');tris+=len(mesh.faces)
GLB=OUT/'REACTOR_SIDE_WALLS_TRUE_PORTS_01.glb';GLB.write_bytes(wall.export(file_type='glb'))
roundtrip=trimesh.load(GLB,force='scene')
assert len(roundtrip.geometry)==len(wall.geometry)
assert sum(len(g.faces) for g in roundtrip.geometry.values())==tris
for side,tag in [(-1,'LEFT'),(1,'RIGHT')]:
    g=roundtrip.geometry[tag+'_SIDE_THROUGH_SHELL__liner']
    assert g.is_watertight and g.euler_number==0
    # Check aperture inside 3D sheet with face projections in YZ; compare a
    # truly empty port point with a filled point above the hatch.
    def covers(y,z):
        p=np.asarray((y,z));t=g.vertices[g.faces][:,:,[1,2]]
        a,b,c=t[:,0],t[:,1],t[:,2];e=b-a;f=c-a;q=p-a
        cross=lambda u,v:u[:,0]*v[:,1]-u[:,1]*v[:,0]
        det=cross(e,f);d=np.where(np.abs(det)>1e-7,det,1.)
        u=cross(q,f)/d;v=cross(e,q)/d
        return bool(np.any((np.abs(det)>1e-7)&(u>1e-5)&(v>1e-5)&(u+v<1-1e-5)))
    for y in (-8,0,8):
        for z in (-8,0,8):assert not covers(y,z),(tag,'blocked port',y,z)
    for y,z in [(-11,0),(11,0)]:assert not covers(y,z),(tag,'blocked sliding clearance',y,z)
    for y,z in [(-11,-8),(11,8),(-15,0),(0,11.5)]:
        assert covers(y,z),(tag,'missing structural close-fit course',y,z)

# Reference-guided OFFLINE assembly preview. Everything but the new side-wall
# GLB below comes from individual previously approved assets. Nothing is put
# into Roblox Studio yet. Orientation is shared with the final mechanical spec.
closed=trimesh.load(PERSIST/'REACTOR_WALL_HATCH_THROUGH_01.glb',force='scene')
open_h=trimesh.load(PERSIST/'REACTOR_WALL_HATCH_OPEN_INSPECTION_01.glb',force='scene')
emitter=trimesh.load(PERSIST/'REACTOR_EMITTER_REV03.glb',force='scene')
piston=trimesh.load(PERSIST/'REACTOR_PISTON_GUIDE_01.glb',force='scene')
grilles=trimesh.load(PERSIST/'REACTOR_REAR_SERVICE_GRILLES_01.glb',force='scene')

def place(scene,asset,prefix,T):
    # Load geometry with each GLB's original scene-graph transform, notably
    # the open inspection hatch where individual doors move in its graph.
    for node_name in asset.graph.nodes_geometry:
        Tlocal,geom_name=asset.graph[node_name]
        geom=asset.geometry[geom_name]
        scene.add_geometry(geom,geom_name=f'{prefix}_{node_name}_{geom_name}',transform=T@Tlocal)

def assemble(open_doors=False,one_side_emitter=False,pistons=False):
    s=trimesh.Scene()
    place(s,roundtrip,'NEW_SIDE',np.eye(4))
    place(s,approved_bulk,'APPROVED_REAR_WALL',np.eye(4))
    place(s,grilles,'APPROVED_REAR_GRILLES',np.eye(4))
    for side,word in [(-1,'LEFT'),(1,'RIGHT')]:
        T=np.eye(4)
        if side>0:T=trimesh.transformations.rotation_matrix(math.pi,(0,0,1))
        T[:3,3]=(side*24.5,0,0)
        place(s,open_h if open_doors else closed,word+'_HATCH',T)
        if one_side_emitter and side==-1:
            TE=T.copy();TE[:3,3]+=np.array((-11.47,0,0))
            place(s,emitter,word+'_COLD_EMITTER',TE)
        if pistons and side==-1:
            place(s,piston,word+'_PISTON',T)
    return s

cold=assemble(False,True,False)
open_cut=assemble(True,True,True)
open_empty=assemble(True,False,False)
solo=trimesh.Scene();place(solo,roundtrip,'ONLY_NEW_SIDE_WALLS',np.eye(4))

def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    rt=np.cross(f,(0,0,1.));rt/=np.linalg.norm(rt)
    up=np.cross(rt,f)
    P=np.eye(4);P[:3,:3]=np.stack((rt,up,-f),axis=1);P[:3,3]=eye
    return P

def render(src,eye,target,fov):
    scene=pyrender.Scene.from_trimesh_scene(src,bg_color=[.009,.013,.021,1],ambient_light=[.23,.23,.25])
    for pos,col,power in [((-18,-20,15),(1.,.70,.52),425),
                          ((21,-9,8),(.50,.59,.98),360),
                          ((0,2,-7),(.63,.40,.85),150),
                          ((-31,3,1),(1.,.40,.24),115)]:
        T=np.eye(4);T[:3,3]=pos
        scene.add(pyrender.PointLight(color=np.asarray(col),intensity=power),pose=T)
    scene.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)),pose=look(eye,target))
    r=pyrender.OffscreenRenderer(1380,820)
    pix,_=r.render(scene,flags=pyrender.RenderFlags.RGBA)
    r.delete()
    return Image.fromarray(pix,'RGBA').convert('RGB')
full=render(cold,(0,-32,8),(0,2,0),58)
left=render(cold,(4,-9,5),(-24.3,0,0),58)
empty=render(solo,(0,-30,13),(0,-1,0),62)
behind=render(open_cut,(-38,-10,10),(-24.5,0,0),66)
through=render(open_empty,(-39,-8,6),(-22,1,0),62)
for name,im in [('FRONT',full),('LEFT',left),('ONLY',empty),
                ('BEHIND',behind),('THROUGH_OPEN',through)]: 
    im.save(DBG/('SIDE_WALLS_'+name+'.jpg'),quality=85)

sheet=Image.new('RGB',(1920,1990),(13,19,30));d=ImageDraw.Draw(sheet)
try:
    big=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',29)
    label=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
except OSError:big=label=small=ImageFont.load_default()
def panel(im,x,y,w,h,name):
    d.rectangle((x,y,x+w,y+h),fill=(17,24,36),outline=(71,88,106),width=2)
    v=ImageOps.contain(im,(w-4,h-4),Image.Resampling.LANCZOS)
    sheet.paste(v,(x+(w-v.width)//2,y+(h-v.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(71,88,106),width=2)
    d.text((x+12,y+10),name,font=label,fill=(242,245,251),stroke_width=1,stroke_fill=(7,10,17))
d.text((42,17),'MODEL 06  /  YAN DUVARLAR, GERÇEK YAYICI GEÇİTLERİ',font=big,fill=(242,246,254))
d.text((42,64),'Aynı onaylı kahverengi demir  •  iki gerçek merkez geçidi, gelecekteki arka tesis için açık  •  kapak/yayıcı/piston ayrı GLB',
       font=label,fill=(173,192,213))
panel(full,38,105,1173,630,'BAĞLAM / yalnız yeni yan duvarlar + önce onaylı arka duvar, ızgara ve kapaklar')
ref=Image.open(ROOT/'uploads/image-3.png').convert('RGB').crop((5,10,888,424))
panel(ref,1233,105,648,630,'REFERANS / aynı faz testi değil')
d.text((1250,583),'Referans: parlak MELTDOWN karesi.',font=label,fill=(218,226,240))
d.text((1250,615),'Bu önizleme: ışınsız COLD montajı.',font=label,fill=(176,196,217))
d.text((1250,647),'Yalnız YAN DUVAR geometrisi yeni;',font=label,fill=(176,196,217))
d.text((1250,679),'kapak ve arka duvar onaylı GLB.',font=label,fill=(176,196,217))
panel(left,38,771,911,579,'SOL YAN / gerçek çelik sac ve onaylı kapak, COLD')
panel(empty,972,771,909,579,'YALNIZ YENİ GLB / her iki yanda kapatılmamış geçit')
panel(through,38,1382,911,540,'ARKADAN / açılmış kapak, merkeze açık geçit; yayıcı gizlendi')
panel(behind,972,1382,909,540,'ARKADAN / açık kapak + yayıcı/piston; çevrimdışı')
d.text((42,1950),f'Yeni GLB {GLB.stat().st_size/1e6:.2f} MB  •  {len(roundtrip.geometry)} adlandırılmış mesh  •  {tris:,} üçgen  •  çatı/zemin/ön cam, ışın VFX ve oyun testi HENÜZ YOK.',
       font=small,fill=(165,185,209))
PRE=OUT/'REACTOR_SIDE_WALLS_TRUE_PORTS_01_ONAY.png';sheet.save(PRE,optimize=True)
print('OUTPUT',GLB,GLB.stat().st_size,'bytes',len(roundtrip.geometry),'meshes',tris,'triangles')
print('PREVIEW',PRE,PRE.stat().st_size,'bytes; stepped aperture max width',hU1-hU0,
      'at rail height and max height',hV1-hV0,'within facade width',sheetU1-sheetU0)
