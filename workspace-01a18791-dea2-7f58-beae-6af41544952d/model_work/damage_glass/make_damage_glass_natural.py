"""M14 alternatif: katmanlı, tekrarlanabilir, ince ve düzensiz hacimli çatlaklar.
GLB koordinatları önceki M14 ile aynıdır. Katmanlar BİRİKİMLİ görünür olmalı;
1: L1, 2: L1+L2, 3: L1+L2+L3. Studio entegrasyonu değildir.
"""
import sys, os, math
from pathlib import Path
sys.path.insert(0, '/home/user/.cache/modeldeps')
os.environ.setdefault('PYOPENGL_PLATFORM','egl')
import numpy as np, trimesh, pyrender
from PIL import Image
R=np.random.default_rng(93241)
Y=-46.625
# Görüş bölmeleri ve dış çerçeveden güvenli pay, author X/Z
panes=[(-26.8,-11.53),(-10.97,10.97),(11.53,26.8)]
zlo,zhi=-12.9,9.15
bucket={1:[],2:[],3:[]}
mat=trimesh.visual.material.PBRMaterial(name='laminate_fracture',baseColorFactor=[0.70,0.80,0.84,1],metallicFactor=0.0,roughnessFactor=0.58,doubleSided=True)

def clip(a,b,rect):
    lo,hi,z0,z1=rect; d=b-a; t0,t1=0.,1.
    for p,q in ((-d[0],a[0]-lo),(d[0],hi-a[0]),(-d[1],a[1]-z0),(d[1],z1-a[1])):
        if abs(p)<1e-10:
            if q<0:return None
        elif p<0:t0=max(t0,q/p)
        else:t1=min(t1,q/p)
        if t0>t1:return None
    return a+d*t0,a+d*t1

def segment(stage,a,b,w1,w2):
    a=np.asarray(a,dtype=float); b=np.asarray(b,dtype=float)
    w1 *= 1.35; w2 *= 1.35
    for lo,hi in panes:
        clipped=clip(a,b,(lo+0.08,hi-0.08,zlo+0.08,zhi-0.08))
        if clipped is None:continue
        x1,x2=clipped; d=x2-x1; length=np.linalg.norm(d)
        if length<0.015:continue
        n=np.array([-d[1],d[0]])/length
        a0=x1+n*w1/2; a1=x1-n*w1/2; b0=x2+n*w2/2; b1=x2-n*w2/2
        # watertight tapered prism rather than camera-facing line; 0.018 thickness
        coords=[a0,a1,b1,b0]; vs=[[p[0],Y+dy,p[1]] for dy in (-.009,.009) for p in coords]
        fs=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
        bucket[stage].append(trimesh.Trimesh(vertices=vs,faces=fs,process=False))

def crack(stage,center,ang,length,width,steps=9,branch_prob=.22):
    p=np.array(center,dtype=float); angle=ang
    for i in range(steps):
        angle+=R.normal(0,0.085); L=length/steps*R.uniform(.7,1.25)
        q=p+L*np.array([math.cos(angle),math.sin(angle)])
        frac=i/steps; w=max(.009,width*(1-frac*.77)); segment(stage,p,q,w,w*.86)
        if i>1 and R.random()<branch_prob:
            ba=angle+R.choice([-1,1])*R.uniform(.35,1.0); bp=p.copy()
            for j in range(int(R.integers(2,5))):
                ba+=R.normal(0,.13); bq=bp+L*R.uniform(.38,.95)*np.array([math.cos(ba),math.sin(ba)])
                segment(stage,bp,bq,w*.42,max(.008,w*.18));bp=bq
        p=q

def web(stage,c,rays,rmin,rmax,width):
    # directions jitter independently; no evenly spaced grid
    for k in range(rays):
        ang=2*math.pi*k/rays+R.uniform(-.22,.22)
        crack(stage,c,ang,R.uniform(rmin,rmax),width*R.uniform(.65,1.2),steps=int(R.integers(6,12)),branch_prob=.26)
    # fractured concentric fragments, discontinuous and jittered
    for rad in (0.42,0.85,1.5,2.4):
        last=None
        for t in np.linspace(0,2*math.pi,28):
            rr=rad*R.uniform(.92,1.08); p=np.array(c)+rr*np.array([math.cos(t),math.sin(t)])
            if last is not None and R.random()>.20: segment(stage,last,p,.020,.013)
            last=p

