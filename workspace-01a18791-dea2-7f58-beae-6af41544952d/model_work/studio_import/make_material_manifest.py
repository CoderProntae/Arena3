#!/usr/bin/env python3
"""Read the reviewed GLB material metadata for Studio's untextured color fix.
Roblox's importer applied medium-gray Plastic to many plain glTF baseColorFactor
meshes; the approved mesh IDs and uploaded PBR SurfaceAppearances remain intact.
"""
from __future__ import annotations
import json,struct
from pathlib import Path
ROOT=Path('/home/user')
ASSETS=json.loads((ROOT/'model_work/studio_import/manifest_studio_ready.json').read_text())['assets']
all_parts={}
for asset in ASSETS:
    filename=asset['file']
    path=ROOT/'model_exports'/filename
    raw=path.read_bytes()
    length=struct.unpack_from('<I',raw,12)[0]
    gltf=json.loads(raw[20:20+length])
    parts={}
    for node in gltf['nodes']:
        if 'mesh' not in node:
            continue
        primitives=gltf['meshes'][node['mesh']]['primitives']
        assert len(primitives)==1,(filename,node['name'])
        material=gltf['materials'][primitives[0]['material']]
        pbr=material.get('pbrMetallicRoughness',{})
        color=pbr.get('baseColorFactor',[1,1,1,1])
        parts[node['name']]={
            'rgb':[round(x*255) for x in color[:3]],
            'alpha':round(color[3],4),
            'metal':round(pbr.get('metallicFactor',0),3),
            'texture':bool(pbr.get('baseColorTexture')),
            'emissive':round(max(material.get('emissiveFactor') or [0,0,0]),3),
        }
    assert len(parts)==asset['mesh_nodes']
    all_parts[filename.removesuffix('.glb')]=parts
path=ROOT/'model_work/studio_import/materials_by_node.json'
path.write_text(json.dumps(all_parts,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('manifest',path,'nodes',sum(map(len,all_parts.values())),'bytes',path.stat().st_size)
