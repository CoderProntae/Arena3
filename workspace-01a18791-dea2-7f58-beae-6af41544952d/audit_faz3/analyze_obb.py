#!/usr/bin/env python3
"""COLD pozu OBB kesisim analizi (Edit dokumu). SAT 15 eksen."""
import json, math, collections
import numpy as np

d = json.load(open('/home/user/audit_faz3/edit_geo_full.json'))
parts = []
for row in d['items']:
    path, cls = row[0], row[1]
    nums = np.array(row[2:], float)
    c = nums[:3]; R = nums[3:12].reshape(3, 3)  # satirlar: r00 r01 r02 / ...
    size = nums[12:15]; tr = nums[15]
    # Roblox: RightVector=(r00,r10,r20) vb. -> eksenler R'nin sutunlari
    axes = [R[:, 0], R[:, 1], R[:, 2]]
    half = size / 2.0
    # AABB yarisi
    aabb_half = np.abs(R) @ half if False else np.sum(np.abs(np.stack(axes, 1)) * half[None, :], axis=1)
    toks = path.split('.')
    grp = toks[2] if len(toks) > 2 else '?'       # STATIC/MOVING
    model = toks[3] if len(toks) > 3 else '?'
    sub = toks[4] if len(toks) > 4 else ''
    leaf = toks[-1]
    parts.append(dict(path=path, cls=cls, c=c, axes=axes, half=half, size=size,
                      aabb_min=c - aabb_half, aabb_max=c + aabb_half, tr=tr,
                      grp=grp, model=model, sub=sub, leaf=leaf,
                      key=f"{grp}/{model}"))
vis = [p for p in parts if p['tr'] < 0.99]
print(f"toplam {len(parts)}, gorunur {len(vis)}")
print("model basina gorunur parca:")
for k, v in collections.Counter(p['key'] for p in vis).most_common():
    print(f"  {k}: {v}")

def aabb_overlap(a, b):
    return bool(np.all(a['aabb_min'] <= b['aabb_max']) and np.all(b['aabb_min'] <= a['aabb_max']))

def radius_on(p, axis):
    return sum(abs(np.dot(axis, p['axes'][i])) * p['half'][i] for i in range(3))

def obb_depth(a, b):
    """Kesisiyorsa yaklasik sizma derinligi (min eksen bindirmesi), yoksa None."""
    axes = list(a['axes']) + list(b['axes'])
    for x in a['axes']:
        for y in b['axes']:
            cr = np.cross(x, y)
            n = np.linalg.norm(cr)
            if n > 1e-6: axes.append(cr / n)
    rel = b['c'] - a['c']
    best = 1e9
    for ax in axes:
        axn = ax / np.linalg.norm(ax)
        dist = abs(np.dot(rel, axn))
        overlap = radius_on(a, axn) + radius_on(b, axn) - dist
        if overlap <= 0: return None
        best = min(best, overlap)
    return best

results = []
n = len(vis)
for i in range(n):
    a = vis[i]
    for j in range(i + 1, n):
        b = vis[j]
        if not aabb_overlap(a, b): continue
        dep = obb_depth(a, b)
        if dep is None or dep < 0.05: continue
        # AABB bindirme hacmi (vekil)
        ov = np.maximum(0, np.minimum(a['aabb_max'], b['aabb_max']) - np.maximum(a['aabb_min'], b['aabb_min']))
        vol = float(np.prod(ov))
        if a['key'] == b['key']: cat = 'AYNI MODEL'
        elif a['grp'] == 'MOVING' and b['grp'] == 'MOVING': cat = 'HAREKETLI-HAREKETLI'
        elif a['grp'] == 'STATIC' and b['grp'] == 'STATIC': cat = 'SABIT-SABIT'
        else: cat = 'HAREKETLI-SABIT'
        results.append(dict(cat=cat, depth=float(dep), vol=vol,
                            a=a['path'].split('REACTOR_MESH_ASSEMBLY.')[1],
                            b=b['path'].split('REACTOR_MESH_ASSEMBLY.')[1],
                            ka=a['key'], kb=b['key']))
print(f"\nkesisen cift (derinlik>=0.05): {len(results)}")
for cat in ('HAREKETLI-SABIT', 'HAREKETLI-HAREKETLI', 'SABIT-SABIT', 'AYNI MODEL'):
    sub = sorted([r for r in results if r['cat'] == cat], key=lambda r: -r['depth'])
    pairs = collections.Counter()
    for r in sub:
        pairs[tuple(sorted((r['ka'], r['kb'])))] += 1
    print(f"\n### {cat}: {len(sub)} cift, model ciftleri: {len(pairs)}")
    for (k1, k2), cnt in pairs.most_common(14):
        mx = max(r['depth'] for r in sub if tuple(sorted((r['ka'], r['kb']))) == (k1, k2))
        print(f"   {cnt:4d} x  maksDerinlik {mx:5.2f}  {k1}  <->  {k2}")
    if cat != 'AYNI MODEL':
        print("   en derin 12 ornek:")
        for r in sub[:12]:
            print(f"     d={r['depth']:.2f} v={r['vol']:.1f}  {r['a']}  X  {r['b']}")
json.dump(results, open('/home/user/audit_faz3/cold_intersections.json', 'w'), ensure_ascii=False, indent=1)
print("\nyazildi: cold_intersections.json")
