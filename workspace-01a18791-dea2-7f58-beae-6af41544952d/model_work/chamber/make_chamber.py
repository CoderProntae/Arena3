#!/usr/bin/env python3
"""Third reference-guided original 3D asset: the octagonal containment chamber.

Real angled wall geometry with UV-textured paint/wear and recessed inset vents,
wall mounting plates, warnings, rails, conduits and grilles. Not a collection
of untextured Roblox Parts. This is an offline approval model, not in Studio.
Reference: user uploads image-3 and image-8. Unseen rear/side geometry is an
original mechanical interpolation, never claimed to be an exact hidden match.
"""
from __future__ import annotations
import os,sys,math,random
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps
os.environ['PYOPENGL_PLATFORM']='egl'
sys.path[:0]=['/home/user/.cache/modeldeps','/home/user/.cache/modelrender']
import trimesh,pyrender
ROOT=Path('/home/user');OUT=ROOT/'model_exports';OUT.mkdir(exist_ok=True)
DBG=ROOT/'.cache/model_debug';DBG.mkdir(parents=True,exist_ok=True)
RAND=random.Random(834523);NRNG=np.random.default_rng(675453)


def worn_texture(rgb,seed,contrast=1.0):
    rng=np.random.default_rng(seed);h=w=1024
    # Noise at three separate spatial wavelengths makes old painted metal,
    # not a flat or overly pastel single-color plane.
    lo=np.uint8(rng.integers(0,256,(48,48)))
    mid=np.uint8(rng.integers(0,256,(220,220)))
    low=np.asarray(Image.fromarray(lo,'L').resize((w,h),Image.Resampling.BICUBIC),float)-128
    med=np.asarray(Image.fromarray(mid,'L').resize((w,h),Image.Resampling.BILINEAR),float)-128
    fine=rng.standard_normal((h,w))
    pat=low*.38+med*.24+fine*8
    base=np.zeros((h,w,3),float);base[:]=rgb
    base+=pat[:,:,None]*np.array([.57,.27,.17])*contrast
    grit=rng.random((h,w))<.006
    base[grit]*=rng.uniform(.35,.8)
    base=np.uint8(np.clip(base,1,254));img=Image.fromarray(base,'RGB')
    d=ImageDraw.Draw(img,'RGBA')
    for _ in range(240):
        x=rng.integers(0,w);y=rng.integers(0,h)
        length=int(rng.integers(4,132));alpha=int(rng.integers(7,30))
        d.line((x,y,x+length,y+int(rng.integers(-2,3))),
               fill=(15,18,25,alpha),width=int(rng.integers(1,3)))
    return img

RUST=worn_texture((122,48,27),106,.68)
ORANGE=worn_texture((157,69,29),102,.71)
COBALT=worn_texture((29,29,52),103,.64)
GRAPHITE=worn_texture((39,39,42),105,.45)

def make_hazard():
    im=worn_texture((31,31,36),151,.30).crop((0,0,1024,256))
    d=ImageDraw.Draw(im,'RGBA')
    for j in range(-5,18):
        x=j*82
        d.polygon([(x,256),(x+63,256),(x+135,0),(x+72,0)],fill=(236,86,29,250))
    # thin dust on the paint, rather than a child-game yellow-black decal
    for _ in range(180):
        x=RAND.randrange(1024);y=RAND.randrange(256)
        d.line((x,y,x+RAND.randrange(3,38),y),fill=(25,26,27,53),width=1)
    return im
HAZARD=make_hazard()

def make_sign():
    im=Image.new('RGB',(1024,512),(19,21,28));d=ImageDraw.Draw(im)
    for x in range(0,1024,11):
        d.line((x,2,x+102,512),fill=(25,26,32),width=3)
    d.rectangle((19,17,1004,494),outline=(75,64,61),width=8)
    try:
        a=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',56)
        b=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',87)
    except OSError:a=b=ImageFont.load_default()
    d.text((345,131),'SL - 02',font=a,fill=(190,73,40))
    d.text((205,250),'Containment',font=b,fill=(190,96,49))
    return im
SIGN=make_sign()

def mat(name,rgb,metal=.4,rough=.67,emit=(0,0,0),image=None):
    return trimesh.visual.material.PBRMaterial(name=name,
      baseColorFactor=[*((255,255,255) if image is not None else rgb),255],
      baseColorTexture=image,metallicFactor=metal,roughnessFactor=rough,
      emissiveFactor=emit,doubleSided=True)
