# -*- coding: utf-8 -*-
"""
M14 — DAMAGE_GLASS_FRACTURE_STAGES_01
Panoramik lamine kontrol odasi cami icin 3 kademeli GERCEK 3B catlak kiti.
%0 2D efekt: catlaklar cam hacmine gomulu buzlu-beyaz damar geometrisi,
darbe kraterleri, buz desenleri ve ara katmandan sarkan gercek parcalar.

Canli olculer (Play, 4.1 dogrulama ciktisi verify41_out.json):
  PANORAMIC_LAMINATED_GLASS_1 (-2.75,24.625,46.625) 48.5x22.5x0.2
  PANORAMIC_LAMINATED_GLASS_2 (24.25,24.625,46.625)  5.5x22.5x0.2
  Mullionlar x=+-11.25 (0.42 eninde, oda tarafinda z=46.725)
Author koordinatlari: x ayni; z_up = studioY-26.5 -> cam merkezi -1.875,
aralik z [-13.125, 9.375]; y_derinlik = -46.625 (cam duzlemi).
Damarlar 0.26 kalin: cam (0.2) iki yuzden 0.03 tasar -> iki taraftan okunur,
es-duzlem z-fight yok.
Kademeler (crackPanes cagrilarina Faz 6'da baglanacak):
  STAGE1 kilcal yildiz (tek darbe), STAGE2 orumcek agi (iki darbe + kosucular),
  STAGE3 tam buzlanma/crazing (iki panel + sarkan parcalar).
"""
import os, sys, math
from pathlib import Path

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 20261028
sys.path.insert(0, "/home/user/.cache/modeldeps")
sys.path.insert(0, "/home/user/.cache/modelrender")
os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

OUT_DIR = Path("/home/user/model_exports")
GLB_PATH = OUT_DIR / "DAMAGE_GLASS_FRACTURE_STAGES_ADAY_YON_DUZELTME.glb"
PROOF_PATH = OUT_DIR / "DAMAGE_GLASS_FRACTURE_STAGES_ADAY_YON_DUZELTME.png"

Y_GLASS = -46.625
RECT = (-26.85, 26.85, -12.98, 9.23)  # x0, x1, z0, z1 (kenar payi 0.15)
P1 = np.array([-9.0, -4.0])   # ana darbe (author x,z) -> Studio (-9, 22.5)
P2 = np.array([7.0, 2.5])     # ikincil darbe -> Studio (7, 29.0)
P3 = np.array([-20.0, 4.0])   # ucuncul (yalniz kademe 3)

def pbr(name, rgb, metallic=0.0, rough=0.6, alpha=1.0):
    return PBRMaterial(name=name,
                       baseColorFactor=[rgb[0]/255, rgb[1]/255, rgb[2]/255, alpha],
                       metallicFactor=metallic, roughnessFactor=rough, doubleSided=True)

MATS = {
    "crack_vein":  pbr("Frosted crack vein", (205, 220, 235), 0.0, 0.55),
    "frost_patch": pbr("Laminate frost bloom", (226, 237, 247), 0.0, 0.92),
    "impact_core": pbr("Impact crater core", (238, 244, 251), 0.0, 0.85),
    "glass_shard": pbr("Sagging glass flake", (176, 208, 228), 0.0, 0.18),
}

class GB:
    def __init__(self):
        self.buckets = {}
    def add(self, grp, mat, mesh):
        if mesh is None or len(getattr(mesh, "faces", [])) == 0: return
        self.buckets.setdefault((grp, mat), []).append(mesh)

def box_mesh(extents, M):
    b = trimesh.creation.box(extents=extents)
    b.apply_transform(M)
    return b

def basis_xz(d):  # author: X sag, Z yukari, Y derinlik(normal)
    d = np.asarray(d, float); L = np.linalg.norm(d)
    if L < 1e-9: return None, 0
    xp = np.array([d[0], 0, d[1]]) / L
    yp = np.array([0.0, 1, 0])
    zp = np.cross(xp, yp)
    return (xp, yp, zp), L

def ribbon(gb, grp, mat, a, b, w, t=0.26, yoff=0.0):
    a = np.asarray(a, float); b = np.asarray(b, float)
    (xp, yp, zp), L = basis_xz(b - a)
    if L < 1e-6: return
    c = (a + b) / 2
    M = np.eye(4); M[:3, 0] = xp; M[:3, 1] = yp; M[:3, 2] = zp
    M[:3, 3] = np.array([c[0], Y_GLASS + yoff, c[1]])
    gb.add(grp, mat, box_mesh((L + w * 0.6, t, w), M))

