#!/usr/bin/env python3
"""Model 07 Rev02 candidate: 360p-led roof/deck and lower diagonal housings.

A reference-led original 3-D mesh add-on to the APPROVED sidewall Rev02:
X ±17 at Z ±21.5, source Y -18..15.4. The existing approved six emitter
GLBs and pistons are shown only in a REAL mesh context render; they are not
baked into this new GLB or altered. No star rays, audio, physics, or game
scripts are baked here. Rear service rooms remain separate future work.

Coordinates: X horizontal, Y negative toward observation window, Z up.
"""
from __future__ import annotations
import math,os,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
os.environ['PYOPENGL_PLATFORM']='egl'
sys.path[:0]=['/home/user/.cache/modeldeps','/home/user/.cache/modelrender']
import trimesh,pyrender
ROOT=Path('/home/user');OUT=ROOT/'model_exports';OUT.mkdir(exist_ok=True)
NAME='REACTOR_CEILING_DECK_SERVICE_BAYS_REV02'
prev=trimesh.load(OUT/'REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV02.glb',force='scene')
# Blue-grey NEW roof/deck skins; this DOES NOT change the user's approved
# brown-pitted BACK wall. Its texture physics reuse approved normal/roughness,
# while a distinct deliberately cooler albedo approaches 360p cold frames.
refIron=prev.geometry['LEFT_UPPER_SLOPED_ROLLED_IRON_1__iron'].visual.material
rng=np.random.default_rng(607702)
noise=rng.normal(0,5,(512,512,1))
blueSteel=np.clip(np.array([84,103,135])+noise,0,255).astype(np.uint8)
blueTexture=Image.fromarray(blueSteel,'RGB')
M={
 'IRON':trimesh.visual.material.PBRMaterial(name='Cool weathered pitted sheet',
    baseColorTexture=blueTexture,normalTexture=refIron.normalTexture,
    metallicRoughnessTexture=refIron.metallicRoughnessTexture,
    baseColorFactor=(255,255,255,255),metallicFactor=1,roughnessFactor=1,
    doubleSided=True),
 'LINER':trimesh.visual.material.PBRMaterial(name='Deep blue-grey welded liner',
    baseColorFactor=(50,67,95,255),metallicFactor=.77,roughnessFactor=.62,
    doubleSided=True),
 'FRAME':trimesh.visual.material.PBRMaterial(name='Brushed perimeter alloy',
    baseColorFactor=(128,151,180,255),metallicFactor=.91,
    roughnessFactor=.42,doubleSided=True),
 'EDGE':trimesh.visual.material.PBRMaterial(name='Polished pale cold rim',
    baseColorFactor=(171,193,212,255),metallicFactor=.83,
    roughnessFactor=.36,doubleSided=True),
 'LUMEN':trimesh.visual.material.PBRMaterial(name='WHITE groove emitter in actual roof mesh',
    baseColorFactor=(232,246,255,255),emissiveFactor=(1.0,1.0,1.0),
    metallicFactor=.10,roughnessFactor=.32,doubleSided=True),
}
BINS={}
def add(zone,kind,mesh):
 assert len(mesh.faces)>0
 BINS.setdefault((zone,kind),[]).append(mesh)
def box(c,size,zone,kind):
 m=trimesh.creation.box(extents=size);m.apply_translation(c)
 add(zone,kind,m);return m
def cylinder(a,b,r,zone,kind,sections=14):
 a=np.asarray(a,float);b=np.asarray(b,float);v=b-a
 if np.linalg.norm(v)<1e-4:raise ValueError('zero length')
 m=trimesh.creation.cylinder(radius=r,height=np.linalg.norm(v),sections=sections)
 m.apply_transform(trimesh.geometry.align_vectors((0,0,1),v/np.linalg.norm(v)))
 m.apply_translation((a+b)*.5)
 add(zone,kind,m)
 return m