MATS={
 'rust':mat('01 - Patinated red containment metal',(255,255,255),.37,.76,image=RUST),
 'orange':mat('02 - Burnished orange overhead',(255,255,255),.38,.73,image=ORANGE),
 'cobalt':mat('03 - Blue-black smoke-stained panels',(255,255,255),.34,.78,image=COBALT),
 'graphite':mat('04 - Weathered black wall panels',(255,255,255),.55,.70,image=GRAPHITE),
 'hazard':mat('05 - Baked worn warning strip',(255,255,255),.15,.80,image=HAZARD),
 'sign':mat('06 - Containment zone plate',(255,255,255),.28,.73,image=SIGN),
 'rim':mat('07 - Oxidized dark structural alloy',(63,54,59),.68,.57),
 'black':mat('08 - Dark recessed vents',(11,17,29),.39,.86),
 'grille':mat('09 - Charcoal brushed grille',(58,67,78),.61,.63),
 'slit':mat('10 - Deep cobalt vent shadows',(20,43,72),.21,.84),
 'chrome':mat('11 - Cut brushed edges',(145,133,129),.73,.43),
 'amber':mat('12 - Rusted heating seam',(178,60,24),.16,.63,(.40,.025,.004)),
 'red_light':mat('13 - Narrow red signal lamp',(203,46,26),.08,.31,(.72,.025,.009)),
 'cold_light':mat('14 - Roof optical strip',(146,171,216),.06,.28,(.48,.54,.72)),
}
# Geometry: separate named damage zones, each material is one indexed GLB mesh.
GEOM={}
def add_faces(zone,material,pts,faces,uv=None):
    pts=np.asarray(pts,float);fs=np.asarray(faces,int)
    if uv is None:uv=np.zeros((len(pts),2),float)
    uv=np.asarray(uv,float)
    b=GEOM.setdefault((zone,material),[[],[],[]])
    k=sum(len(x) for x in b[0]);b[0].append(pts);b[1].append(fs+k);b[2].append(uv)

def quad(zone,material,a,b,c,d,uv=((0,0),(1,0),(1,1),(0,1))):
    add_faces(zone,material,[a,b,c,d],[(0,1,2),(0,2,3)],uv)

def stick(a,b,r,zone,material,sections=8):
    a=np.asarray(a,float);b=np.asarray(b,float);v=b-a;L=np.linalg.norm(v)
    if L<1.e-4:return
    m=trimesh.creation.cylinder(radius=r,height=L,sections=sections)
    m.apply_transform(trimesh.geometry.align_vectors((0,0,1),v/L))
    m.apply_translation((a+b)*.5)
    add_faces(zone,material,m.vertices,m.faces)

def line_box(cx,cy,cz,sx,sy,sz,zone,material):
    m=trimesh.creation.box(extents=(sx,sy,sz))
    m.apply_translation((cx,cy,cz));add_faces(zone,material,m.vertices,m.faces)

# Actual octagonal inner surface; not an outer rectangular map around a cube.
profile=[(-15.5,22),(15.5,22),(24.5,12.5),(24.5,-12.5),
         (15,-22),(-15,-22),(-24.5,-12.5),(-24.5,12.5)]
front,back=-8.5,15

def segment_wall(p,q,low,high,matname,zone='INNER_SHELL'):
    P=np.asarray(p,float);Q=np.asarray(q,float)
    A=P+(Q-P)*low;B=P+(Q-P)*high
    # Long inner face, textured by distance along physical wall and depth.
    x1,z1=A;x2,z2=B
    quad(zone,matname,(x1,front,z1),(x2,front,z2),(x2,back,z2),(x1,back,z1),
         uv=((.05,.0),(.88,.0),(.88,.94),(.05,.94)))