def clip_seg(a, b, rect=RECT):
    """Liang-Barsky: segmenti dikdortgene kirp; disaridaysa None."""
    x0, x1, z0, z1 = rect
    a = np.array(a, float); b = np.array(b, float)
    d = b - a
    tmin, tmax = 0.0, 1.0
    for p, q in ((-d[0], a[0] - x0), (d[0], x1 - a[0]), (-d[1], a[1] - z0), (d[1], z1 - a[1])):
        if abs(p) < 1e-12:
            if q < 0: return None
        else:
            r = q / p
            if p < 0: tmin = max(tmin, r)
            else: tmax = min(tmax, r)
            if tmin > tmax: return None
    return a + d * tmin, a + d * tmax

def vein(gb, grp, a, b, w, mat="crack_vein", t=0.26, yoff=0.0):
    # Üç gerçek görüş bölmesinde dikmelere denk gelen şeritleri üretme.
    # Genişlik/uzatma payı da ayrılır; diğer küçük detaylar ayrıca denetlenmelidir.
    x0, x1, z0, z1 = RECT
    margin = 0.21 + w * 0.9 + 0.02
    for lo, hi in ((x0, -11.25 - margin), (-11.25 + margin, 11.25 - margin), (11.25 + margin, x1)):
        c = clip_seg(a, b, (lo, hi, z0, z1))
        if c is not None and np.linalg.norm(c[1] - c[0]) > 1e-6:
            ribbon(gb, grp, mat, c[0], c[1], w, t=t, yoff=yoff)

def crater(gb, grp, c, r, rng):
    # cekirdek: kisa silindir (eksen Y)
    core = trimesh.creation.cylinder(radius=r * 0.42, height=0.30, sections=10)
    core.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    core.apply_translation([c[0], Y_GLASS, c[1]])
    gb.add(grp, "impact_core", core)
    # yildiz pullari: hafif yatik ucgenler
    n = 10
    for i in range(n):
        a0 = 2 * math.pi * i / n + rng.uniform(-0.08, 0.08)
        a1 = a0 + 2 * math.pi / n * rng.uniform(0.7, 1.0)
        rr = r * rng.uniform(0.8, 1.25)
        y1 = Y_GLASS + rng.uniform(-0.05, 0.05)
        y2 = Y_GLASS + rng.uniform(-0.05, 0.05)
        v = np.array([[c[0], Y_GLASS + rng.uniform(-0.03, 0.03), c[1]],
                      [c[0] + rr * math.cos(a0), y1, c[1] + rr * math.sin(a0)],
                      [c[0] + rr * math.cos(a1), y2, c[1] + rr * math.sin(a1)]])
        f = np.array([[0, 1, 2], [0, 2, 1]])
        gb.add(grp, "frost_patch", trimesh.Trimesh(vertices=v, faces=f, process=False))

def spider(gb, grp, c, R, n_spokes, ring_fracs, rng, branch_p=0.5, w0=0.055):
    c = np.asarray(c, float)
    steps = np.array([0.16, 0.38, 0.62, 0.84, 1.0])
    spokes = []
    for i in range(n_spokes):
        base_ang = 2 * math.pi * i / n_spokes + rng.uniform(-0.12, 0.12)
        ang = base_ang
        pts = [c.copy()]
        angs = [ang]
        for sf in steps:
            ang += rng.uniform(-0.055, 0.055)
            angs.append(ang)
            pts.append(c + R * sf * np.array([math.cos(ang), math.sin(ang)]))
        spokes.append((pts, angs))
        for k in range(len(pts) - 1):
            w = w0 * (1 - 0.62 * (k / (len(pts) - 1))) + 0.012
            vein(gb, grp, pts[k], pts[k + 1], w)
        # dallar
        for _ in range(2):
            if rng.random() > branch_p: continue
            k = int(rng.integers(1, len(pts) - 1))
            ba = angs[k] + rng.choice([-1, 1]) * rng.uniform(0.45, 0.85)
            bl = R * rng.uniform(0.12, 0.30)
            mid = pts[k] + bl * 0.55 * np.array([math.cos(ba), math.sin(ba)])
            ba2 = ba + rng.uniform(-0.2, 0.2)
            end = mid + bl * 0.5 * np.array([math.cos(ba2), math.sin(ba2)])
            vein(gb, grp, pts[k], mid, 0.024)
            vein(gb, grp, mid, end, 0.017)
    # halkalar
    for f in ring_fracs:
        ring_pts = []
        for pts, angs in spokes:
            # yaricap f*R bileskesindeki nokta: adimlar arasi dogrusal
            target = f
            j = int(np.searchsorted(steps, target))
            j = max(1, min(j, len(steps) - 1))
            f0, f1 = steps[j - 1], steps[j]
            u = 0 if f1 == f0 else (target - f0) / (f1 - f0)
            ring_pts.append(pts[j] * (1 - u) + pts[j + 1] * u)
        for i in range(len(spokes)):
            if rng.random() < 0.22: continue
            vein(gb, grp, ring_pts[i], ring_pts[(i + 1) % len(spokes)], 0.028)

