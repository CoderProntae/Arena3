#!/usr/bin/env python3
"""Prepare the seven ALREADY REVIEWED GLBs for Roblox's glTF Y-up Importer.

The offline authoring space is X-right / Y-depth (front -> rear) / Z-up. glTF
uses Y-up. For Studio, bake ONLY this proper rigid rotation into the vertices:
(X,Y,Z)_source -> (X,Z,-Y)_glTF. No materials, UVs, geometry, or proportions
are intentionally revised. All seven components keep the same shared origin.

Authoritative, user-reviewed exports remain untouched in model_exports/. This
script stores transient converted copies under .cache/ and a small persistent
ZIP containing the seven GLBs + the user-run Studio bridge (but no agent admin
credential). The pack is NOT proof the importer uploaded or displayed assets.
"""
from __future__ import annotations
import hashlib,json,os,sys,zipfile
from pathlib import Path

ROOT=Path('/home/user')
sys.path.insert(0,str(ROOT/'.cache/modeldeps'))
import numpy as np
import trimesh

EXP=ROOT/'model_exports'
TEMP=ROOT/'.cache/studio_ready'
BRIDGE=ROOT/'studio_bridge/provider_switch'
PACK=ROOT/'REACTOR_STUDIO_TEK_PAKET.zip'
TEMP.mkdir(parents=True,exist_ok=True)
FILES=[
 'REACTOR_EMITTER_REV03.glb',
 'REACTOR_CORE_MANYETIK_01.glb',
 'REACTOR_WALL_HATCH_THROUGH_01.glb',
 'REACTOR_PISTON_GUIDE_01.glb',
 'REACTOR_REAR_SERVICE_GRILLES_01.glb',
 'REACTOR_REAR_BULKHEAD_IRON_REV04.glb',
 'REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV02.glb',
]
R=np.eye(4)
R[:3,:3]=[[1,0,0],[0,0,1],[0,-1,0]]
assert abs(np.linalg.det(R[:3,:3])-1)<1e-8

def named_geometry(scene):
    # Each source glTF node was individually named for hatch leaves, piston
    # stage groups and energy parts. Preserve their names for Luau discovery.
    return list(scene.graph.nodes_geometry)

manifest=[]
for filename in FILES:
    src_path=EXP/filename
    src=trimesh.load(src_path,force='scene',process=False)
    ready=trimesh.Scene()
    nodes=named_geometry(src)
    tri_before=sum(len(src.geometry[src.graph[node][1]].faces) for node in nodes)
    for node in nodes:
        frame,geom=src.graph[node]
        mesh=src.geometry[geom].copy()
        mesh.apply_transform(R@frame)
        ready.add_geometry(mesh,geom_name=geom,node_name=node,transform=np.eye(4))
    data=ready.export(file_type='glb')
    dst_path=TEMP/filename
    dst_path.write_bytes(data)
    verify=trimesh.load(dst_path,force='scene',process=False)
    reloaded_nodes=list(verify.graph.nodes_geometry)
    tri_after=sum(len(verify.geometry[verify.graph[node][1]].faces) for node in reloaded_nodes)
    assert tri_after==tri_before,(filename,tri_before,tri_after)
    assert len(reloaded_nodes)==len(nodes),(filename,len(reloaded_nodes),len(nodes))
    assert set(reloaded_nodes)==set(nodes),(filename,'animation node names changed')
    # Bounds of the SAME actual triangles in the Y-up file must match the
    # mapped source, irrespective of geometry/node traversal order.
    original_corners=np.array([[x,y,z] for x in src.bounds[:,0]
                                 for y in src.bounds[:,1]
                                 for z in src.bounds[:,2]])
    mapped=(R[:3,:3]@original_corners.T).T
    expect=np.stack([mapped.min(axis=0),mapped.max(axis=0)])
    assert np.allclose(verify.bounds,expect,atol=.005),(filename,verify.bounds,expect)
    entry={'file':filename,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
           'mesh_nodes':len(nodes),'triangles':tri_after,
           'bounds_y_up':np.round(verify.bounds,3).tolist()}
    manifest.append(entry)
    print(filename,len(data),'bytes',len(nodes),'named nodes',tri_after,'triangles',flush=True)