for i in range(len(profile)):
    p,q=profile[i],profile[(i+1)%len(profile)]
    if i in (0,1,7):
        segment_wall(p,q,0,1,'orange' if i!=0 else 'graphite','ROOF' if i==0 else 'UPPER_SHELL')
    elif i in (3,4,5):
        segment_wall(p,q,0,1,'cobalt' if i!=4 else 'graphite','FLOOR' if i==4 else 'LOWER_SHELL')
    else:
        # Large red side walls with a smoky black-blue toe and orange upper rim.
        segment_wall(p,q,0,.26,'rust')
        segment_wall(p,q,.26,.76,'rust')
        segment_wall(p,q,.76,1,'cobalt')
        for t in (.26,.76):
            x,z=np.asarray(p)+(np.asarray(q)-p)*t
            stick((x,front,z),(x,back,z),.09,'FRAME','rim')
    stick((p[0],front,p[1]),(p[0],back,p[1]),.16,'FRAME','rim',sections=8)
    # Continuous front and rear steel lip follows the octagon profile.
    stick((p[0],front,p[1]),(q[0],front,q[1]),.15,'FRAME','rim')
    stick((p[0],back,p[1]),(q[0],back,q[1]),.13,'FRAME','rim')

# Back cap: wall isn't invisible behind the six-way star. Faceted base with
# panel overlays, real buttresses, relief vents, beam feeds and cable stems.
quad('BACK_WALL','rust',(-22.3,back,-12.1),(22.3,back,-12.1),
     (22.3,back,13.0),(-22.3,back,13.0))
quad('BACK_WALL','orange',(-15.5,back,12.9),(15.5,back,12.9),
     (15.5,back,22),(-15.5,back,22))
quad('BACK_WALL','cobalt',(-15.3,back,-22),(15.3,back,-22),
     (15.3,back,-11.9),(-15.3,back,-11.9))
for s in (-1,1):
    # Those trapezoids fill the octagon's four visible back chamfer gaps.
    quad('BACK_WALL','rust', (s*15.5,back,22),(s*24.5,back,12.5),
         (s*22.3,back,12.5),(s*15.5,back,13))
    quad('BACK_WALL','cobalt',(s*24.5,back,-12.5),(s*15,back,-22),
         (s*15,back,-12),(s*22.3,back,-12))
# Tall central rear maintenance bay visible between dual vent towers.
quad('BACK_BAY','graphite',(-4.5,14.68,-10.8),(4.5,14.68,-10.8),
     (4.5,14.68,11.0),(-4.5,14.68,11.0))
quad('BACK_BAY','rust',(-3.6,14.61,-8.3),(3.6,14.61,-8.3),
     (3.6,14.61,8.1),(-3.6,14.61,8.1))
for x in (-4.2,4.2):stick((x,14.50,-10),(x,14.50,10),.12,'BACK_BAY','rim')
for z in (-10.7,10.8):stick((-4.5,14.5,z),(4.5,14.5,z),.11,'BACK_BAY','rim')

# Two banks of tall inset, round-topped grille windows (3 + 3), not painted
# rectangles. Their actual cavity is dark and each has individually raised bars.
for side in (-1,1):
    bank_x=side*10.1
    line_box(bank_x,14.38,3.6,9.0,.46,16.8,'BACK_VENTS','rim')
    line_box(bank_x,14.07,3.5,8.4,.20,15.9,'BACK_VENTS','black')
    for u in (-2.63,0,2.63):
        xc=bank_x+u
        # Shallow arched top cap, actually curved in the silhouette.
        arch=[]
        for theta in np.linspace(0,math.pi,9):
            arch.append((xc+1.02*math.cos(theta),13.84,10.2+1.02*math.sin(theta)))
        poly=[(xc-1.02,13.84,-3.9),(xc+1.02,13.84,-3.9)]+arch
        verts=poly+[(xc,13.84,4)]
        c=len(verts)-1
        faces=[(c,i,i+1) for i in range(len(poly)-1)]
        add_faces('BACK_VENTS','slit',verts,faces)
        for x in (xc-.99,xc+.99):stick((x,13.76,-3.7),(x,13.76,10.1),.07,'VENT_GRILLES','grille',sections=6)
        for z in np.arange(-2.9,10.0,1.55):
            stick((xc-.91,13.69,z),(xc+.91,13.69,z),.047,'VENT_GRILLES','grille',sections=6)
    for z in (-4.6,11.5):stick((bank_x-4.45,13.73,z),(bank_x+4.45,13.73,z),.12,'VENT_GRILLES','rim')

