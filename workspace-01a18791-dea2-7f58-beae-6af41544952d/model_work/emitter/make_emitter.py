#!/usr/bin/env python3
"""Original, reference-guided 3D reactor emitter. Real triangle meshes, not Roblox Parts.

Axis is +X toward the star. Source images: uploads/image-3.png and image-7.png.
Shape/features modeled from visible evidence; unseen interior is an original design.
GLB contains separate named damage zones and real PBR/emissive materials.
"""
from __future__ import annotations
import os,sys,math,random
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops,ImageOps
sys.path.insert(0,'/home/user/.cache/modeldeps')
sys.path.insert(0,'/home/user/.cache/modelrender')
import trimesh
os.environ['PYOPENGL_PLATFORM']='egl'
import pyrender

ROOT=Path('/home/user')
OUT=ROOT/'model_exports'
OUT.mkdir(exist_ok=True)
RNG=random.Random(902142)
N=64
TAU=math.tau

# Lightly imperfect invented PBR palette. The geometry, not just a texture,
# makes the windows, stepped muzzle, flutes, cooling cage and rear chevrons.
def material(name, rgb, metallic=.5, rough=.45, emission=(0,0,0), alpha=1):
    r,g,b=rgb
    return trimesh.visual.material.PBRMaterial(
        name=name, baseColorFactor=[r,g,b,int(alpha*255)],
        metallicFactor=metallic, roughnessFactor=rough,
        emissiveFactor=[min(1.0,c) for c in emission],
        alphaMode='BLEND' if alpha<1 else 'OPAQUE', doubleSided=True)
MAT={
    'obsidian':material('01 - Carbonized graphite', (15,19,24),.67,.69),
    'body':material('02 - Weathered gunmetal casing',(36,42,47),.71,.62),
    'slate':material('03 - Dark titanium alloy',(47,53,61),.69,.53),
    'polished':material('04 - Brushed machined steel',(115,124,134),.75,.42),
    'silver':material('05 - Worn steel edges',(165,173,179),.76,.36),
    'bronze':material('06 - Heat-patina containment steel',(70,32,31),.60,.68),
    'soot':material('07 - Crevice and bore',(6,9,12),.32,.88),
    'amber':material('08 - Heated warning seam',(191,55,30),.39,.50,(.38,.045,.005)),
    'cyan':material('09 - Saturated high-energy ion',(23,167,218),.06,.27,(.005,.38,.86)),
    'cyan_core':material('10 - Deeper cobalt window interior',(16,85,128),.08,.39,(.00,.08,.22)),
    'cyan_shell':material('11 - Smoke-blue ion shield',(17,85,126),.07,.38,(.00,.035,.095),.22),
    'violet':material('11 - Deep indigo UV seam',(86,43,143),.19,.43,(.16,.025,.31)),
    'pink':material('12 - Fuchsia arc seam',(187,45,105),.23,.40,(.38,.012,.13)),
    'white':material('13 - Hot ion aperture',(198,208,217),.10,.30,(.70,.73,.83)),
}
# (damage-zone, material) -> list of individual mesh shells; concatenate each
# group into one actual mesh for an affordable Roblox MeshPart count.
GROUPS={}
def put(part, zone, mat):
    assert len(part.faces)>0
    GROUPS.setdefault((zone,mat),[]).append(part)


def shell(outer, inner, n=N, waver=None):
    """Spin an arbitrary hollow longitudinal profile about the real X axis."""
    contour=list(outer)+list(reversed(inner))
    verts=[]
    for k,(x,r) in enumerate(contour):
        for j in range(n):
            th=TAU*j/n
            rx=r*(waver(x,th) if waver else 1.0)
            verts.append((x,rx*math.cos(th),rx*math.sin(th)))
    faces=[];length=len(contour)
    for k in range(length):
        q=(k+1)%length
        for j in range(n):
            j1=(j+1)%n
            a=k*n+j;b=k*n+j1;c=q*n+j;d=q*n+j1
            faces.extend(((a,b,c),(b,d,c)))
    return trimesh.Trimesh(vertices=np.array(verts),faces=np.array(faces),process=False)