def toroid(center,axis,inner,outer,length,zone,kind,segments=48):
 """Four-ring solid sleeve; through-opening stays genuinely clear."""
 c=np.asarray(center,float);a=np.asarray(axis,float);a/=np.linalg.norm(a)
 base=np.cross(a,(0,1,0))
 if np.linalg.norm(base)<.1:base=np.cross(a,(1,0,0))
 base/=np.linalg.norm(base);other=np.cross(a,base)
 verts=[];faces=[]
 # ring order: front-inner, front-outer, back-inner, back-outer.
 for axial,radius in ((-1,inner),(-1,outer),(1,inner),(1,outer)):
  for j in range(segments):
   th=j*2*math.pi/segments
   verts.append(c+a*axial*length/2+radius*(math.cos(th)*base+math.sin(th)*other))
 for j in range(segments):
  k=(j+1)%segments
  for u,v,flip in ((0,1,False),(2,3,True),(0,2,True),(1,3,False)):
   aa=u*segments+j;bb=u*segments+k;cc=v*segments+j;dd=v*segments+k
   if flip:faces.extend(((aa,cc,bb),(bb,cc,dd)))
   else:faces.extend(((aa,bb,cc),(bb,dd,cc)))
 m=trimesh.Trimesh(vertices=np.asarray(verts),faces=np.asarray(faces),process=False)
 m.remove_unreferenced_vertices()
 add(zone,kind,m)
 return m
Y0,Y1=-18.,15.4
HOLE_X=5.45;HOLE_Y0,HOLE_Y1=-8.35,2.95  # actual guide radius 4.33
# Four separate continuous panel courses per surface give a REAL central
# opening. All metal is structurally thick; NO flat sheet behind the aperture.
for sign,title in ((1,'ROOF'),(-1,'DECK')):
 z=sign*22.72;thickness=2.44
 for a,b in ((-17,-HOLE_X),(HOLE_X,17)):
  box(((a+b)/2,(Y0+Y1)/2,z),(b-a,Y1-Y0,thickness),
      title+'_FULL_DEPTH_LATERAL_SHELL','LINER')
  # Separate embedded rolled course, not a grey untextured plane.
  box(((a+b)/2,(Y0+Y1)/2,z-sign*1.17),
      (b-a-.19,Y1-Y0-.24,.10),title+'_PITTED_IRON_FACE','IRON')
 for a,b in ((Y0,HOLE_Y0),(HOLE_Y1,Y1)):
  box((0,(a+b)/2,z),(2*HOLE_X,b-a,thickness),
      title+'_CUT_PORT_FRONT_AND_REAR_BRIDGES','LINER')
  box((0,(a+b)/2,z-sign*1.17),
      (2*HOLE_X-.15,b-a-.12,.10),title+'_PITTED_IRON_FACE','IRON')
 # Ring around the *visible* hole but NEVER across it. Both upper and lower
 # guides pass through at their existing approved 1:1 stud scale.
 toroid((0,-2.7,sign*23.56),(0,0,sign),4.9,5.32,.74,
        title+'_PORT_MACHINED_HOLLOW_SLEEVE','FRAME')
 toroid((0,-2.7,sign*22.31),(0,0,sign),5.34,5.55,.22,
        title+'_RUBBED_PORT_EDGE','EDGE')
 # In the 360p source, two STEPPED WHITE GUIDELINES cross the top
 # and bottom faces. Each is an inset 3-D bar with a separate forged holder;
 # the central port remains open at ALL y along its mechanical travel.
 for y in (-14.9,10.8):
  box((0,y,sign*21.43),(31.7,.36,.095),
      title+'_GUIDELINE_STEEL_CHANNEL','FRAME')
  box((0,y,sign*21.37),(30.6,.12,.075),
      title+'_TWO_RECESSED_WHITE_SERVICE_GUIDELINES','LUMEN')
  for x in (-14.3,-10.2,-6.0,6.0,10.2,14.3):
   box((x,y,sign*21.40),(.10,.52,.085),
       title+'_GUIDELINE_TRUE_SEGMENT_JOINT','LINER')
 toroid((0,-2.7,sign*21.39),(0,0,sign),5.62,5.72,.085,
        title+'_WHITE_COLD_PORT_INSET_NOT_FILLED','LUMEN')
 for x in (-8.5,8.5):
  # True 3D long rail into side wall / rear bulkhead.
  cylinder((x,Y0+.8,sign*21.56),(x,Y1-.9,sign*21.56),.27,
      title+'_LOAD_BEARING_STEEL_GIRDER','FRAME')
 for x in (-13.7,13.7):
  for y in (-14.3,10.8):
   toroid((x,y,sign*21.33),(0,0,sign),.12,.27,.08,
     title+'_RECESSED_CORNER_FASTENERS','EDGE',segments=16)