def frost_cluster(gb, grp, c, R, n, rng):
    c = np.asarray(c, float)
    pts = []
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        rr = abs(rng.normal(0, R * 0.55))
        p = c + rr * np.array([math.cos(a), math.sin(a)])
        if clip_seg(p, p) is None: continue
        pts.append(p)
        s = rng.uniform(0.16, 0.55)
        rot = rng.uniform(0, math.pi)
        (xp, yp, zp), _ = basis_xz(np.array([math.cos(rot), math.sin(rot)]))
        M = np.eye(4); M[:3, 0] = xp; M[:3, 1] = yp; M[:3, 2] = zp
        M[:3, 3] = np.array([p[0], Y_GLASS + rng.uniform(-0.02, 0.02), p[1]])
        gb.add(grp, "frost_patch", box_mesh((s, 0.27, s * rng.uniform(0.5, 0.9)), M))
    for i in range(len(pts) - 1):
        if rng.random() < 0.45:
            vein(gb, grp, pts[i], pts[i + 1], 0.018)

def crazing(gb, grp, spacing, rng, skip=0.12):
    x0, x1, z0, z1 = RECT
    xs = np.arange(x0 + 0.4, x1, spacing)
    zs = np.arange(z0 + 0.4, z1, spacing)
    grid = {}
    for i, x in enumerate(xs):
        for j, z in enumerate(zs):
            grid[(i, j)] = np.array([x + rng.uniform(-0.5, 0.5), z + rng.uniform(-0.5, 0.5)])
    for (i, j), p in grid.items():
        for di, dj in ((1, 0), (0, 1)):
            q = grid.get((i + di, j + dj))
            if q is not None and rng.random() > skip:
                vein(gb, grp, p, q, 0.022)
        if rng.random() < 0.10:
            q = grid.get((i + 1, j + 1))
            if q is not None: vein(gb, grp, p, q, 0.018)

def hanging_flake(gb, grp, c, w, h, tilt_deg, rng):
    """Ust kenarindan ara katmana tutunmus, alti iceri (oda) sarkan parca.
    Author +Y oda tarafi degil: oda studio z>46.6 => author y < -46.6 tarafi.
    Alt kenar author -Y yonde acilir."""
    tilt = math.radians(tilt_deg)
    b = trimesh.creation.box(extents=(w, 0.07, h))
    b.apply_translation([0, 0, -h / 2])  # ust kenar orijinde
    Rm = trimesh.transformations.rotation_matrix(-tilt, [1, 0, 0])
    b.apply_transform(Rm)
    b.apply_translation([c[0], Y_GLASS, c[1]])
    gb.add(grp, "glass_shard", b)
    # tutunma cizgisi
    vein(gb, grp, np.array([c[0] - w * 0.55, c[1]]), np.array([c[0] + w * 0.55, c[1]]), 0.03)

# ---------------- KADEMELER ----------------
gb = GB()

# STAGE 1 — kilcal yildiz
g = "GLASS_STAGE1_HAIRLINE"
rng = np.random.default_rng(SEED + 11)
spider(gb, g, P1, 5.2, 9, [0.5], rng, branch_p=0.35)
crater(gb, g, P1, 0.38, rng)

# STAGE 2 — orumcek agi
g = "GLASS_STAGE2_SPIDERWEB"
rng = np.random.default_rng(SEED + 22)
spider(gb, g, P1, 17.0, 13, [0.22, 0.45, 0.70], rng, branch_p=0.6)
crater(gb, g, P1, 0.55, rng)
spider(gb, g, P2, 7.5, 9, [0.35, 0.65], rng, branch_p=0.5)
crater(gb, g, P2, 0.42, rng)
frost_cluster(gb, g, P1, 1.7, 26, rng)
for corner in ((-26.5, 8.9), (21.0, -12.6), (21.0, 8.9)):
    cp = np.array(corner)
    mid = (P1 + cp) / 2 + rng.uniform(-0.7, 0.7, 2)
    vein(gb, g, P1, mid, 0.040); vein(gb, g, mid, cp, 0.028)