README='''REAKTOR / TEK PAKET — YEDI ONAYLI 3B MODEL + YENI KOPRU
========================================================
Bu GLB dosyalari kullanicinin onayladigi modellerin Studio icin Y-yukari
koordinatina DONUSTURULMUS kopyalaridir; sekilleri/olcekleri degistirilmedi.

1. Eski ntfy.sh koprusunu terminalde Ctrl+C ile durdur. Bu ZIP'i YENI bir
   klasore ac. Roblox Studio'yu ilgili yer ile Edit modunda ac ve yedek al.
2. O klasorde PowerShell: python .\\Roblox_Studio_MCP_Kalici_Kopru.py
   cryptography eksikse bir kez: python -m pip install cryptography
   Bu terminali acik birak. Bu sohbetten "Kopru ONLINE" haberini ver.
3. Studio File > Import (veya Ctrl+M): models klasorundeki YEDI .glb'yi
   tek seferde sec. Importer'da hepsinin Scale Unit = Studs oldugunu
   kontrol et, Import Only As Model secili kalsin, sonra Import de.
   Roblox'a yukleme secenegi paylasim/kalicilik kararin; bundan haber ver.
   Studio'da gorunene kadar aktarildi veya dogru gorunuyor varsaymiyoruz.
4. Dosyalar Workspace'e gelince bana haber ver. Sunucu tarafli hatch/piston/
   yekpare yayici animasyonlarini, koordinat/olcek hizalamasini ve durum VFX'ini
   Studio'da bizzat inceleyip kuracagim; fiziki tiklama testi yapmayacagim.

Windows istemcisi sadece Studio'nun resmi yerel mcp.bat surecini baslatir,
disariya yalniz giden HTTPS baglantisi acar; yazma/Play/Luau icin konsolda
HER ISLEMDE ayri YES gerekir. Yeni saglayici ntfy.envs.net ucretsiz bir
ucuncu taraf posta kutusudur: kota/erisim garantisi yoktur; AES/Fernet ile
icerik uctan uca sifrelenir fakat iletisim zamani/boyutu gorulebilir.
Roblox hesap sifresi veya API anahtari istemez. Gizli JSON'u paylasma.
Kaynak modeller model_exports/ altinda DEGISMEDEN kaldi.
'''
(ROOT/'model_work/studio_import/README_STUDIO_PACK.txt').write_text(README,encoding='utf-8')
manifest_path=ROOT/'model_work/studio_import/manifest_studio_ready.json'
manifest_path.write_text(json.dumps({'axis_map':'source (X,Y,Z) -> glTF (X,Z,-Y)',
   'originals_unchanged':True,'scale_unit_to_select':'Studs','assets':manifest},
   indent=2,ensure_ascii=False),encoding='utf-8')
with zipfile.ZipFile(PACK,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for path in (BRIDGE/'Roblox_Studio_MCP_Kalici_Kopru.py',
                 BRIDGE/'Roblox_Studio_Bus.py',
                 BRIDGE/'Roblox_Studio_MCP_Gizli_Ayar.json'):
        archive.write(path,path.name)
    archive.write(ROOT/'model_work/studio_import/README_STUDIO_PACK.txt','BASLAT.txt')
    archive.write(manifest_path,'models/MANIFEST.json')
    for filename in FILES:
        archive.write(TEMP/filename,'models/'+filename)
with zipfile.ZipFile(PACK) as archive:
    assert len(archive.namelist())==12
    assert archive.testzip() is None
print('PACK',PACK,PACK.stat().st_size,'bytes (seven GLBs + Windows bridge)',flush=True)