# Two heavy lower-diagonal collars line up with the ACTUAL approved rails,
# not decorative heads pasted on a wall. The connector foot terminates in
# the APPROVED sloped side block (approximately X ±21 at Z -16).
for side,label in ((-1,'LEFT'),(1,'RIGHT')):
 outward=np.asarray((side*.72,0,-.694),float)
 outward/=np.linalg.norm(outward)
 collar=outward*24.3+np.asarray((0,-2.7,0))
 toroid(collar,outward,4.96,5.52,.95,
   label+'_LOWER_DIAGONAL_TRUE_OPEN_SOCKET','FRAME')
 toroid(collar-outward*.59,outward,5.55,5.78,.22,
   label+'_LOWER_DIAGONAL_RUBBED_IRON_RIM','EDGE')
 for depth in (-7.5,2.1):
  # Open triangulated support bracket, meets rather than covers the approved
  # slanted lower side sheet. Dark webs + steel knee, no fake closed gate.
  wall=np.array((side*21.7,depth,-15.7))
  foot=np.array((collar[0]+side*1.75,depth,collar[2]-2.4))
  cylinder(wall,foot,.49,label+'_WELDED_SERVICE_KNEE','FRAME')
  cylinder(wall+np.array((0,0,-1.55)),foot,.24,
           label+'_TRIANGULATED_SUPPORT_WEB','LINER')
  cylinder(foot,collar+np.array((0,depth+2.7,0)),.32,
           label+'_OPEN_RADIAL_RAIL','FRAME')
 # Short, actual 3-D service line supported along the lower wall, purpose
 # limited to the visible chamber; no invented remote facility is claimed.
 tubeStart=(side*20.9,-12.3,-17.9)
 tubeEnd=(side*20.9,10.9,-17.9)
 cylinder(tubeStart,tubeEnd,.28,label+'_DAMAGE_READY_VISIBLE_CONDUIT','EDGE')
 for y in (-11,10):
  toroid((side*20.9,y,-17.9),(0,1,0),.295,.44,.26,
   label+'_CONDUIT_CLAMP','FRAME',segments=20)
# Keyframe-aware QA: roof/deck port void is not filled by any rectangle.
for a,b in ((-17,-HOLE_X),(HOLE_X,17)):
 assert not (a<0<b)
assert HOLE_X>4.33 and -2.7-HOLE_Y0>4.33 and HOLE_Y1-(-2.7)>4.33
scene=trimesh.Scene();tris=0
for (zone,kind),meshes in BINS.items():
 g=trimesh.util.concatenate(meshes)
 g.remove_unreferenced_vertices()
 v=g.vertices
 # UV on the horizontal face, shared *world scale* as Rev02 pitted iron.
 # Subcomponents retain physical metalness/roughness/glancing highlights.
 uv=np.stack(((v[:,0]+18)/12.,(v[:,1]+18)/12.),axis=1)
 g.visual=trimesh.visual.texture.TextureVisuals(uv=uv,material=M[kind])
 scene.add_geometry(g,geom_name=zone+'__'+kind)
 tris+=len(g.faces)