# Side mounting stations. The hollow-looking orange patch is a *mount recess*,
# not a glowing reactor shutter; no plate ever closes the center of the scene.
for side in (-1,1):
    x=side*24.50;xb=x-side*.24;xl=x-side*.34
    quad('SIDE_STATION','graphite',(xb,-3.3,-9.5),(xb,10,-9.5),
         (xb,10,9.5),(xb,-3.3,9.5))
    quad('SIDE_STATION','rust',(xl,-2.7,-8.85),(xl,9.25,-8.85),
         (xl,9.25,8.85),(xl,-2.7,8.85))
    for z in (-8.40,8.40):
        quad('WARNINGS','hazard',(xl-side*.02,-2.2,z-.67),
             (xl-side*.02,8.9,z-.67),(xl-side*.02,8.9,z+.67),
             (xl-side*.02,-2.2,z+.67),
             uv=((0,0),(1,0),(1,1),(0,1)))
    # Small equipment label exactly above the emitter root (not on nozzle).
    sign_uv=((1,0),(0,0),(0,1),(1,1)) if side==1 else ((0,0),(1,0),(1,1),(0,1))
    quad('STATION_LABELS','sign',(xl-side*.06,.35,3.60),
         (xl-side*.06,6.80,3.60),(xl-side*.06,6.80,7.20),
         (xl-side*.06,.35,7.20),uv=sign_uv)
    quad('SIDE_STATION','black',(xl-side*.05,-.55,-2.61),
         (xl-side*.05,5.43,-2.61),(xl-side*.05,5.43,2.63),
         (xl-side*.05,-.55,2.63))
    quad('SIDE_STATION','amber',(xl-side*.08,-.1,-2.08),
         (xl-side*.08,4.96,-2.08),(xl-side*.08,4.96,2.10),
         (xl-side*.08,-.1,2.10))
    for y in (-3.25,10.0):stick((xb,y,-9.4),(xb,y,9.4),.13,'FRAME','rim')
    for z in (-9.45,9.45):stick((xb,-3.3,z),(xb,10,z),.13,'FRAME','rim')
    # Mounted plate fasteners are distinct low-poly physical metal heads.
    for y in (-2.78,1.4,5.8,9.48):
        for z in (-8.92,8.92):
            stick((xb-side*.04,y,z),(xb-side*.18,y,z),.072,
                  'STATION_FASTENERS','chrome',sections=6)
    # Extremely narrow corner warning pillars, matching the reference pair.
    line_box(side*22.7,11.25,4.2,.35,.50,14.8,'LAMPS','rim')
    line_box(side*22.7,10.82,8.12,.23,.20,5.6,'LAMPS','red_light')

# Back-wall door columns, top grilles and fluorescent roof conduit contour.
for side in (-1,1):
    x=side*4.9
    line_box(x,14.5,10.7,.63,.55,2.8,'BACK_BAY','rim')
    line_box(x,14.13,10.9,.28,.17,1.8,'LAMPS','red_light')
    for center_x in (side*6.8,side*10.9):
        # reference has pairs of small angled high ventilation grates
        line_box(center_x,14.64,16.2,2.7,.3,2.5,'UPPER_VENTS','rim')
        line_box(center_x,14.45,16.2,2.3,.24,2.1,'UPPER_VENTS','black')
        for zz in (15.5,15.9,16.3,16.7):
            stick((center_x-1.07,14.29,zz),(center_x+1.07,14.29,zz),
                  .043,'UPPER_VENTS','grille')
# Seven structural raceways turning with the top corners, each behind upper
# emitter. They are thin metal and occasional white service-light segments.
for i in range(5):
    yy=-5.7+i*1.12
    for j in range(len(profile)):
        if j not in (0,1,7):continue
        a=np.asarray(profile[j],float);b=np.asarray(profile[(j+1)%len(profile)],float)
        delta=np.array([0,-.015*(i+1)])
        stick((a[0],yy,a[1]+delta[1]),(b[0],yy,b[1]+delta[1]),
              .056,'CEILING_RACEWAYS','rim',sections=7)
for side in (-1,1):
    for xx in (side*6.2,side*13.0):
        stick((xx,-6.1,21.69),(xx,12.7,21.69),.048,'CEILING_RACEWAYS','cold_light',sections=7)