# STAGE 3 — tam crazing
g = "GLASS_STAGE3_CRAZED"
rng = np.random.default_rng(SEED + 33)
crazing(gb, g, 2.3, rng)
spider(gb, g, P1, 15.0, 13, [0.18, 0.38, 0.58, 0.80], rng, branch_p=0.75, w0=0.062)
crater(gb, g, P1, 0.65, rng)
spider(gb, g, P2, 9.0, 10, [0.30, 0.55, 0.82], rng, branch_p=0.65)
crater(gb, g, P2, 0.5, rng)
spider(gb, g, P3, 5.0, 8, [0.45], rng, branch_p=0.4)
crater(gb, g, P3, 0.4, rng)
frost_cluster(gb, g, P1, 2.2, 34, rng)
frost_cluster(gb, g, P2, 1.6, 22, rng)
frost_cluster(gb, g, np.array([-18.0, -8.0]), 1.8, 20, rng)
for (fx, fz, fw, fh, ft) in ((-14.5, 1.5, 1.6, 2.2, 14), (0.5, -8.5, 1.3, 1.8, 18),
                             (13.5, -3.0, 1.8, 2.4, 11), (-4.0, 6.0, 1.2, 1.6, 20),
                             (23.8, 0.0, 1.1, 1.7, 16), (-23.0, -6.5, 1.4, 1.9, 13)):
    hanging_flake(gb, g, np.array([fx, fz]), fw, fh, ft, rng)
# mullion kenar cipleri
for mx in (-11.25, 11.25):
    for k in range(6):
        z = -11 + k * 3.8 + rng.uniform(-0.6, 0.6)
        a = np.array([mx + rng.uniform(-0.1, 0.1), z])
        vein(gb, g, a, a + np.array([rng.choice([-1, 1]) * rng.uniform(0.6, 1.1), rng.uniform(-0.3, 0.3)]), 0.026)

# ---------------- GLB ----------------
def box_uv(mesh):
    v = mesh.vertices
    uv = np.column_stack([(v[:, 0] + 28.0) / 12.0, (v[:, 2] + 14.0) / 12.0])
    return uv

sc = trimesh.Scene()
total = 0
for (grp, mat), parts in sorted(gb.buckets.items()):
    merged = trimesh.util.concatenate(parts)
    merged.visual = trimesh.visual.texture.TextureVisuals(uv=box_uv(merged), material=MATS[mat])
    nm = f"{grp}__{mat}"
    sc.add_geometry(merged, geom_name=nm, node_name=nm)
    total += len(merged.faces)
raw = sc.export(file_type="glb")
GLB_PATH.write_bytes(raw)
print(f"GLB: {GLB_PATH} | {len(sc.geometry)} mesh | {total} ucgen | {len(raw)/1e6:.2f} MB")

# ---------------- ONAY RENDERI ----------------
import pyrender
from PIL import Image, ImageDraw

Mmap = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, -46.625], [0, 0, 0, 1]], dtype=float)
# author (x,y,z) -> render (x, z, -y-46.625): cam duzlemi render z=0

def ctx_geoms():
    """Baglam (yalniz render): soluk cam paneller + cerceve + mullionlar."""
    out = []
    glass_mat = pbr("ctx glass", (140, 175, 205), 0.0, 0.25, alpha=0.30)
    frame_mat = pbr("ctx frame", (58, 64, 78), 0.6, 0.5)
    def add_box(cx, cz, sx, sz, sy, mat):
        b = trimesh.creation.box(extents=(sx, sy, sz))
        b.apply_translation([cx, Y_GLASS, cz])
        b.visual = trimesh.visual.texture.TextureVisuals(uv=box_uv(b), material=mat)
        out.append(b)
    add_box(-2.75, -1.875, 48.5, 22.5, 0.2, glass_mat)
    add_box(24.25, -1.875, 5.5, 22.5, 0.2, glass_mat)
    add_box(0, 9.375 + 0.65, 55.3, 1.3, 0.7, frame_mat)
    add_box(0, -13.125 - 0.65, 55.3, 1.3, 0.7, frame_mat)
    add_box(-27.65, -1.875, 1.3, 23.8, 0.7, frame_mat)
    add_box(27.65, -1.875, 1.3, 23.8, 0.7, frame_mat)
    for mx in (-11.25, 11.25, 21.5):
        b = trimesh.creation.box(extents=(0.42, 0.65, 22.5))
        b.apply_translation([mx, Y_GLASS - 0.10, -1.875])
        b.visual = trimesh.visual.texture.TextureVisuals(uv=box_uv(b), material=frame_mat)
        out.append(b)
    return out