# A single evolving first impact (cumulative layers preserve earlier cracks)
impact=(-5.4,-1.1)
web(1,impact,10,1.3,3.7,.044)
for k in range(13):
    ang=2*math.pi*k/13+R.uniform(-.18,.18)
    start=np.array(impact)+R.uniform(1.0,2.6)*np.array([math.cos(ang),math.sin(ang)])
    crack(2,start,ang,R.uniform(3.5,10),.033,steps=10,branch_prob=.27)
web(2,(17.2,3.1),8,1.3,4.4,.036)
web(3,(-19.2,-6.0),10,2.5,7.0,.040)
for center in [impact,(17.2,3.1),(-19.2,-6.0)]:
    for k in range(7):
        ang=2*math.pi*k/7+R.uniform(-.2,.2); start=np.array(center)+R.uniform(1.0,3.5)*np.array([math.cos(ang),math.sin(ang)])
        crack(3,start,ang,R.uniform(5,12),.028,steps=11,branch_prob=.35)

# Shards: small jagged 3D triangular flaps, oriented into room (-Y).
def shard(x,z,s,angle):
    pts=np.array([[-.55*s,0],[.48*s,.12*s],[.08*s,-1.1*s]])
    a=math.radians(angle); vs=[]
    for dy in [-.025,.025]:
        for dx,dz in pts:
            vs.append([x+dx,Y+dy+dz*math.sin(a),z+dz*math.cos(a)])
    faces=[[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]]
    bucket[3].append(trimesh.Trimesh(vertices=vs,faces=faces,process=False))
for x,z,s,a in [(-5.4,-1.0,.40,16),(17.2,3.1,.34,18),(-19.2,-6,.33,14),(-2.1,-6.3,.20,12),(7.8,1.9,.24,19)]: shard(x,z,s,a)
scene=trimesh.Scene(); merges={}
for stage in (1,2,3):
    m=trimesh.util.concatenate(bucket[stage]); m.visual=trimesh.visual.texture.TextureVisuals(material=mat,uv=np.zeros((len(m.vertices),2)))
    name=f'GLASS_LAYER_{stage:02d}';scene.add_geometry(m,geom_name=name,node_name=name);merges[stage]=m
out=Path('/home/user/model_exports');out.mkdir(exist_ok=True)
path=out/'DAMAGE_GLASS_NATURAL_CANDIDATE.glb';path.write_bytes(scene.export(file_type='glb'))
print('GLB:',path,'triangles:',sum(len(m.faces) for m in merges.values()))
# Standalone views, preview context does not enter GLB.
M=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,-46.625],[0,0,0,1]],float)
def box_scene(sc,center,extent,color):
 m=trimesh.creation.box(extents=extent);m.apply_translation(center)
 m.visual=trimesh.visual.ColorVisuals(m,face_colors=color); sc.add(pyrender.Mesh.from_trimesh(m,smooth=False))
for stage in (1,2,3):
 s=pyrender.Scene(bg_color=[.045,.062,.075,1],ambient_light=[.48,.48,.48]);
 # Render axes x, vertical y, depth z. Fake dark backdrop is not glass.
 box_scene(s,[0,-1.875,-1],[54,22.5,.12],[30,44,52,255])
 for x in [-27.4,-11.25,11.25,27.4]:box_scene(s,[x,-1.875,.18],[.42,23.0,.7],[55,62,67,255])
 for z in [-13.25,9.5]:box_scene(s,[0,z,.18],[55,.48,.7],[55,62,67,255])
 for k in range(1,stage+1):
  g=merges[k].copy();g.apply_transform(M);s.add(pyrender.Mesh.from_trimesh(g,smooth=False))
 cam=pyrender.PerspectiveCamera(yfov=math.radians(32));pose=np.eye(4);pose[:3,3]=[0,-1.875,57];s.add(cam,pose=pose)
 light=pyrender.DirectionalLight(color=np.ones(3),intensity=3.0);s.add(light,pose=pose)
 renderer=pyrender.OffscreenRenderer(1500,720);color,_=renderer.render(s);renderer.delete()
 p=out/f'DAMAGE_GLASS_NATURAL_KADEME_{stage}.png';Image.fromarray(color[:,:,:3]).save(p);print('Preview:',p)