def annulus(x,r,thick=.12,width=.12,zone='HEAD',mat='silver',n=N):
    outer=[(x-thick/2,r-width*.24),(x-thick*.27,r+width*.5),
           (x+thick*.27,r+width*.5),(x+thick/2,r-width*.24)]
    inner=[(x-thick/2,r-width*.87),(x+thick/2,r-width*.87)]
    put(shell(outer,inner,n=n),zone,mat)


def cyl_between(a,b,r,zone,mat,sections=12):
    a=np.array(a,dtype=float);b=np.array(b,dtype=float)
    v=b-a; L=np.linalg.norm(v)
    if L<1.e-4:return
    m=trimesh.creation.cylinder(radius=r,height=L,sections=sections)
    T=trimesh.geometry.align_vectors((0,0,1),v/L)
    m.apply_transform(T);m.apply_translation((a+b)/2)
    put(m,zone,mat)


def bolt(x,r,th,zone='HEAD',mat='polished',size=.075):
    p=trimesh.creation.icosphere(subdivisions=1,radius=size)
    p.apply_translation([x,r*math.cos(th),r*math.sin(th)])
    put(p,zone,mat)


def sector_shell(x0,x1,r0,r1,theta0,theta1,zone,mat,nx=2,nt=18):
    """Curved, genuinely three-dimensional open aperture or machined vane."""
    # 2 radial surfaces, 2 axial ends and 2 angular ends of a swept wedge.
    vs=[]
    for radius in [r0,r1]:
        for i in range(nx+1):
            x=x0+(x1-x0)*i/nx
            for j in range(nt+1):
                t=theta0+(theta1-theta0)*j/nt
                vs.append((x,radius*math.cos(t),radius*math.sin(t)))
    row=nt+1; layer=(nx+1)*row
    fs=[]
    for k in [0,1]:
        off=k*layer
        for i in range(nx):
            for j in range(nt):
                a=off+i*row+j;b=a+1;c=a+row;d=c+1
                fs.extend(((a,b,c),(b,d,c)) if k else ((a,c,b),(b,c,d)))
    for i in range(nx):
        for j in (0,nt):
            a=i*row+j;b=(i+1)*row+j;c=layer+a;d=layer+b
            fs.extend(((a,b,c),(b,d,c)))
    for j in range(nt):
        for i in (0,nx):
            a=i*row+j;b=a+1;c=layer+a;d=c+1
            fs.extend(((a,b,c),(b,d,c)))
    return trimesh.Trimesh(vertices=np.asarray(vs),faces=np.asarray(fs),process=False)

# 1. Ventilated anchor set into an orange containment wall, not a blunt capped
# cylinder. Overlapping bevels and tapered concentric chevrons are true mesh.
put(shell([(-9.15,2.06),(-8.95,2.36),(-8.65,2.57),(-6.45,2.90),
           (-6.17,2.84)],
          [(-9.15,1.52),(-6.17,1.73)]),'TAIL','bronze')
put(shell([(-9.05,2.21),(-8.94,2.37),(-6.45,2.78),(-6.32,2.81)],
          [(-9.05,2.14),(-6.32,2.66)]),'TAIL','obsidian')
for j in range(7):
    x=-8.75+j*.39
    # Wavy axial offset makes proper nested V-shaped chevron collar edges.
    def vshape(_x,theta):return 1+.038*math.cos(2*theta)
    outer=[(x-.072,2.45+j*.039),(x-.018,2.54+j*.039),
           (x+.060,2.58+j*.039),(x+.09,2.53+j*.039)]
    inner=[(x-.072,2.40+j*.039),(x+.09,2.43+j*.039)]
    put(shell(outer,inner,waver=vshape),'TAIL','soot')