GLB=OUT/(NAME+'.glb');GLB.write_bytes(scene.export(file_type='glb'))
check=trimesh.load(GLB,force='scene')
assert len(check.geometry)==len(scene.geometry)
assert sum(len(m.faces) for m in check.geometry.values())==tris
assert any('ROOF_PORT' in x for x in check.geometry)
assert any('DECK_PORT' in x for x in check.geometry)
assert any('LOWER_DIAGONAL_TRUE_OPEN_SOCKET' in x for x in check.geometry)
# Real GLB context for existing approved seven assets. Only NEW shell
# geometry is included in the exported model.
sidewall=prev
rear=trimesh.load(OUT/'REACTOR_REAR_BULKHEAD_IRON_REV04.glb',force='scene')
grille=trimesh.load(OUT/'REACTOR_REAR_SERVICE_GRILLES_01.glb',force='scene')
emitter=trimesh.load(OUT/'REACTOR_EMITTER_REV03.glb',force='scene')
piston=trimesh.load(OUT/'REACTOR_PISTON_GUIDE_01.glb',force='scene')
hatch=trimesh.load(OUT/'REACTOR_WALL_HATCH_OPEN_INSPECTION_01.glb',force='scene')

def place(dst,src,prefix,T,stroke=0):
 for node in src.graph.nodes_geometry:
  local,geom=src.graph[node]
  # Four real piston stages move +X in the approved source orientation.
  extra=np.eye(4)
  if stroke and prefix.startswith('PISTON'):
   stage=geom.split('__')[0]
   extra[0,3]={'STAGE1':6.6,'STAGE2':13.2,
    'STAGE3':19.8,'PUSHER':19.8}.get(stage,0)*stroke
  dst.add_geometry(src.geometry[geom],
   geom_name=f'{prefix}_{node}_{geom}',transform=T@extra@local)

def rotation_from_out(dir):
 d=np.asarray(dir,float);d/=np.linalg.norm(d)
 toward=-d;up=np.array((0,1,0),float)
 return np.stack((toward,up,np.cross(toward,up)),axis=1)

def build_context(show_heads=True):
 c=trimesh.Scene();iden=np.eye(4)
 for source,name in ((check,'NEW_MODEL_07'),(sidewall,'APPROVED_SIDE'),
                     (rear,'APPROVED_BACK'),(grille,'APPROVED_GRILLES')):
  place(c,source,name,iden)
 if show_heads:
  radial=[('UPPER',(0,0,1)),('LEFT',(-1,0,0)),
          ('RIGHT',(1,0,0)),('LOWER_LEFT',(-.72,0,-.694)),
          ('LOWER_RIGHT',(.72,0,-.694)),('LOWER',(0,0,-1))]
  for label,dir0 in radial:
   d=np.asarray(dir0,float);d/=np.linalg.norm(d)
   R=rotation_from_out(d)
   T=np.eye(4);T[:3,:3]=R;T[:3,3]=d*16.17+(0,-2.7,0)
   place(c,emitter,'EMITTER_'+label,T)
   T=np.eye(4);T[:3,:3]=R;T[:3,3]=d*24.5+(0,-2.7,0)
   place(c,piston,'PISTON_'+label,T,stroke=1)
   if label in ('LEFT','RIGHT'):
    place(c,hatch,'APPROVED_HATCH_'+label,T)
 return c

def cam(eye,target):
 eye=np.asarray(eye,float);target=np.asarray(target,float)
 f=target-eye;f/=np.linalg.norm(f)
 r=np.cross(f,(0,0,1));r/=np.linalg.norm(r)
 up=np.cross(r,f)
 T=np.eye(4);T[:3,:3]=np.stack((r,up,-f),axis=1);T[:3,3]=eye
 return T

