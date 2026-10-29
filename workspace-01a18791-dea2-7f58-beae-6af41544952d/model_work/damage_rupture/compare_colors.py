# -*- coding: utf-8 -*-
"""Renk kanıtı: Faz3 sağlam spool vs M13 patlak spool — aynı ışık/kamera, yan yana.
+ her iki GLB'den malzeme baseColor değerlerini basar (aynıysa Studio'da da aynı)."""
import os, sys, math, json
SEED=int(sys.argv[1]) if len(sys.argv)>1 else 0
def _import_gallery_block(*a, **k): pass
sys.path.insert(0, "/home/user/.cache/modeldeps"); sys.path.insert(0, "/home/user/.cache/modelrender")
import numpy as np
import trimesh
from PIL import Image, ImageDraw

FAZ3 = "/home/user/model_exports/REACTOR_COOLANT_PIPING_RING_01.glb"
M13  = "/home/user/model_exports/DAMAGE_PIPE_RUPTURE_KIT_01.glb"

def mats(path):
    sc = trimesh.load(path, process=False)
    out = {}
    for name, g in sc.geometry.items():
        m = getattr(g.visual, "material", None)
        bc = getattr(m, "baseColorFactor", None) if m is not None else None
        out[name] = tuple(int(round(float(x)*255)) for x in bc[:3]) if bc is not None else None
    return out

print("== FAZ3 (saglam) renkler ==")
for k, v in sorted(mats(FAZ3).items()):
    if "PIPE_SPOOL_UPPER_LEFT" in k: print(" ", k, v)
print("== M13 (patlak) renkler ==")
for k, v in sorted(mats(M13).items()):
    if "UPPER_LEFT" in k: print(" ", k, v)

# ---- sahne: üstte sağlam (Faz3), altta patlak (M13), author->render (x, z, -y)
Mmap = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]], dtype=float)
def spool_geoms(path, group_prefix, dz_author):
    sc = trimesh.load(path, process=False)
    geoms = []
    for node in sc.graph.nodes_geometry:
        T, gname = sc.graph[node]
        if not gname.startswith(group_prefix): continue
        g = sc.geometry[gname].copy()
        g.apply_transform(T)
        g.apply_transform(np.array([[1,0,0,0],[0,1,0,0],[0,0,1,dz_author],[0,0,0,1]]))
        g.apply_transform(Mmap)
        geoms.append(g)
    return geoms

intact  = spool_geoms(FAZ3, "PIPE_SPOOL_UPPER_LEFT", +1.6)
ruptured = spool_geoms(M13, "PIPE_SPOOL_UPPER_LEFT_RUPTURED", -1.6)
print("saglam parca:", len(intact), "| patlak parca:", len(ruptured))

import pyrender
scene = pyrender.Scene(bg_color=[0.043, 0.051, 0.063, 1.0])
for g in intact + ruptured:
    scene.add(pyrender.Mesh.from_trimesh(g, smooth=False))

center = np.array([-19.95, 15.85, 4.70])  # render frame: (x, z_up, -y) ; author UL (-19.95,-4.70,15.85)
cam_pos = center + np.array([5.2, 2.2, 7.2])
def look(eye, tgt, up=(0,1,0)):
    z = eye - tgt; z = z/np.linalg.norm(z)
    x = np.cross(up, z); x = x/np.linalg.norm(x)
    y = np.cross(z, x)
    T = np.eye(4); T[:3,0]=x; T[:3,1]=y; T[:3,2]=z; T[:3,3]=eye
    return T
scene.add(pyrender.PerspectiveCamera(yfov=math.radians(38), znear=0.05, zfar=300),
          pose=look(cam_pos, center))
scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=3.0),
          pose=look(np.array([8.0, 18.0, 14.0])), ) if False else None
key = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)
scene.add(key, pose=look(np.array([8.0, 18.0, 14.0]), np.array([0.0, 8.0, 0.0])))
fill = pyrender.DirectionalLight(color=np.array([0.55, 0.68, 0.85]), intensity=1.1)
scene.add(fill, pose=look(np.array([-14.0, 6.0, -8.0]), np.array([0.0, 8.0, 0.0])))
r = pyrender.OffscreenRenderer(1100, 760)
color, _ = r.render(scene)
img = Image.fromarray(color[:, :, :3])
d = ImageDraw.Draw(img)
d.rectangle([0, 716, 1100, 760], fill=(10, 12, 15))
d.text((12, 730), "UST: MEVCUT SAGLAM SPOOL (Faz 3, Studio'daki)   |   ALT: M13 PATLAK SPOOL  -  ayni isik, ayni kamera", fill=(205, 215, 228))
out = "/home/user/model_exports/DAMAGE_PIPE_RUPTURE_KIT_01_RENK_KARSILASTIRMA.png"
img.save(out); r.delete()
print("KARSILASTIRMA:", out)