annulus(-6.34,2.96,.18,.22,'TAIL','polished')
annulus(-6.16,2.81,.075,.09,'TAIL','pink')

# 2. Ion cell: genuine cylindrical cut-outs, refractive-color glass segments,
# continuous photon rod, six cage beams and two polished hoop-seams.
put(shell([(-6.12,2.48),(-5.85,2.69),(-5.54,2.52)],
          [(-6.12,2.12),(-5.54,2.11)]),'WINDOW','silver')
put(shell([(-5.57,1.73),(-2.07,1.73)],[(-5.57,1.10),(-2.07,1.10)]),
    'WINDOW','cyan_core')
put(shell([(-5.65,2.01),(-2.02,2.01)],[(-5.65,1.94),(-2.02,1.94)]),
    'WINDOW','cyan_shell')
for i in range(6):
    th=TAU*i/6
    arc=TAU/6
    # Each window opening is a curved transparent pane, separated by thick
    # silver-magenta longitudinal girders, not one solid glowing pipe.
    put(sector_shell(-5.72,-2.23,2.35,2.39,th+.10,th+arc-.10,
                     'WINDOW','cyan_shell',nx=3,nt=9),'WINDOW','cyan_shell')
    for radius,mat,width in ((2.49,'polished',.115),(2.52,'pink',.046)):
        a=(-5.75,radius*math.cos(th),radius*math.sin(th))
        b=(-2.22,radius*math.cos(th),radius*math.sin(th))
        cyl_between(a,b,width,'WINDOW',mat,sections=10)
for x in (-5.75,-5.43,-2.64,-2.28):
    annulus(x,2.59,.16,.15,'WINDOW','polished')
for x in (-5.43,-2.63): annulus(x,2.68,.07,.055,'WINDOW','pink')
for th in np.arange(0,TAU,TAU/12):bolt(-5.76,2.66,float(th),'WINDOW',size=.065)

# 3. Stepped graphite primary reaction body, with dark seam recesses and
# longitudinal machined flutes. This part is not a featureless black cube.
put(shell([(-2.28,2.14),(-2.07,2.37),(-1.79,2.28),(-1.56,2.10),
           (1.95,2.10),(2.24,2.31),(2.60,2.30)],
          [(-2.28,1.45),(2.60,1.39)]),'BODY','body')
for x,r in [(-1.98,2.43),(-1.66,2.26),(1.98,2.21),(2.42,2.39)]:
    annulus(x,r,.09,.095,'BODY','slate')
for i in range(12):
    theta=TAU*i/12
    put(sector_shell(-1.5,1.9,2.105,2.141,theta+.105,theta+.148,
        'BODY','obsidian',nx=1,nt=2),'BODY','obsidian')
for x in (-1.27,1.69):
    for i in range(8):
        th=TAU*(i+.2)/8
        # A few recessed screw seats; sparse hardware avoids the toy dots.
        bolt(float(x),2.12,th,'BODY','soot',size=.072)
        bolt(float(x),2.156,th,'BODY','polished',size=.03)
# Uneven hairline tool-scoring has 3D relief; wear is not a flat overlay.
for _ in range(30):
    x=RNG.uniform(-1.36,1.55);th=RNG.uniform(0,TAU)
    le=RNG.uniform(.07,.31);r=2.146
    a=(x,r*math.cos(th),r*math.sin(th))
    b=(x+le,r*math.cos(th+.013),r*math.sin(th+.013))
    cyl_between(a,b,.006,'BODY','soot',sections=5)
# 4. Photonic focus assembly: independently breakable, layered multi-ring
# machined support, stepped insulating collars and radial seam fasteners.
put(shell([(2.48,2.32),(2.69,2.59),(3.02,2.70),
           (4.37,2.70),(4.67,2.51),(5.06,2.46)],
          [(2.48,1.49),(5.06,1.54)]),'HEAD','slate')