def render(s,eye,target,fov,width=1060,height=675):
 p=pyrender.Scene.from_trimesh_scene(s,
  bg_color=[.014,.017,.026,1.],ambient_light=[.12,.13,.16])
 for loc,rgb,intens in [((-22,-24,22),(.79,.88,1.),530),
                        ((20,-17,9),(.65,.83,1.),455),
                        ((0,-11,4),(.79,.89,1.),165),
                        ((-14,9,-14),(.55,.70,1.),180)]:
  pose=np.eye(4);pose[:3,3]=loc
  p.add(pyrender.PointLight(color=np.array(rgb),intensity=intens),pose=pose)
 p.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)),pose=cam(eye,target))
 r=pyrender.OffscreenRenderer(width,height)
 image,_=r.render(p,flags=pyrender.RenderFlags.RGBA);r.delete()
 return Image.fromarray(image,'RGBA').convert('RGB')
main=render(build_context(True),(0,-40,6),(0,-1,0),66)
side=render(build_context(True),(-35,-29,20),(-13,-3,2),68)
solo=render(build_context(False),(0,-38,8),(0,0,0),70)
# A bounded QA sheet; not a promise of in-Studio lighting or game effects.
board=Image.new('RGB',(1770,1260),(12,17,27));draw=ImageDraw.Draw(board)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
head=ImageFont.truetype(bold,29);sub=ImageFont.truetype(font,17)
small=ImageFont.truetype(font,15)
def panel(im,x,y,w,h,label):
 r=ImageOps.contain(im,(w-6,h-6),Image.Resampling.LANCZOS)
 board.paste(r,(x+(w-r.width)//2,y+(h-r.height)//2))
 draw.rectangle((x,y,x+w,y+h),outline=(69,87,109),width=2)
 draw.text((x+14,y+14),label,font=sub,fill=(245,249,252),
  stroke_width=2,stroke_fill=(4,7,13))
draw.text((32,16),'MODEL 07 REV02 / MAVİ-GRİ ÇATI + ZEMİN SERVİS YUVALARI',
 font=head,fill=(240,245,250))
draw.text((33,60),'Yedi onaylı GLB DEĞİŞMEDİ. Yeni gerçek delikler, üst/alt geçit, çapraz alt mafsallar ve gerçek çelik ışık kanalları.',
 font=sub,fill=(175,192,213))
panel(main,28,101,841,515,'Altı onaylı yayıcı ve piston • merkezden ÇALIŞMA POZU (render)')
panel(side,898,101,841,515,'Açılı görünüm • çatıda delik, tabanda delik, alt çapraz montaj')
panel(solo,28,640,1119,545,'YALNIZ YENİ 3B GLB + onaylı kahverengi metal duvar • yayıcı kopyaları gizli')
# Video-start frames are the ONLY image comparator in this sheet: camera
# and bright control room differ from the offline chamber-only render.
ref=Image.open(ROOT/'.cache/references/keyframes/050s.png').convert('RGB')
panel(ref,1170,640,568,355,'360p açılış / 00:50 • 6 fiziksel başlık, mavi çelik')
draw.text((1178,1018),'Eski onaylı KAHVERENGİ arka duvar',font=small,fill=(182,201,222))
draw.text((1178,1045),'burada değiştirilmedi: görünür farktır.',font=small,fill=(182,201,222))
draw.text((30,1217),f'YENİ GLB: {len(check.geometry)} mesh  •  {tris:,} üçgen  •  {GLB.stat().st_size/1e6:.2f} MB  •  KURULMADI; canlı Play, ses ve ışık doğrulaması bekliyor.',
 font=small,fill=(162,184,207))
PRE=OUT/(NAME+'_ONAY.png');board.save(PRE,optimize=True)
print('MODEL',GLB,GLB.stat().st_size,'bytes;',len(check.geometry),'meshes;',tris,'triangles')
print('PREVIEW',PRE,PRE.stat().st_size,'bytes')
