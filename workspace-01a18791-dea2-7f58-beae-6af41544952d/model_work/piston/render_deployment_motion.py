#!/usr/bin/env python3
"""Offline, *true 3D mesh* preview of approved hatch + proposed piston.

No Studio animation test or audio permission is implied. Both front and
behind-wall camera views render the same changing mesh nodes each frame.
"""
import os,sys,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
os.environ['PYOPENGL_PLATFORM']='egl'
sys.path[:0]=['/home/user/.cache/modeldeps','/home/user/.cache/modelrender']
import trimesh,pyrender
ROOT=Path('/home/user');OUT=ROOT/'model_exports'
W=trimesh.load(OUT/'REACTOR_WALL_HATCH_THROUGH_01.glb',force='scene')
P=trimesh.load(OUT/'REACTOR_PISTON_GUIDE_01.glb',force='scene')
E=trimesh.load(OUT/'REACTOR_EMITTER_REV03.glb',force='scene')
sc=pyrender.Scene(bg_color=[.011,.013,.025,1],ambient_light=[.21,.21,.23])
wall_nodes=[];piston_nodes=[];emitter_nodes=[]
for name,g in W.geometry.items():
    node=sc.add(pyrender.Mesh.from_trimesh(g),name='W_'+name,pose=np.eye(4))
    wall_nodes.append((node,name))
for name,g in P.geometry.items():
    node=sc.add(pyrender.Mesh.from_trimesh(g),name='P_'+name,pose=np.eye(4))
    piston_nodes.append((node,name))
for name,g in E.geometry.items():
    M=np.eye(4);M[0,3]=-11.47
    emitter_nodes.append(sc.add(pyrender.Mesh.from_trimesh(g),name='E_'+name,pose=M))
for pos,color,intensity in [((-18,-12,9),(.80,.85,1.),160),
                            ((-29,6,2),(1.,.43,.19),72),
                            ((9,-8,8),(.90,.64,.74),170),
                            ((11,5,-7),(.30,.40,.91),68)]:
    pose=np.eye(4);pose[:3,3]=pos
    sc.add(pyrender.PointLight(color=np.asarray(color),intensity=intensity),pose=pose)

def look(eye,target):
    eye=np.asarray(eye,float);target=np.asarray(target,float)
    f=target-eye;f/=np.linalg.norm(f)
    rt=np.cross(f,(0,0,1.));rt/=np.linalg.norm(rt)
    up=np.cross(rt,f)
    T=np.eye(4);T[:3,:3]=np.stack((rt,up,-f),axis=1);T[:3,3]=eye
    return T
camera=sc.add(pyrender.PerspectiveCamera(yfov=math.radians(52)),
              pose=look((30,-16,6),(4,0,0)))
render=pyrender.OffscreenRenderer(600,380)
try:
    title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',19)
    text=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
except OSError:title=text=ImageFont.load_default()

def smooth(v):
    v=np.clip(v,0,1);return float(v*v*(3-2*v))
frames=[];fps=12
for i in range(64):
    t=i/fps
    door=smooth((t-.44)/.75)*(1-smooth((t-4.25)/.73))
    travel=smooth((t-1.23)/1.43)*(1-smooth((t-3.14)/1.08))
    for node,name in wall_nodes:
        T=np.eye(4)
        if name.startswith('HATCH_LEFT'):T[1,3]=-5.85*door
        if name.startswith('HATCH_RIGHT'):T[1,3]=5.85*door
        sc.set_pose(node,pose=T)
    for node,name in piston_nodes:
        T=np.eye(4)
        if name.startswith('STAGE1'):T[0,3]=6.6*travel
        elif name.startswith('STAGE2'):T[0,3]=13.2*travel
        elif name.startswith('STAGE3') or name.startswith('PUSHER'):
            T[0,3]=19.8*travel
        sc.set_pose(node,pose=T)
    for node in emitter_nodes:
        T=np.eye(4);T[0,3]=-11.47+19.8*travel
        sc.set_pose(node,pose=T)
    sc.set_pose(camera,pose=look((30,-16,6),(4,0,0)))
    front,_=render.render(sc,flags=pyrender.RenderFlags.RGBA)
    sc.set_pose(camera,pose=look((-18,-18,10),(-15,0,0)))
    back,_=render.render(sc,flags=pyrender.RenderFlags.RGBA)
    frame=Image.new('RGB',(1200,430),(13,18,28))
    frame.paste(Image.fromarray(front,'RGBA').convert('RGB'),(0,32))
    frame.paste(Image.fromarray(back,'RGBA').convert('RGB'),(600,32))
    d=ImageDraw.Draw(frame)
    d.text((15,6),'ÖNDEN: KAPAKLAR VE YAYICI',font=title,fill=(242,243,249))
    d.text((616,6),'ARKADAN: KILAVUZ VE PİSTON',font=title,fill=(242,243,249))
    if t<.45:label='COLD / kapaklar kapalı / yayıcı içeride'
    elif t<1.23:label='STARTUP / kapaklar iki yana kayıyor'
    elif t<2.68:label='STARTUP / üç piston kademesi ilerliyor, yayıcı tek parça gidiyor'
    elif t<3.15:label='İLERİ KONUM / ışın efektleri sonra açılır'
    elif t<4.25:label='KAPANIŞ / piston yayıcıyı geri çekiyor'
    else:label='KAPANIŞ / kapaklar iki yandan kapanıyor'
    d.rectangle((0,411,1200,430),fill=(13,18,28))
    d.text((15,411),label+'  •  SESSİZ çevrimdışı mesh önizlemesi; Studio testi değildir',
           font=text,fill=(187,201,221))
    frames.append(frame.quantize(colors=128,method=Image.Quantize.FASTOCTREE))
render.delete()
path=OUT/'REACTOR_DEPLOYMENT_WITH_PISTON_01.gif'
frames[0].save(path,save_all=True,append_images=frames[1:],duration=83,
               optimize=True,loop=0,disposal=2)
print('OUTPUT',path,'size',path.stat().st_size,'bytes; rendered',len(frames),'frames')