for x in (2.73,2.94,3.30,3.72,4.16,4.45,4.79):
    annulus(x,2.73,.125,.17,'HEAD','silver' if x in (2.73,4.79) else 'polished')
for x in (3.11,4.34):
    annulus(x,2.78,.042,.043,'HEAD','violet')
annulus(3.93,2.78,.053,.058,'HEAD','amber')
for i in range(12):
    t=TAU*i/12
    cyl_between((3.0,2.51*math.cos(t),2.51*math.sin(t)),
                (4.49,2.51*math.cos(t),2.51*math.sin(t)),
                .044,'HEAD','body',sections=7)
for x in (2.96,4.49):
    for i in range(12):bolt(x,2.80,TAU*i/12,'HEAD',size=.066)

# 5. A visibly hollow focusing mouth, iris, cage and tiny calibration rails.
# Dark inner tunnel is an actual annular shell with a hole, not a black decal.
put(shell([(4.96,2.05),(5.19,2.26),(5.49,2.18),(5.69,1.72),
           (6.54,1.73),(6.90,1.51),(7.53,1.51),(7.86,1.59),
           (8.24,1.43),(8.42,1.25)],
          [(4.96,1.13),(8.42,.84)]),'NOZZLE','polished')
put(shell([(5.75,1.75),(6.80,1.75),(7.75,1.50),(8.45,1.19)],
          [(5.75,1.61),(8.45,1.10)]),'NOZZLE','body')
put(shell([(6.98,1.12),(8.55,1.12)],[(6.98,.82),(8.55,.78)]),
    'NOZZLE','soot')
for x,r in ((5.25,2.30),(5.59,1.90),(6.02,1.86),(6.45,1.83),
            (6.87,1.71),(7.18,1.66),(7.52,1.64),(7.89,1.70),
            (8.22,1.57)):
    annulus(x,r,.11,.115,'NOZZLE','silver' if x in (5.25,7.89,8.22) else 'polished')
for x,r in ((7.16,1.68),(7.54,1.64),(8.11,1.59)):
    annulus(x,r,.046,.046,'NOZZLE','pink')
annulus(8.44,1.32,.15,.13,'NOZZLE','white')
annulus(8.49,1.09,.045,.09,'NOZZLE','cyan')
# Eight small separate concentric teeth with a dark central pupil.
for i in range(8):
    th=TAU*i/8
    put(sector_shell(8.45,8.51,.81,1.03,th+.10,th+.61,
                     'NOZZLE','polished',nx=1,nt=3),'NOZZLE','polished')
# Real hand-sized inner white optic, recessed into the nozzle and surrounded
# by thin transport rods. It is intentionally narrower than the outer muzzle.
put(shell([(8.05,.41),(8.28,.52),(8.43,.42)],
          [(8.05,.18),(8.43,.16)]),'OPTIC','cyan')
for i in range(6):
    th=TAU*i/6
    r=1.86
    cyl_between((5.73,r*math.cos(th),r*math.sin(th)),
                (8.35,r*.72*math.cos(th),r*.72*math.sin(th)),
                .061,'NOZZLE','silver',sections=8)
for i in range(8):bolt(5.26,2.26,TAU*i/8,'HEAD','silver',size=.069)

# External articulated antenna / beam-stabilizer rods: requested revision.
# They sit beyond the nozzle silhouette, project past its lip, and remain
# separately named so they can snap or bend during a genuine MELTDOWN.
ANTENNA_ANGLES=tuple(math.radians(deg) for deg in (35,105,215,305))
for index,th in enumerate(ANTENNA_ANGLES):
    # Four independent prongs around the bore; a slight angular stagger
    # prevents two physically present antennas merging in the profile view.
    # Alternating arm lengths keep these rails from reading as a toy comb.
    radius=2.29 if index%2==0 else 2.34
    y,z=radius*math.cos(th),radius*math.sin(th)
    cyl_between((4.84,y,z),(5.42,y,z),.15,'ANTENNA','body')
    cyl_between((5.23,y,z),(8.94,y,z),.084,'ANTENNA','polished',sections=10)
    cyl_between((8.76,y,z),(9.16,y,z),.097,'ANTENNA','silver',sections=9)
    cyl_between((9.12,y,z),(9.29,y,z),.047,'ANTENNA','soot',sections=9)
    bolt(9.28,radius,th,'ANTENNA','silver',size=.053)