def stage_geoms(prefix):
    s2 = trimesh.load(GLB_PATH, process=False)
    gs = []
    for node in s2.graph.nodes_geometry:
        T, gname = s2.graph[node]
        if not gname.startswith(prefix): continue
        g = s2.geometry[gname].copy()
        g.apply_transform(T)
        gs.append(g)
    return gs

def look(eye, tgt, up=(0, 1, 0)):
    eye = np.asarray(eye, float); tgt = np.asarray(tgt, float)
    z = eye - tgt; z /= np.linalg.norm(z)
    x = np.cross(up, z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    T = np.eye(4); T[:3, 0] = x; T[:3, 1] = y; T[:3, 2] = z; T[:3, 3] = eye
    return T

def render_view(geoms, cam_pos, target, fov=42):
    scene = pyrender.Scene(bg_color=[0.043, 0.051, 0.063, 1.0])
    for g in geoms:
        gg = g.copy(); gg.apply_transform(Mmap)
        scene.add(pyrender.Mesh.from_trimesh(gg, smooth=False))
    scene.add(pyrender.PerspectiveCamera(yfov=math.radians(fov), znear=0.05, zfar=400),
              pose=look(cam_pos, target))
    key = pyrender.DirectionalLight(color=np.ones(3), intensity=2.6)
    scene.add(key, pose=look(np.array([14.0, 18.0, 26.0]), np.array([0.0, 0.0, 0.0])))
    fill = pyrender.DirectionalLight(color=np.array([0.55, 0.68, 0.85]), intensity=1.2)
    scene.add(fill, pose=look(np.array([-18.0, 4.0, 20.0]), np.array([0.0, 0.0, 0.0])))
    back = pyrender.DirectionalLight(color=np.array([0.75, 0.85, 1.0]), intensity=1.5)
    scene.add(back, pose=look(np.array([4.0, 6.0, -22.0]), np.array([0.0, 0.0, 0.0])))
    r = pyrender.OffscreenRenderer(1180, 740)
    color, _ = r.render(scene)
    r.delete()
    return Image.fromarray(color[:, :, :3])

CTX = ctx_geoms()
CTR = np.array([0.0, -1.875, 0.0])
views = [
    ("1) KADEME 1 - KILCAL YILDIZ",  "GLASS_STAGE1", CTR + np.array([0, 0.5, 46.0]), CTR),
    ("2) KADEME 2 - ORUMCEK AGI",    "GLASS_STAGE2", CTR + np.array([0, 0.5, 46.0]), CTR),
    ("3) KADEME 3 - TAM BUZLANMA",   "GLASS_STAGE3", CTR + np.array([0, 0.5, 46.0]), CTR),
    ("4) KADEME 2 - KRATER MAKRO",   "GLASS_STAGE2", np.array([-4.6, -1.4, 9.5]), np.array([-9.0, -4.0, 0.0])),
    ("5) KADEME 3 - ICERDEN 3/4 (SARKAN PARCALAR)", "GLASS_STAGE3", np.array([16.0, 4.5, -17.0]), np.array([2.0, -3.0, 0.0])),
    ("6) KADEME 1 - MAKRO",          "GLASS_STAGE1", np.array([-5.2, -1.8, 8.0]), np.array([-9.0, -4.0, 0.0])),
]

tiles = []
for label, prefix, cam, tgt in views:
    print("render:", label)
    img = render_view(CTX + stage_geoms(prefix), cam, tgt)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 740 - 26, 1180, 740], fill=(10, 12, 15))
    d.text((10, 740 - 19), label, fill=(205, 215, 228))
    tiles.append(img)

sheet = Image.new("RGB", (1180 * 2 + 12, 740 * 3 + 16), (8, 9, 11))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % 2) * (1180 + 12), (i // 2) * (740 + 8)))
sheet.save(PROOF_PATH)
print("ONAY SAYFASI:", PROOF_PATH, sheet.size)