# Thin tiered zig-zag overhead light track that actually turns the back corners.
# It is split before the central overhead emitter, as in the uploaded frames.
for level in range(4):
    zz=20.62-level*.47
    for side in (-1,1):
        kind='cold_light' if level in (0,3) else 'rim'
        path=[(side*15.5,14.33,zz+.54),(side*11.25,14.33,zz),
              (side*7.8,14.33,zz),(side*6.55,14.33,zz-.39),
              (side*3.65,14.33,zz-.39)]
        for a,b in zip(path,path[1:]):stick(a,b,.050,'CEILING_RACEWAYS',kind,sections=7)
# Floor hazard edge sits on the FLOOR, not an added barricade before the core.
for i in range(-8,8):
    x=i*2
    pts=[(x,-7.7,-21.86),(x+1.05,-7.7,-21.86),
         (x+2.05,-6.18,-21.86),(x+1.,-6.18,-21.86)]
    add_faces('FLOOR_WARNINGS','amber',pts,[(0,1,2),(0,2,3)])
for yy in (-5,1,7,12.7):
    stick((-14.5,yy,-21.77),(14.5,yy,-21.77),.065,'FLOOR_RAILS','rim')
# Long exterior side cable runs remain inside the octagonal wall boundaries.
for side in (-1,1):
    for z in (11.60,-11.60):
        stick((side*24.3,front,z),(side*24.3,back,z),.082,'CONDUITS','rim')
    for yy in (-6,0,6,12):
        for zz in (11.5,-11.5):
            line_box(side*24.23,yy,zz,.18,.24,.48,'CONDUITS','chrome')

# Export per damage zone/material. Curved surfaces and UV paint remain real 3D
# glTF mesh data, not Roblox block Part counts disguised as detail.
scene=trimesh.Scene();tris=0
for (zone,matname),(vl,fl,uvl) in GEOM.items():
    v=np.concatenate(vl);f=np.concatenate(fl);uv=np.concatenate(uvl)
    mesh=trimesh.Trimesh(vertices=v,faces=f,process=False)
    mesh.visual=trimesh.visual.texture.TextureVisuals(uv=uv,material=MATS[matname])
    scene.add_geometry(mesh,geom_name=f'{zone}__{matname}')
    tris+=len(f)
glb=OUT/'REACTOR_CHAMBER_SHELL_01.glb';glb.write_bytes(scene.export(file_type='glb'))

# The viewer sees a direct render of the new GLB from the would-be observation
# window. There is no inaccessible external texture or pasted environment art.
def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    right=np.cross(f,[0,0,1.]);right/=np.linalg.norm(right)
    up=np.cross(right,f)
    pose=np.eye(4);pose[:3,:3]=np.stack([right,up,-f],axis=1);pose[:3,3]=eye
    return pose

def lights(view):
    for pos,color,power in [((-19,-12,14),(1,.39,.11),420),
                            ((18,4,13),(1,.30,.14),350),
                            ((0,-1,0),(.31,.20,.86),220),
                            ((0,-16,19),(.78,.71,.65),95)]:
        pose=np.eye(4);pose[:3,3]=pos
        view.add(pyrender.PointLight(color=np.asarray(color),intensity=power),pose=pose)

rscene=pyrender.Scene.from_trimesh_scene(scene,bg_color=[.008,.006,.018,1],
                                         ambient_light=[.27,.23,.21])
lights(rscene)
r=pyrender.OffscreenRenderer(1440,850)
def render(view,eye,angle):
    node=view.add(pyrender.PerspectiveCamera(yfov=math.radians(angle)),pose=look(eye,(0,1,0)))
    a,_=r.render(view,flags=pyrender.RenderFlags.RGBA)
    view.remove_node(node)
    return Image.fromarray(a,'RGBA').convert('RGB')
room=render(rscene,(0,-34,2),62)
angle=render(rscene,(9,-30,7),65)
r.delete()
room.save(DBG/'REACTOR_CHAMBER_ISOLATED_01.png')
angle.save(DBG/'REACTOR_CHAMBER_ANGLE_01.png')