# Diagonal root braces are short and dark, leaving the cyan muzzle readable.
for th in ANTENNA_ANGLES:
    cyl_between((5.10,2.53*math.cos(th),2.53*math.sin(th)),
                (5.76,2.30*math.cos(th),2.30*math.sin(th)),
                .08,'ANTENNA','body',sections=8)

# 6. Final cooling/control spokes on the tail cell and a few asymmetrical
# engraved witness marks prevent the object reading as generic cylinders.
for j in range(3):
    t=.48+j*TAU/3
    cyl_between((-5.38,2.57*math.cos(t),2.57*math.sin(t)),
                (-2.61,2.57*math.cos(t),2.57*math.sin(t)),
                .074,'WINDOW','silver',sections=8)
for x in (-1.14,-.82,1.11,1.48):
    put(sector_shell(x,x+.055,2.142,2.16,.27,.97,'BODY','slate',nx=1,nt=6),
        'BODY','slate')

# Export a *single* multicomponent GLB, preserving meaningful names for
# replacing one head and blacking out one window during the damage sequence.
scene=trimesh.Scene()
geo_names=[];faces_total=0;tri_groups={}
for (zone,mat),items in GROUPS.items():
    mesh=trimesh.util.concatenate(items)
    mesh.remove_unreferenced_vertices()
    # TextureVisuals carries the actual glTF PBR material, not only RGB vertex
    # colors; materials also preserve (glass) transparency and emission.
    mesh.visual=trimesh.visual.texture.TextureVisuals(
        uv=np.zeros((len(mesh.vertices),2)), material=MAT[mat])
    name=f'{zone}__{mat}'
    scene.add_geometry(mesh,geom_name=name)
    geo_names.append(name);faces_total+=len(mesh.faces)
    tri_groups[name]=len(mesh.faces)
GLB=OUT/'REACTOR_EMITTER_REV03.glb'
GLB.write_bytes(scene.export(file_type='glb'))
OBJ=ROOT/'.cache/model_obj/REACTOR_EMITTER_REV03.obj'
OBJ.parent.mkdir(parents=True,exist_ok=True)
# Optional interchange file is disposable; only the GLB is kept in snapshots.
OBJ.write_text(trimesh.exchange.obj.export_obj(scene),encoding='utf-8')

# Render FROM THE EXACT SAME MESHES. No generated reference-art substitutions.
# A mild photographed blue/pink rim + pearl key approximates the game's warm
# room/cool emitter contrast; preview is deliberately not the game's effects.
render_scene=pyrender.Scene.from_trimesh_scene(scene,
    bg_color=np.array([0.014,0.017,0.025,1.0]),ambient_light=[.17,.19,.22])

