#!/usr/bin/env python3
"""Offline GIF of the *actual* closed-hatch GLB and approved emitter GLB.

This demonstrates the future Studio motion plan; it is not Studio gameplay,
not a physics test, and it does not pretend that Roblox audio is permitted yet.
"""
from pathlib import Path
import os,sys,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
os.environ['PYOPENGL_PLATFORM']='egl'
sys.path[:0]=['/home/user/.cache/modeldeps','/home/user/.cache/modelrender']
import trimesh,pyrender
ROOT=Path('/home/user');OUT=ROOT/'model_exports'
wall=trimesh.load(OUT/'REACTOR_WALL_HATCH_THROUGH_01.glb',force='scene')
emitter=trimesh.load(OUT/'REACTOR_EMITTER_REV03.glb',force='scene')
p=pyrender.Scene(bg_color=[.012,.012,.026,1],ambient_light=[.22,.20,.23])
wall_nodes=[];emitter_nodes=[]
for name,g in wall.geometry.items():
    node=p.add(pyrender.Mesh.from_trimesh(g),name=name,pose=np.eye(4))
    wall_nodes.append((node,name))
for name,g in emitter.geometry.items():
    T=np.eye(4);T[0,3]=-11.47
    node=p.add(pyrender.Mesh.from_trimesh(g),name='EM_'+name,pose=T)
    emitter_nodes.append(node)
for pos,color,power in [((8,-8,9),(1.,.42,.17),230),
                        ((10,6,6),(.46,.49,.96),80),
                        ((13,-3,-9),(.30,.32,.99),53)]:
    M=np.eye(4);M[:3,3]=pos
    p.add(pyrender.PointLight(color=np.asarray(color),intensity=power),pose=M)

def camera(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    r=np.cross(f,(0,0,1.));r/=np.linalg.norm(r)
    u=np.cross(r,f)
    M=np.eye(4);M[:3,:3]=np.stack((r,u,-f),axis=1);M[:3,3]=eye
    return M
p.add(pyrender.PerspectiveCamera(yfov=math.radians(52)),
      pose=camera((30,-16,6),(4,0,0)))
R=pyrender.OffscreenRenderer(720,450)
try:
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',19)
    subfont=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
except OSError:font=subfont=ImageFont.load_default()

def ease(x):
    x=np.clip(x,0,1)
    return x*x*(3-2*x)
frames=[]
fps=12
for i in range(64):
    t=i/fps
    door=float(ease((t-.45)/.74)*(1-ease((t-4.25)/.72)))
    ext=float(ease((t-1.25)/1.38)*(1-ease((t-3.15)/1.07)))
    for node,name in wall_nodes:
        T=np.eye(4)
        if name.startswith('HATCH_LEFT'):T[1,3]=-5.85*door
        elif name.startswith('HATCH_RIGHT'):T[1,3]=5.85*door
        p.set_pose(node,pose=T)
    for node in emitter_nodes:
        T=np.eye(4);T[0,3]=-11.47+19.80*ext
        p.set_pose(node,pose=T)
    rgb,_=R.render(p,flags=pyrender.RenderFlags.RGBA)
    im=Image.fromarray(rgb,'RGBA').convert('RGB')
    im=im.resize((576,360),Image.Resampling.LANCZOS)
    d=ImageDraw.Draw(im)
    if t<.45:label='COLD — kapaklar kapalı'
    elif t<1.24:label='STARTUP — kapaklar yanlara açılıyor'
    elif t<2.66:label='STARTUP — piston tüm yayıcıyı ileri itiyor'
    elif t<3.16:label='Yayıcı dışarıda — ışın efektleri sonra açılır'
    elif t<4.25:label='KAPANIŞ — piston yayıcıyı geri çekiyor'
    else:label='KAPANIŞ — kapaklar kapanıyor'
    d.rectangle((0,0,576,40),fill=(12,17,25))
    d.text((12,9),label,font=font,fill=(241,243,251))
    d.rectangle((0,338,576,360),fill=(12,17,25))
    d.text((12,341),'Çevrimdışı gerçek 3B hareket • Studio testi değil • ses uygulanmadı',
           font=subfont,fill=(179,195,214))
    frames.append(im.quantize(colors=128,method=Image.Quantize.FASTOCTREE))
R.delete()
path=OUT/'REACTOR_WALL_HATCH_MOTION_01.gif'
frames[0].save(path,save_all=True,append_images=frames[1:],duration=83,
               optimize=True,loop=0,disposal=2)
print('GIF',path,'frames',len(frames),'size',path.stat().st_size)