# Optional off-line context: already-reviewed emitter and provisional core.
# It illustrates fit, not a claim of installed Studio effects or final test.
combine=trimesh.Scene()
for k,g in scene.geometry.items():combine.add_geometry(g,geom_name='CHAMBER_'+k)
core=trimesh.load(OUT/'REACTOR_CORE_MANYETIK_01.glb',force='scene')
for k,g in core.geometry.items():combine.add_geometry(g,geom_name='CORE_'+k)
em=trimesh.load(OUT/'REACTOR_EMITTER_REV03.glb',force='scene')
dirs={'LEFT':(-1,0,0),'RIGHT':(1,0,0),'TOP':(0,0,1),
      'BOTTOM':(0,0,-1),'LOWER_LEFT':(-.72,0,-.694),
      'LOWER_RIGHT':(.72,0,-.694)}
for zone,v in dirs.items():
    d=np.asarray(v,float);d/=np.linalg.norm(d)
    T=trimesh.geometry.align_vectors((1,0,0),-d);T[:3,3]=d*(7.20+8.55)
    for k,g in em.geometry.items():combine.add_geometry(g,geom_name=f'{zone}_{k}',transform=T)
vv=pyrender.Scene.from_trimesh_scene(combine,bg_color=[.007,.005,.018,1],
                                    ambient_light=[.26,.21,.21])
lights(vv)
pose=np.eye(4);pose[:3,3]=[0,-2,1]
vv.add(pyrender.PointLight(color=np.array([.85,.55,1]),intensity=460),pose=pose)
r=pyrender.OffscreenRenderer(1440,850)
context=render(vv,(0,-34,2),62)
r.delete()
a=np.asarray(context,dtype=np.float32)
hot=Image.fromarray(np.uint8(np.clip((a-90)*1.5,0,255)),'RGB')
halo=np.asarray(hot.filter(ImageFilter.GaussianBlur(34)),dtype=float)
context=Image.fromarray(np.uint8(np.clip(a+.40*halo,0,255)),'RGB')
context.save(OUT/'REACTOR_CHAMBER_WITH_APPROVED_MODELS_01.png')

# Single approval sheet. Render pixels at top are from REAL GLB geometry; the
# two reference crops at bottom are the user's uploaded screenshots.
board=Image.new('RGB',(1900,1360),(13,17,27));d=ImageDraw.Draw(board)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',31)
    normal=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    foot=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
except OSError:title=normal=foot=ImageFont.load_default()
def panel(im,x,y,w,h,label):
    d.rectangle((x,y,x+w,y+h),fill=(24,29,42))
    obj=ImageOps.contain(im,(w,h),Image.Resampling.LANCZOS)
    board.paste(obj,(x+(w-obj.width)//2,y+(h-obj.height)//2))
    d.rectangle((x,y,x+w,y+h),outline=(72,80,104),width=2)
    d.text((x+14,y+12),label,font=normal,fill=(245,241,247),stroke_width=1,stroke_fill=(12,13,18))
d.text((44,26),'MODEL 03  /  REAKTÖR BÖLMESİ — TEKSTÜRLÜ 3B KABUK',font=title,fill=(239,244,252))
d.text((44,78),'Gerçek .glb geometrisi + gömülü yıpranmış metal dokular  •  Studio ekranı veya oynanış testi değildir',font=normal,fill=(178,191,211))
panel(room,44,117,1120,670,'Boş bölme — bu model tek başına')
panel(context,1183,117,671,670,'Bağlam — onaylı modeller + geçici çekirdek')
panel(angle,44,824,559,456,'Çapraz açı — derinlik / duvar hacmi')
ref=Image.open(ROOT/'model_work/reference_crops/ROOM_LEFT_1321.png').convert('RGB')
panel(ref,626,824,595,456,'Referans — sol duvar / hazard / yuva')
ref2=Image.open(ROOT/'model_work/reference_crops/ROOM_CENTER_1321.png').convert('RGB')
panel(ref2,1242,824,612,456,'Referans — arka duvar / tavan / menfez')
d.text((44,1309),f'GLB: {glb.stat().st_size/1e6:.2f} MB  •  {tris:,} üçgen  •  {len(scene.geometry)} adlandırılmış malzeme/hasar bölgesi',font=foot,fill=(175,188,209))
preview=OUT/'REACTOR_CHAMBER_MODEL_ONAY_01.png';board.save(preview,optimize=True)
print('EXPORT:',glb,'size',glb.stat().st_size,'meshes',len(scene.geometry),'triangles',tris)
print('PREVIEW:',preview)