def look_at(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    forward=(target-eye);forward/=np.linalg.norm(forward)
    right=np.cross(forward,[0,0,1.]);right/=np.linalg.norm(right)
    up=np.cross(right,forward)
    M=np.eye(4);M[:3,0]=right;M[:3,1]=up;M[:3,2]=-forward;M[:3,3]=eye
    return M
for pos,rgb,intensity in [
    ((-1,-8,11),(.72,.81,.91),72.),
    ((7,4,7),(.12,.48,.84),47.),
    ((-8,-2,3),(1.,.20,.045),47.),
]:
    l=pyrender.PointLight(color=np.asarray(rgb,float),intensity=intensity)
    render_scene.add(l,pose=np.eye(4) if False else
        np.array([[1,0,0,pos[0]],[0,1,0,pos[1]],[0,0,1,pos[2]],[0,0,0,1]],float))
renderer=pyrender.OffscreenRenderer(1060,640)

def render(eye,center=(0,0,0),yfov=math.radians(43)):
    node=render_scene.add(pyrender.PerspectiveCamera(yfov=yfov),pose=look_at(eye,center))
    rgb,depth=renderer.render(render_scene,flags=pyrender.RenderFlags.RGBA)
    render_scene.remove_node(node)
    art=Image.fromarray(rgb,'RGBA').convert('RGB')
    # Filmic bloom ONLY in preview; emitter geometry stays the GLB above.
    bloom=art.point(lambda v:max(0,(v-150)*1.1))
    bloom=bloom.filter(ImageFilter.GaussianBlur(16))
    art=ImageChops.add(art,bloom,scale=1.15)
    return art
side=render((0,-24,9),(.2,0,0),yfov=math.radians(30))
iso=render((13,-16,9),(0,0,0),yfov=math.radians(35))
front=render((22,0,0),(5.7,0,0),yfov=math.radians(27))
renderer.delete()
DEBUG=ROOT/'.cache/model_debug';DEBUG.mkdir(parents=True,exist_ok=True)
side.save(DEBUG/'REACTOR_EMITTER_SIDE_REV03.png')
iso.save(DEBUG/'REACTOR_EMITTER_3D_REV03.png')
front.save(DEBUG/'REACTOR_EMITTER_MUZZLE_REV03.png')

W,H=1800,1260
board=Image.new('RGB',(W,H),(13,18,30))
d=ImageDraw.Draw(board)
try:
    ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',32)
    fl=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
    fm=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
except OSError:ft=ImageFont.load_default();fl=fm=ft

def panel(img,x,y,width,height,label):
    resized=ImageOps.contain(img,(width,height),Image.Resampling.LANCZOS)
    d.rectangle((x,y,x+width,y+height),fill=(23,30,47))
    board.paste(resized,(x+(width-resized.width)//2,y+(height-resized.height)//2))
    d.rectangle((x,y,x+width,y+height),outline=(73,88,118),width=2)
    d.text((x+14,y+12),label,font=fl,fill=(239,243,250),stroke_width=1,stroke_fill=(11,16,24))

d.text((45,28),'YAYICI / NOZUL  —  REVİZYON 03 / GERÇEK 3B MESH',font=ft,fill=(241,245,253))
d.text((45,78),'4 bağımsız anten  •  önden dördü de görülebilir  •  koyu kobalt hücre  •  gerçek mesh renderı',
       font=fl,fill=(176,194,219))
panel(side,45,120,1090,595,'Yan görünüş • 3B mesh render')
panel(iso,1160,120,595,595,'3/4 görünüş • 3B mesh render')
panel(front,45,755,595,420,'Önden say: 4 anten • gerçek iris / boşluk')
ref=Image.open(ROOT/'model_work/reference_crops/image-3_right.png').convert('RGB')
panel(ref,665,755,480,420,'Referanstan görünen sol/sağ yayıcı')
ref_off=Image.open(ROOT/'model_work/reference_crops/image-7_right.png').convert('RGB')
panel(ref_off,1170,755,585,420,'Referansta hasarlı/kapanan hücre')
d.text((45,1205),f'GLB + OBJ teslimi  •  {faces_total:,} üçgen  •  {len(geo_names)} adlandırılmış mesh  •  yerleşim +X yönü',
       font=fm,fill=(171,188,211))
board.save(OUT/'REACTOR_EMITTER_MODEL_ONAY_REV03.png',optimize=True)
print(f'EXPORT: {GLB} ({GLB.stat().st_size/1e6:.2f}MB), {len(geo_names)} meshes, {faces_total} triangles')
print('Preview:',OUT/'REACTOR_EMITTER_MODEL_ONAY_REV03.png')
