#!/usr/bin/env python3
"""Faz 2 Rear 10-Blade Crisp CNC Turbine, Upper Blue Louvre, Deep Plenum & Multi-Tone Slate-Iron Rear Bulkhead.

Upgrades per user direction:
  1) Multi-tone grey/iron industrial architecture calibrated directly from 01_komut_110.jpg (ZERO coppery brown!):
     - Course 4 (Z > +8.5): Cool Slate-Blue Rolled Steel (RGB ~94, 106, 128)
     - Course 3 (Z in [-2.0, +8.5]): Cool Slate-Graphite Bulkhead Iron (RGB ~68, 73, 88)
     - Courses 1-2 (Z < -2.0): Gunmetal-Slate & Olive-Taupe Industrial Dado (RGB ~74, 72, 64) + muted yellow caution tabs
  2) Rear Turbine Fan Blade Count reduced slightly (12 -> 10 blades, matching 01_komut_110.jpg 36-deg spacing!)
  3) Razor-sharp hard-surface CNC fan quality:
     - Removed coarse rust normal map from all turbine parts!
     - Explicit hard-surface crease normals (unmerge_vertices on faceted blades/bolts/louvers + 64-seg precision rings)
     - Each of the 10 blades features a bolted root trunnion cuff + dark titanium-gunmetal airfoil + bright cold-steel
       leading-edge chamfer strip so every blade edge reads tack-sharp at all distances!
     - Cool brushed nickel-steel & gunmetal 18-stud behind-fan exhaust tunnel & 12-tube condenser plenum (%0 void, %0 copper!).
"""
from __future__ import annotations
import math, os, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy.ndimage import gaussian_filter

os.environ["PYOPENGL_PLATFORM"] = "egl"
ROOT = Path("/home/user")
sys.path[:0] = [str(ROOT / ".cache/modeldeps")]
import trimesh, pyrender

EXP = ROOT / "model_exports"
DBG = ROOT / ".cache/model_debug"
EXP.mkdir(parents=True, exist_ok=True)
DBG.mkdir(parents=True, exist_ok=True)

FAN_X = 0.0
FAN_Z = 1.80
FAN_HOLE_R = 3.92
LOUVRE_X = 3.76
LOUVRE_Z0, LOUVRE_Z1 = 9.50, 12.50

# ============================================================================
# 1. MULTI-TONE SLATE-IRON REAR BULKHEAD (REACTOR_REAR_BULKHEAD_IRON_REV05_TURBINE_PORT.glb)
# ============================================================================
rng4 = np.random.default_rng(91919)
W4 = H4 = 1024
co = np.asarray(Image.fromarray(rng4.integers(0, 256, (43, 43), dtype=np.uint8), "L").resize((W4, H4), Image.Resampling.BICUBIC), float) - 128
mid = np.asarray(Image.fromarray(rng4.integers(0, 256, (210, 210), dtype=np.uint8), "L").resize((W4, H4), Image.Resampling.BILINEAR), float) - 128
speck = rng4.standard_normal((H4, W4)) * 2.4
wear = np.clip(0.56 + 0.045 * np.tanh((co + 8) / 34) + 0.095 * np.tanh(mid / 32), 0.38, 0.74)
pits = rng4.random((H4, W4)) < 0.008

def make_course_tex(rgb_a, rgb_b):
    arr = wear[:, :, None] * np.asarray(rgb_a, float) + (1.0 - wear[:, :, None]) * np.asarray(rgb_b, float)
    arr += speck[:, :, None] * 0.85
    arr[pits] -= np.array([15.0, 16.0, 18.0])
    return Image.fromarray(np.uint8(np.clip(arr, 6, 248)), "RGB")

# Calibrated directly from 01_komut_110.jpg normal white lighting:
TEX_COURSE_TOP  = make_course_tex((92.0, 104.0, 128.0), (110.0, 120.0, 140.0))  # Course 4: Cool Slate-Blue Frieze
TEX_COURSE_MID  = make_course_tex((66.0,  71.0,  86.0), ( 84.0,  89.0, 102.0))  # Course 3: Cool Slate-Graphite Center
TEX_COURSE_LOW2 = make_course_tex((70.0,  73.0,  82.0), ( 58.0,  61.0,  70.0))  # Course 2: Lower-Mid Gunmetal Slate
TEX_COURSE_DADO = make_course_tex((76.0,  73.0,  64.0), ( 60.0,  59.0,  55.0))  # Course 1: Olive-Taupe Industrial Dado

height4 = mid * 0.22 + speck * 0.55
hgy, hgx = np.gradient(height4)
nx4, ny4, nz4 = -hgx * 0.018, -hgy * 0.018, np.ones((H4, W4))
norm4 = np.sqrt(nx4 * nx4 + ny4 * ny4 + nz4 * nz4)
REV05_NORM = Image.fromarray(np.uint8(np.clip((np.stack((nx4 / norm4, ny4 / norm4, nz4 / norm4), 2) * 0.5 + 0.5) * 255, 0, 255)), "RGB")

mr4 = np.empty((H4, W4, 3), dtype=np.uint8)
mr4[:, :, 0] = 255
mr4[:, :, 1] = np.uint8(np.clip((0.42 + 0.24 * wear + np.maximum(speck, 0) * 0.002) * 255, 1, 255))
mr4[:, :, 2] = np.uint8(np.clip((0.88 - 0.26 * wear) * 255, 1, 255))
REV05_MR = Image.fromarray(mr4, "RGB")

def mat4(name, rgb, met=0.72, rough=0.52, tex=None, mr=None, norm=None):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=[*((255, 255, 255) if tex is not None else rgb), 255],
        baseColorTexture=tex,
        metallicFactor=met,
        roughnessFactor=rough,
        metallicRoughnessTexture=mr,
        normalTexture=norm,
        doubleSided=True,
    )

M4 = {
    "iron_c1": mat4("Course 1 Lower Olive-Taupe Industrial Dado", None, 1.0, 1.0, TEX_COURSE_DADO, REV05_MR, REV05_NORM),
    "iron_c2": mat4("Course 2 Lower-Mid Gunmetal Slate Iron",     None, 1.0, 1.0, TEX_COURSE_LOW2, REV05_MR, REV05_NORM),
    "iron_c3": mat4("Course 3 Mid Bulkhead Slate-Graphite Iron",  None, 1.0, 1.0, TEX_COURSE_MID,  REV05_MR, REV05_NORM),
    "iron_c4": mat4("Course 4 Upper Frieze Cool Slate-Blue Steel",None, 1.0, 1.0, TEX_COURSE_TOP,  REV05_MR, REV05_NORM),
    "lining":  mat4("Structural Charcoal Steel Backing Liner", (42, 46, 55), 0.78, 0.56),
    "cut":     mat4("Exposed Brushed Cold-Steel Plate Edges",  (136, 143, 152), 0.88, 0.34),
    "rib":     mat4("Forged Dark Graphite Support Iron",       (46, 51, 60), 0.82, 0.48),
    "weld":    mat4("Dark Tempered Steel Seam Channel",        (54, 58, 68), 0.80, 0.46),
    "caution": mat4("Industrial Muted Yellow Caution Tabs",    (190, 168, 58), 0.25, 0.62),
}

outer_oct = [(-17.0, -21.5), (17.0, -21.5), (24.5, -12.5), (24.5, 12.5),
             (17.0, 21.5), (-17.0, 21.5), (-24.5, 12.5), (-24.5, -12.5)]

def bend_y(x):
    t = np.clip((abs(x) - 16.14) / (24.5 - 16.14), 0, 1)
    return -2.55 * t * t * (3 - 2 * t)

def aperture_weight(x, z):
    distance = 1e6
    for c in (-10.75, 10.75):
        lo, hi = c - 5.36, c + 5.36
        dx = max(lo - x, 0.0, x - hi)
        dz = max(-7.18 - z, 0.0, z - 17.18)
        distance = min(distance, math.hypot(dx, dz))
    # Smooth 1.22-stud roll around +/-5.36 grilles so |x| <= 4.14 around the central fan ring is 100% flat!
    t = np.clip(1.0 - distance / 1.22, 0, 1)
    return t * t * (3 - 2 * t)

def wall_y(x, z):
    q = np.clip((z - 9.0) / 4.5, 0, 1)
    q = q * q * (3 - 2 * q)
    depth = 1.50 * (1 - q) + 0.12 * q
    return bend_y(x) - depth * aperture_weight(x, z)

def clip_poly_halfplane(poly, a, b):
    def signed(p):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    out = []
    for s, e in zip(poly, poly[1:] + poly[:1]):
        ds, de = signed(s), signed(e)
        ins, ine = ds >= -1e-9, de >= -1e-9
        if ins != ine:
            q = ds / (ds - de)
            out.append((s[0] + (e[0] - s[0]) * q, s[1] + (e[1] - s[1]) * q))
        if ine:
            out.append(e)
    clean = []
    for q in out:
        if not clean or math.dist(q, clean[-1]) > 1e-6:
            clean.append(q)
    if len(clean) > 1 and math.dist(clean[0], clean[-1]) < 1e-6:
        clean.pop()
    return clean

def clip_to_octagon(poly):
    for a, b in zip(outer_oct, outer_oct[1:] + outer_oct[:1]):
        if not poly:
            break
        poly = clip_poly_halfplane(poly, a, b)
    return poly

BOX_X = 4.10
BOX_Z0, BOX_Z1 = FAN_Z - 4.10, FAN_Z + 4.10  # [-2.30, +5.90] — 100% flat inside shroud flange (R_out=4.52)!

xcuts = [-24.5, -17.74, -17.34, -17.0, -16.74, -16.44, -16.14,
         -5.36, -5.06, -4.76, -BOX_X, -LOUVRE_X, 0.0, LOUVRE_X, BOX_X, 4.76, 5.06, 5.36,
         16.14, 16.44, 16.74, 17.0, 17.34, 17.74, 24.5]
zcuts = sorted(set([-21.5, -12.5, -8.78, -8.38, -7.98, -7.78, -7.48, -7.18, BOX_Z0, -2.0,
                    BOX_Z1, 8.5, 9.50, 11.0, 12.50, 13.5, 17.18, 17.48, 17.78, 18.18, 18.78, 21.5]))
bands = [-21.5, -12.5, -2.0, 8.5, 21.5]

def fan_annulus_quads(N=48):
    polys = []
    for k in range(N):
        th0 = 2.0 * math.pi * k / N
        th1 = 2.0 * math.pi * (k + 1) / N
        def sq_pt(th):
            c, s = math.cos(th), math.sin(th)
            scale = BOX_X / max(abs(c), abs(s))
            return (c * scale, FAN_Z + s * scale)
        ci0 = (FAN_HOLE_R * math.cos(th0), FAN_Z + FAN_HOLE_R * math.sin(th0))
        ci1 = (FAN_HOLE_R * math.cos(th1), FAN_Z + FAN_HOLE_R * math.sin(th1))
        sq0, sq1 = sq_pt(th0), sq_pt(th1)
        th_mid = 0.5 * (th0 + th1)
        sq_m = sq_pt(th_mid)
        ci_m = (FAN_HOLE_R * math.cos(th_mid), FAN_Z + FAN_HOLE_R * math.sin(th_mid))
        polys.append([ci0, sq0, sq_m, ci_m])
        polys.append([ci_m, sq_m, sq1, ci1])
    return polys

ANNULUS_POLYS = fan_annulus_quads(48)

def base_wall_polys():
    for i in range(len(xcuts) - 1):
        x1, x2 = xcuts[i], xcuts[i + 1]
        for j in range(len(zcuts) - 1):
            z1, z2 = zcuts[j], zcuts[j + 1]
            grille_hole = (((x1 >= 5.36 - 1e-6 and x2 <= 16.14 + 1e-6) or
                            (x1 >= -16.14 - 1e-6 and x2 <= -5.36 + 1e-6))
                           and z1 >= -7.18 - 1e-6 and z2 <= 17.18 + 1e-6)
            louvre_hole = (x1 >= -LOUVRE_X - 1e-6 and x2 <= LOUVRE_X + 1e-6
                           and z1 >= LOUVRE_Z0 - 1e-6 and z2 <= LOUVRE_Z1 + 1e-6)
            in_fan_box = (x1 >= -BOX_X - 1e-6 and x2 <= BOX_X + 1e-6
                          and z1 >= BOX_Z0 - 1e-6 and z2 <= BOX_Z1 + 1e-6)
            if grille_hole or louvre_hole or in_fan_box:
                continue
            yield [(x1, z1), (x2, z1), (x2, z2), (x1, z2)]
    for ap in ANNULUS_POLYS:
        above = clip_poly_halfplane(ap, (-10.0, -2.0), (10.0, -2.0))
        below = clip_poly_halfplane(ap, (10.0, -2.0), (-10.0, -2.0))
        if len(above) >= 3:
            yield above
        if len(below) >= 3:
            yield below

def extruded_cells(items, front_y, back_y, liner=False):
    verts, fidx, bidx, face = [], {}, {}, []
    def get(x, z, which):
        key = (round(float(x), 5), round(float(z), 5))
        cache = fidx if which == 0 else bidx
        if key not in cache:
            cache[key] = len(verts)
            y = (front_y if which == 0 else back_y) + wall_y(*key)
            if liner and which == 0:
                y -= 0.35 * aperture_weight(*key)
            verts.append((key[0], y, key[1]))
        return cache[key]
    for poly in items:
        if len(poly) < 3:
            continue
        a = [get(x, z, 0) for x, z in poly]
        b = [get(x, z, 1) for x, z in poly]
        for j in range(1, len(poly) - 1):
            if a[0] != a[j] and a[j] != a[j + 1] and a[0] != a[j + 1]:
                face.append((a[0], a[j], a[j + 1]))
                face.append((b[0], b[j + 1], b[j]))
    edges = {}
    for a, b, c in face[::2]:
        for u, v in ((a, b), (b, c), (c, a)):
            k = (min(u, v), max(u, v))
            edges.setdefault(k, []).append((u, v))
    back_of = {fidx[k]: bidx[k] for k in fidx}
    for key, uses in edges.items():
        if len(uses) != 1:
            continue
        a, b = uses[0]
        A, B = back_of[a], back_of[b]
        face.extend(((a, b, B), (a, B, A)))
    m = trimesh.Trimesh(vertices=np.asarray(verts), faces=np.asarray(face), process=False)
    m.remove_unreferenced_vertices()
    return m

BUCKET4 = {}
def add4(zone, kind, mesh):
    v = mesh.vertices
    uv = np.stack(((v[:, 0] + 25.0) / 50.0, (v[:, 2] + 22.0) / 44.0), axis=1)
    BUCKET4.setdefault((zone, kind), []).append((v, mesh.faces, uv))

def bar4(a, b, r, zone, kind, sections=8):
    a = np.asarray(a, float); b = np.asarray(b, float); d = b - a; L = np.linalg.norm(d)
    if L < 1e-4: return
    g = trimesh.creation.cylinder(radius=r, height=L, sections=sections)
    g.apply_transform(trimesh.geometry.align_vectors((0, 0, 1), d / L))
    g.apply_translation((a + b) * 0.5)
    add4(zone, kind, g)

def box4(x, y, z, sx, sy, sz, zone, kind):
    g = trimesh.creation.box(extents=(sx, sy, sz))
    g.apply_translation((x, y, z))
    add4(zone, kind, g)

liner_polys = [q for raw_p in base_wall_polys() if len(q := clip_to_octagon(raw_p)) >= 3]
liner_mesh = extruded_cells(liner_polys, 15.48, 16.12, liner=True)
add4("REAR_LOAD_BEARING_LINER", "lining", liner_mesh)

course_polys = [[] for _ in range(4)]
for raw_p in base_wall_polys():
    q = clip_to_octagon(raw_p)
    if len(q) < 3:
        continue
    cz = sum(p[1] for p in q) / len(q)
    band = next(i for i in range(4) if bands[i] - 1e-5 <= cz <= bands[i + 1] + 1e-5)
    margin = 0.060
    z_lo = bands[band] + (margin if band > 0 else -1.0)
    z_hi = bands[band + 1] - (margin if band < 3 else -1.0)
    q2 = clip_poly_halfplane(q, (-30.0, z_lo), (30.0, z_lo))
    q2 = clip_poly_halfplane(q2, (30.0, z_hi), (-30.0, z_hi))
    if len(q2) >= 3:
        course_polys[band].append(q2)

for i, polys in enumerate(course_polys):
    p = extruded_cells(polys, 15.13, 15.40)
    add4(f"ROLLED_IRON_COURSE_{i + 1}", f"iron_c{i + 1}", p)

for z in bands[1:-1]:
    if abs(z - (-2.0)) < 0.1:
        spans = [(-23.8, -16.35), (-5.10, -3.95), (3.95, 5.10), (16.35, 23.8)]
    elif z < -7.18:
        spans = [(-23.8, 23.8)]
    else:
        spans = [(-23.8, -16.35), (-5.10, 5.10), (16.35, 23.8)]
    for lo, hi in spans:
        for x0, x1 in zip(np.linspace(lo, hi, 6)[:-1], np.linspace(lo, hi, 6)[1:]):
            bar4((x0, 15.14 + bend_y(x0), z), (x1, 15.14 + bend_y(x1), z), 0.032, "STAMPED_COURSE_WELDS", "weld", 6)

for sgn in (-1, 1):
    x = sgn * 17.0
    bar4((x, 15.04 + bend_y(x), -12.45), (x, 15.04 + bend_y(x), 12.45), 0.067, "OCTAGON_WING_FOLD", "cut", 8)

for a, b in zip(outer_oct, outer_oct[1:] + outer_oct[:1]):
    bar4((a[0], 15.03 + bend_y(a[0]), a[1]), (b[0], 15.03 + bend_y(b[0]), b[1]), 0.096, "BENT_EDGE_IRON", "rib", 9)

for side in (-1, 1):
    x = side * 21.12; tag = "L" if side < 0 else "R"; bend = bend_y(x)
    box4(x, 15.08 + bend, 3.4, 0.30, 0.33, 13.8, "SERVICE_MARKER_" + tag, "rib")
    box4(x, 14.88 + bend, 5.5, 0.115, 0.075, 7.5, "SERVICE_MARKER_" + tag, "weld")
    for z in (-3.3, 10.3):
        box4(x, 14.76 + bend, z, 0.53, 0.16, 0.30, "SERVICE_MARKER_" + tag, "cut")
    for k in range(10):
        xx = side * 10.75 - 3.97 + k * 0.85
        bar4((xx - 0.14, 15.03, -8.07), (xx + 0.10, 15.03, -7.94), 0.047, "REAR_SAFETY_TABS", "caution", 6)

rev05_scene = trimesh.Scene()
rev05_tris = 0
for (zone, kind), pieces in BUCKET4.items():
    vv, ff, uu, off = [], [], [], 0
    for v, f, u in pieces:
        vv.append(v); ff.append(f + off); uu.append(u); off += len(v)
    g = trimesh.Trimesh(vertices=np.concatenate(vv), faces=np.concatenate(ff), process=False)
    g.visual = trimesh.visual.texture.TextureVisuals(uv=np.concatenate(uu), material=M4[kind])
    nm = f"{zone}__{kind}"
    rev05_scene.add_geometry(g, geom_name=nm, node_name=nm)
    rev05_tris += len(g.faces)

GLB_REV05_PATH = EXP / "REACTOR_REAR_BULKHEAD_IRON_REV05_TURBINE_PORT.glb"
GLB_REV05_PATH.write_bytes(rev05_scene.export(file_type="glb"))
rev05_ver = trimesh.load(GLB_REV05_PATH, force="scene", process=False)
print(f"[OK] {GLB_REV05_PATH.name}: {len(rev05_ver.geometry)} meshes, {rev05_tris:,} tris, {GLB_REV05_PATH.stat().st_size/1e6:.2f} MB")


# ============================================================================
# 2. RAZOR-SHARP 10-BLADE CNC REAR TURBINE & DEEP NICKEL-STEEL PLENUM
#    (NO coarse normal map! Split hard-surface crease normals + 64-seg rings!)
# ============================================================================
def make_fine_cnc_tex(rgb, seed=811):
    """Ultra-fine 1024x1024 anisotropic brushed steel texture — crisp, clean, zero blotchy blur!"""
    rr = np.random.default_rng(seed)
    streak = gaussian_filter(rr.standard_normal((1024, 1024)), sigma=(0.8, 12.0), mode="wrap") * 3.2
    micro_g = rr.standard_normal((1024, 1024)) * 0.9
    arr = np.empty((1024, 1024, 3), float)
    arr[:] = rgb
    arr += (streak + micro_g)[..., None] * np.array([0.94, 0.97, 1.0])
    return Image.fromarray(np.uint8(np.clip(arr, 8, 250)), "RGB")

CNC_SHROUD = make_fine_cnc_tex((64, 68, 80), 811)   # Matches sampled fan shroud RGB(70, 70, 82) in 01_komut_110!
CNC_BLADE  = make_fine_cnc_tex((52, 57, 68), 812)   # Dark forged titanium-gunmetal airfoil body
CNC_TUNNEL = make_fine_cnc_tex((38, 43, 52), 813)   # Deep steel exhaust duct shell

def tpbr(name, color=(255, 255, 255), met=0.84, rough=0.34, tex=None, emi=(0.0, 0.0, 0.0)):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=[*((255, 255, 255) if tex is not None else color), 255],
        metallicFactor=met,
        roughnessFactor=rough,
        baseColorTexture=tex,
        emissiveFactor=emi,
        doubleSided=True,
    )

TMATS = {
    "shroud":      tpbr("CNC machined slate-gunmetal cowling", None, 0.86, 0.34, CNC_SHROUD),
    "blade":       tpbr("Forged titanium-gunmetal turbine blade", None, 0.90, 0.27, CNC_BLADE),
    "tunnel":      tpbr("Heavy ribbed exhaust tunnel steel", None, 0.80, 0.44, CNC_TUNNEL),
    "edge":        tpbr("Razor-machined cold-steel bevel", (166, 174, 186), 0.94, 0.20),
    "nickel":      tpbr("Brushed industrial nickel-steel manifold", (122, 130, 142), 0.90, 0.28),
    "dark":        tpbr("Deep acoustic duct liner", (20, 24, 31), 0.60, 0.58),
    "hazard":      tpbr("Crisp light-grey containment stripe enamel", (208, 212, 218), 0.20, 0.62),
    "blue_plenum": tpbr("Recessed cobalt cooling diffuser", (72, 148, 255), 0.10, 0.28, emi=(0.45, 0.72, 1.00)),
    "duct_lamp":   tpbr("Internal exhaust tunnel service lamp", (218, 232, 248), 0.14, 0.26, emi=(0.76, 0.85, 0.98)),
    "cool_beacon": tpbr("Deep plenum cool-steel inspection lamp", (175, 208, 248), 0.16, 0.28, emi=(0.55, 0.72, 0.96)),
}

TBINS = {}
def t_add(node_name, mat_key, mesh, hard_crease=True):
    if len(mesh.faces) == 0:
        return
    g = mesh.copy()
    if hard_crease:
        # Unmerge vertices so every chamfer & 90-degree step gets razor-sharp per-face hard-surface normals!
        g.unmerge_vertices()
    v = np.asarray(g.vertices, float)
    f = np.asarray(g.faces, int)
    u = np.stack(((v[:, 0] + v[:, 1] * 0.5) / 6.0, (v[:, 2] + v[:, 1] * 0.25) / 6.0), axis=1)
    b = TBINS.setdefault((node_name, mat_key), [[], [], []])
    off = sum(len(x) for x in b[0])
    b[0].append(v); b[1].append(f + off); b[2].append(u)

def t_box(node, mat_k, c, ext):
    g = trimesh.creation.box(extents=ext)
    g.apply_translation(c)
    t_add(node, mat_k, g, hard_crease=True)

def t_cyl(node, mat_k, a, b, r, sections=32, hard=False):
    a = np.asarray(a, float); b = np.asarray(b, float); d = b - a; L = np.linalg.norm(d)
    if L < 1e-5: return
    g = trimesh.creation.cylinder(radius=r, height=L, sections=sections)
    g.apply_transform(trimesh.geometry.align_vectors((0, 0, 1), d / L))
    g.apply_translation((a + b) * 0.5)
    t_add(node, mat_k, g, hard_crease=hard)

def t_annulus(node, mat_k, y0, y1, r_in0, r_out0, r_in1=None, r_out1=None, segs=64, cx=FAN_X, cz=FAN_Z):
    """64-segment CNC-machined ring with split axial/radial face groups so rim corners are razor-sharp while cylinder arcs stay silky smooth!"""
    if r_in1 is None: r_in1 = r_in0
    if r_out1 is None: r_out1 = r_out0
    # Emit each of the 4 surface bands (front cap, back cap, inner bore, outer rim) with independent vertices
    # -> smooth circumferential curvature + 100% razor-sharp 90-deg / beveled step corners!
    bands_spec = [
        ((y0, r_in0), (y0, r_out0), False),  # Front face
        ((y1, r_in1), (y1, r_out1), True),   # Back face
        ((y0, r_in0), (y1, r_in1),  True),   # Inner bore
        ((y0, r_out0),(y1, r_out1), False),  # Outer cylinder
    ]
    for (ya, ra), (yb, rb), flip in bands_spec:
        if abs(ya - yb) < 1e-6 and abs(ra - rb) < 1e-6:
            continue
        vs, fs = [], []
        for yv, rv in ((ya, ra), (yb, rb)):
            for j in range(segs):
                th = 2.0 * math.pi * j / segs
                vs.append((cx + rv * math.cos(th), yv, cz + rv * math.sin(th)))
        for j in range(segs):
            k = (j + 1) % segs
            aa, bb, cc, dd = j, k, segs + j, segs + k
            if flip:
                fs.extend(((aa, cc, bb), (bb, cc, dd)))
            else:
                fs.extend(((aa, bb, cc), (bb, dd, cc)))
        g = trimesh.Trimesh(vertices=np.asarray(vs), faces=np.asarray(fs), process=False)
        t_add(node, mat_k, g, hard_crease=False)

# A) Precision 64-Segment Multi-Stepped Machined Intake Cowling & Vertical Flanking Stripes
t_annulus("TURBINE_SHROUD_FLANGE", "shroud", 14.88, 15.34, 3.90, 4.52, 3.90, 4.56, segs=64)
t_annulus("TURBINE_SHROUD_OUTER_BEVEL", "edge", 14.80, 14.89, 4.38, 4.50, 4.44, 4.54, segs=64)
t_annulus("TURBINE_SHROUD_LIP",    "edge",   14.72, 14.88, 3.74, 3.98, 3.88, 4.18, segs=64)
t_annulus("TURBINE_SHROUD_STEP",   "dark",   14.86, 15.48, 3.68, 3.76, 3.68, 3.76, segs=64)
t_annulus("TURBINE_SHROUD_THROAT", "shroud", 15.46, 17.00, 3.70, 3.94, 3.70, 3.94, segs=64)
t_annulus("TURBINE_STATOR_TRACK",  "edge",   15.52, 15.66, 3.64, 3.71, 3.64, 3.71, segs=64)

# 24 crisp hex-head perimeter bolts
for j in range(24):
    th = 2.0 * math.pi * j / 24.0
    bx = FAN_X + 4.24 * math.cos(th)
    bz = FAN_Z + 4.24 * math.sin(th)
    t_cyl("TURBINE_SHROUD_BOLTS", "edge", (bx, 14.78, bz), (bx, 14.90, bz), 0.072, sections=6, hard=True)

# Left & Right Vertical Diagonal Stripe Bars flanking the circular fan shroud (proud of curved wall_y!)
for side in (-1, 1):
    sx = side * 4.62
    wy_mid = 15.13 + wall_y(sx, FAN_Z)
    t_box("TURBINE_FLANK_STRIPE_BACK", "dark", (sx, wy_mid - 0.06, FAN_Z + 0.1), (0.44, 0.08, 7.2))
    for sz in np.arange(FAN_Z - 3.1, FAN_Z + 3.2, 0.86):
        wy0 = 15.13 + wall_y(sx, sz) - 0.12
        wy1 = 15.13 + wall_y(sx, sz + 0.54) - 0.12
        pts = np.array([
            [sx - 0.19, wy0, sz],
            [sx + 0.19, wy0, sz + 0.26],
            [sx + 0.19, wy1, sz + 0.58],
            [sx - 0.19, wy1, sz + 0.32],
        ])
        t_add("TURBINE_FLANK_STRIPES", "hazard", trimesh.Trimesh(vertices=pts, faces=[[0, 1, 2], [0, 2, 3]], process=False), hard_crease=True)

# B) Upper Recessed Cobalt-Blue Louvered Cooling Intake Vent (X in [-3.76, +3.76], Z in [9.50, 12.50])
lv_zc = 0.5 * (LOUVRE_Z0 + LOUVRE_Z1)
lv_zh = LOUVRE_Z1 - LOUVRE_Z0
for c_pt, ext_pt in [
    ((0.0, 15.42, LOUVRE_Z1 + 0.16), (LOUVRE_X * 2 + 0.68, 1.35, 0.32)),
    ((0.0, 15.42, LOUVRE_Z0 - 0.16), (LOUVRE_X * 2 + 0.68, 1.35, 0.32)),
    ((-LOUVRE_X - 0.18, 15.42, lv_zc), (0.36, 1.35, lv_zh + 0.64)),
    (( LOUVRE_X + 0.18, 15.42, lv_zc), (0.36, 1.35, lv_zh + 0.64)),
]:
    t_box("UPPER_LOUVRE_FRAME", "shroud", c_pt, ext_pt)

t_box("UPPER_LOUVRE_BOX", "dark", (0.0, 17.35, lv_zc), (LOUVRE_X * 2 + 0.4, 2.10, lv_zh + 0.4))
t_box("UPPER_LOUVRE_DIFFUSER", "blue_plenum", (0.0, 15.62, lv_zc), (LOUVRE_X * 2 - 0.12, 0.12, lv_zh - 0.12))
for mx in (-1.35, 1.35):
    t_box("UPPER_LOUVRE_MULLION", "shroud", (mx, 15.36, lv_zc), (0.12, 0.65, lv_zh - 0.08))
for lz in np.linspace(LOUVRE_Z0 + 0.32, LOUVRE_Z1 - 0.32, 7):
    slat = trimesh.creation.box(extents=(LOUVRE_X * 2 - 0.12, 0.22, 0.052))
    slat.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-14), [1, 0, 0]))
    slat.apply_translation((0.0, 15.35, lz))
    t_add("UPPER_LOUVRE_SLATS", "edge", slat, hard_crease=True)

# C) SEPARATELY NAMED 10-BLADE RAZOR-SHARP CNC TURBINE ROTOR (TURBINE_ROTOR__*)!
ROTOR_Y = 16.25
# Stepped CNC hub drum + beveled locking rings + 10 socket bolts + satin-steel center shaft locknut (ZERO copper!)
t_annulus("TURBINE_ROTOR", "shroud", ROTOR_Y - 0.40, ROTOR_Y + 0.62, 0.02, 1.12, 0.02, 1.12, segs=48)
t_annulus("TURBINE_ROTOR", "edge",   ROTOR_Y - 0.48, ROTOR_Y - 0.38, 0.76, 1.08, 0.80, 1.12, segs=48)
t_annulus("TURBINE_ROTOR", "shroud", ROTOR_Y - 0.86, ROTOR_Y - 0.46, 0.02, 0.56, 0.02, 0.74, segs=48)
t_annulus("TURBINE_ROTOR", "nickel", ROTOR_Y - 0.96, ROTOR_Y - 0.84, 0.16, 0.34, 0.16, 0.42, segs=32)
t_cyl("TURBINE_ROTOR", "edge", (FAN_X, ROTOR_Y - 1.02, FAN_Z), (FAN_X, ROTOR_Y - 0.86, FAN_Z), 0.15, sections=6, hard=True)

N_BLADES = 10  # Reduced slightly from 12 -> 10 per user feedback, matching 01_komut_110.jpg!
for hb_i in range(N_BLADES):
    hth = 2.0 * math.pi * (hb_i + 0.5) / N_BLADES
    t_cyl("TURBINE_ROTOR", "edge",
          (FAN_X + 0.92 * math.cos(hth), ROTOR_Y - 0.54, FAN_Z + 0.92 * math.sin(hth)),
          (FAN_X + 0.92 * math.cos(hth), ROTOR_Y - 0.44, FAN_Z + 0.92 * math.sin(hth)), 0.058, sections=6, hard=True)

for b_i in range(N_BLADES):
    ang = 2.0 * math.pi * b_i / N_BLADES + math.radians(10.0)
    ca, sa = math.cos(ang), math.sin(ang)

    # 1) Machined root trunnion cuff clamping blade into hub
    p_r0 = (FAN_X + 1.04 * ca, ROTOR_Y + 0.02, FAN_Z + 1.04 * sa)
    p_r1 = (FAN_X + 1.32 * ca, ROTOR_Y + 0.02, FAN_Z + 1.32 * sa)
    t_cyl("TURBINE_ROTOR", "nickel", p_r0, p_r1, 0.22, sections=16, hard=False)

    # 2) Precision 6-point hexagonal-airfoil hard-surface blade body (r = 1.22 -> 3.58)
    r_root, r_tip = 1.22, 3.58
    chord_root, chord_tip = 1.02, 0.54
    pitch_root, pitch_tip = math.radians(36.0), math.radians(24.0)
    secs = np.linspace(r_root, r_tip, 8)

    bv, bf = [], []
    lev, lef = [], []  # Separate bright cold-steel leading-edge bevel strip!
    for r_s in secs:
        u = (r_s - r_root) / (r_tip - r_root)
        ch = chord_root * (1.0 - u) + chord_tip * u
        pt = pitch_root * (1.0 - u) + pitch_tip * u
        thk = 0.115 * (1.0 - 0.42 * u)
        dy = 0.5 * ch * math.sin(pt)
        dt = 0.5 * ch * math.cos(pt)
        # Normal to chord in (y, t) plane: (-cos(pt), sin(pt))
        ny_c, nt_c = -math.cos(pt), math.sin(pt)

        # 6-point crisp chamfered airfoil cross-section (main body from 14% chord to 100% trailing knife-edge)
        prof_main = [
            (-0.72 * dy + ny_c * thk * 0.45, -0.72 * dt + nt_c * thk * 0.45),
            (-0.10 * dy + ny_c * thk * 0.55, -0.10 * dt + nt_c * thk * 0.55),
            ( 0.85 * dy + ny_c * thk * 0.18,  0.85 * dt + nt_c * thk * 0.18),
            ( 1.00 * dy,                      1.00 * dt),
            ( 0.85 * dy - ny_c * thk * 0.18,  0.85 * dt - nt_c * thk * 0.18),
            (-0.72 * dy - ny_c * thk * 0.45, -0.72 * dt - nt_c * thk * 0.45),
        ]
        for py, pt_t in prof_main:
            bv.append((FAN_X + r_s * ca - pt_t * sa, ROTOR_Y + py, FAN_Z + r_s * sa + pt_t * ca))

        # 4-point razor leading-edge bevel strip (-100% leading knife-edge to -70% chord)
        prof_le = [
            (-1.02 * dy,                      -1.02 * dt),
            (-0.70 * dy + ny_c * thk * 0.47,  -0.70 * dt + nt_c * thk * 0.47),
            (-0.70 * dy - ny_c * thk * 0.47,  -0.70 * dt - nt_c * thk * 0.47),
        ]
        for py, pt_t in prof_le:
            lev.append((FAN_X + r_s * ca - pt_t * sa, ROTOR_Y + py, FAN_Z + r_s * sa + pt_t * ca))

    M_P = 6
    for s_i in range(len(secs) - 1):
        o0, o1 = s_i * M_P, (s_i + 1) * M_P
        for q_i in range(M_P):
            qn = (q_i + 1) % M_P
            bf.extend(((o0 + q_i, o1 + q_i, o1 + qn), (o0 + q_i, o1 + qn, o0 + qn)))
    lt = (len(secs) - 1) * M_P
    for q_i in range(1, M_P - 1):
        bf.append((0, q_i + 1, q_i))
        bf.append((lt, lt + q_i, lt + q_i + 1))
    t_add("TURBINE_ROTOR", "blade", trimesh.Trimesh(vertices=np.asarray(bv), faces=np.asarray(bf), process=False), hard_crease=True)

    for s_i in range(len(secs) - 1):
        o0, o1 = s_i * 3, (s_i + 1) * 3
        for q_i in range(3):
            qn = (q_i + 1) % 3
            lef.extend(((o0 + q_i, o1 + q_i, o1 + qn), (o0 + q_i, o1 + qn, o0 + qn)))
    lef.append((0, 2, 1))
    lt_le = (len(secs) - 1) * 3
    lef.append((lt_le, lt_le + 1, lt_le + 2))
    t_add("TURBINE_ROTOR", "edge", trimesh.Trimesh(vertices=np.asarray(lev), faces=np.asarray(lef), process=False), hard_crease=True)


# D) DEEP 18-STUD BEHIND-FAN EXHAUST TUNNEL, STATOR NACELLE & NICKEL-FINNED CONDENSER PLENUM
t_annulus("EXHAUST_TUNNEL_SHELL", "tunnel", 16.70, 26.80, 3.92, 4.32, 3.92, 4.32, segs=56)
for y_rib in np.linspace(17.6, 26.0, 7):
    t_annulus("EXHAUST_TUNNEL_RIBS", "shroud", y_rib - 0.14, y_rib + 0.14, 3.68, 3.94, 3.68, 3.94, segs=48)

t_cyl("STATOR_MOTOR_NACELLE", "shroud", (FAN_X, 17.15, FAN_Z), (FAN_X, 22.40, FAN_Z), 1.14, sections=36)
t_annulus("STATOR_MOTOR_COLLAR", "nickel", 18.10, 19.65, 1.13, 1.26, 1.13, 1.26, segs=36)
t_cyl("STATOR_TAILCONE", "edge", (FAN_X, 22.40, FAN_Z), (FAN_X, 24.10, FAN_Z), 0.60, sections=24)
for s_i in range(8):
    th = 2.0 * math.pi * s_i / 8.0 + math.pi / 8.0
    p_in = (FAN_X + 1.08 * math.cos(th), 18.05, FAN_Z + 1.08 * math.sin(th))
    p_out = (FAN_X + 3.88 * math.cos(th), 18.35, FAN_Z + 3.88 * math.sin(th))
    t_cyl("STATOR_GUIDE_STRUTS", "nickel", p_in, p_out, 0.15, sections=12)

for th_deg in (35, 145, 215, 325):
    th = math.radians(th_deg)
    px = FAN_X + 3.52 * math.cos(th)
    pz = FAN_Z + 3.52 * math.sin(th)
    t_cyl("TUNNEL_COOLANT_PIPES", "nickel" if th_deg < 180 else "edge", (px, 17.2, pz), (px, 28.5, pz), 0.14, sections=12)

t_box("TUNNEL_CATWALK_DECK", "shroud", (FAN_X, 22.5, FAN_Z - 2.95), (2.35, 10.6, 0.18))
for y_rung in np.linspace(17.6, 27.2, 14):
    t_box("TUNNEL_CATWALK_RUNGS", "edge", (FAN_X, y_rung, FAN_Z - 2.84), (2.20, 0.14, 0.06))

for side in (-1, 1):
    t_box("TUNNEL_SERVICE_LAMP_FRAME", "shroud", (side * 3.58, 20.8, FAN_Z + 0.85), (0.18, 4.6, 0.42))
    t_box("TUNNEL_SERVICE_LAMP_LENS", "duct_lamp", (side * 3.48, 20.8, FAN_Z + 0.85), (0.08, 4.2, 0.22))
t_box("TUNNEL_UPPER_BEACON", "cool_beacon", (FAN_X, 24.8, FAN_Z + 3.48), (0.95, 1.8, 0.10))

PL_X, PL_Z0, PL_Z1 = 6.60, -3.80, 7.60
PL_ZC, PL_ZH = 0.5 * (PL_Z0 + PL_Z1), (PL_Z1 - PL_Z0)
for x0, x1 in [(-PL_X, -3.85), (3.85, PL_X)]:
    t_box("PLENUM_FRONT_ADAPTER", "tunnel", (0.5 * (x0 + x1), 26.85, PL_ZC), (x1 - x0, 0.55, PL_ZH))
t_box("PLENUM_FRONT_ADAPTER", "tunnel", (0.0, 26.85, PL_Z1 - 0.85), (PL_X * 2, 0.55, 1.75))
t_box("PLENUM_FRONT_ADAPTER", "tunnel", (0.0, 26.85, PL_Z0 + 0.85), (PL_X * 2, 0.55, 1.75))

t_box("PLENUM_WALLS", "tunnel", (-PL_X, 30.5, PL_ZC), (0.55, 7.6, PL_ZH))
t_box("PLENUM_WALLS", "tunnel", ( PL_X, 30.5, PL_ZC), (0.55, 7.6, PL_ZH))
t_box("PLENUM_WALLS", "tunnel", (0.0, 30.5, PL_Z1), (PL_X * 2 + 0.55, 7.6, 0.55))
t_box("PLENUM_WALLS", "tunnel", (0.0, 30.5, PL_Z0), (PL_X * 2 + 0.55, 7.6, 0.55))
t_box("PLENUM_REAR_ENDCAP", "shroud", (0.0, 34.10, PL_ZC), (PL_X * 2 + 0.55, 0.65, PL_ZH + 0.55))

for hx in np.linspace(-5.1, 5.1, 12):
    y_tube = 29.6 if abs(hx) > 1.8 else 31.2
    t_cyl("PLENUM_HEAT_EXCHANGER_TUBES", "blade", (hx, y_tube, PL_Z0 + 0.4), (hx, y_tube, PL_Z1 - 0.4), 0.24, sections=14)
    for fz in np.linspace(PL_Z0 + 1.0, PL_Z1 - 1.0, 9):
        fin = trimesh.creation.cylinder(radius=0.42, height=0.055, sections=16)
        fin.apply_translation((hx, y_tube, fz))
        t_add("PLENUM_CONDENSER_FINS", "nickel", fin, hard_crease=True)

for rx in (-4.2, 0.0, 4.2):
    t_box("PLENUM_ENDCAP_RIBS", "edge", (rx, 33.72, PL_ZC), (0.28, 0.22, PL_ZH - 0.8))
for sz in (FAN_Z - 1.6, FAN_Z + 1.8):
    t_box("PLENUM_DEPTH_LIGHT", "duct_lamp", (0.0, 33.68, sz), (8.4, 0.08, 0.20))

for side in (-1, 1):
    t_cyl("PLENUM_OVERHEAD_RISER", "tunnel", (side * 3.4, 30.5, PL_Z1 + 0.1), (side * 3.4, 30.5, PL_Z1 + 4.8), 1.35, sections=24)
    t_cyl("PLENUM_RISER_FLANGE", "edge", (side * 3.4, 30.5, PL_Z1 + 2.4), (side * 3.4, 30.5, PL_Z1 + 2.65), 1.52, sections=24, hard=True)

turb_scene = trimesh.Scene()
turb_tris = 0
for (node_name, mat_key), (vs, fs, uvs) in TBINS.items():
    g = trimesh.Trimesh(vertices=np.concatenate(vs), faces=np.concatenate(fs), process=False)
    g.visual = trimesh.visual.texture.TextureVisuals(uv=np.concatenate(uvs), material=TMATS[mat_key])
    nm = f"{node_name}__{mat_key}"
    turb_scene.add_geometry(g, geom_name=nm, node_name=nm)
    turb_tris += len(g.faces)

GLB_TURB_PATH = EXP / "REACTOR_REAR_TURBINE_AND_PLENUM_01.glb"
GLB_TURB_PATH.write_bytes(turb_scene.export(file_type="glb"))
turb_ver = trimesh.load(GLB_TURB_PATH, force="scene", process=False)
print(f"[OK] {GLB_TURB_PATH.name}: {len(turb_ver.geometry)} meshes, {turb_tris:,} tris, {GLB_TURB_PATH.stat().st_size/1e6:.2f} MB")


# ============================================================================
# 3. NON-DESTRUCTIVE SLATE-IRON PALETTE EDITIONS FOR GRILLES & SIDE HATCHES
#    (Original *_01.glb files remain 100% untouched; *_SLATE_02.glb eliminates
#     the last orange-copper surround sheets so the whole chamber matches 01_komut_110!)
# ============================================================================
def build_slate_edition(src_path: Path, dst_path: Path, mode: str) -> trimesh.Scene:
    sc_in = trimesh.load(src_path, force="scene", process=False)
    sc_out = trimesh.Scene()
    for node in sc_in.graph.nodes_geometry:
        tr, gname = sc_in.graph[node]
        g = sc_in.geometry[gname].copy()
        mat = getattr(g.visual, "material", None)
        if mat is not None:
            mname = getattr(mat, "name", "") or ""
            new_mat = mat.copy()
            if mode == "grille":
                if "00 Worn orange" in mname:
                    new_mat.baseColorTexture = TEX_COURSE_TOP
                    new_mat.baseColorFactor = [255, 255, 255, 255]
                elif "08 Dark heat-stained brass" in mname:
                    new_mat.baseColorFactor = [112, 120, 132, 255]
                elif "10 Unlit orange" in mname:
                    new_mat.baseColorFactor = [190, 168, 58, 255]
            elif mode == "hatch":
                if "01 - Patinated painted steel" in mname:
                    new_mat.baseColorTexture = TEX_COURSE_TOP
                    new_mat.baseColorFactor = [255, 255, 255, 255]
                elif "09 - Worn amber warning" in mname:
                    new_mat.baseColorFactor = [204, 208, 214, 255]
                elif "07 - Integrated equipment number" in mname:
                    # Cool grey-steel sign instead of orange text
                    im_t = getattr(mat, "baseColorTexture", None)
                    if im_t is not None:
                        arr_t = np.asarray(im_t.convert("RGB"), float)
                        # Desaturate orange lettering to crisp cool silver-grey!
                        lum = 0.35 * arr_t[:, :, 0] + 0.45 * arr_t[:, :, 1] + 0.20 * arr_t[:, :, 2]
                        cool = np.stack((lum * 0.96 + 18, lum * 1.00 + 20, lum * 1.08 + 25), axis=2)
                        new_mat.baseColorTexture = Image.fromarray(np.uint8(np.clip(cool, 12, 240)), "RGB")
            g.visual.material = new_mat
        sc_out.add_geometry(g, geom_name=gname, node_name=node, transform=tr)
    dst_path.write_bytes(sc_out.export(file_type="glb"))
    return trimesh.load(dst_path, force="scene", process=False)

crown_glb = trimesh.load(EXP / "REACTOR_CROWN_DECK_AND_RADIAL_PORTS_01.glb", force="scene", process=False)
rev03_side = trimesh.load(EXP / "REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV03_DIAG_OPEN.glb", force="scene", process=False)
win_glb = trimesh.load(EXP / "OBSERVATION_WINDOW_ARMOR_FRAME_01.glb", force="scene", process=False)
grille_glb = build_slate_edition(EXP / "REACTOR_REAR_SERVICE_GRILLES_01.glb", EXP / "REACTOR_REAR_SERVICE_GRILLES_SLATE_02.glb", "grille")
emitter_glb = trimesh.load(EXP / "REACTOR_EMITTER_REV03.glb", force="scene", process=False)
piston_glb = trimesh.load(EXP / "REACTOR_PISTON_GUIDE_01.glb", force="scene", process=False)
hatch_closed_glb = build_slate_edition(EXP / "REACTOR_WALL_HATCH_THROUGH_01.glb", EXP / "REACTOR_WALL_HATCH_THROUGH_SLATE_02.glb", "hatch")
hatch_open_glb = build_slate_edition(EXP / "REACTOR_WALL_HATCH_OPEN_INSPECTION_01.glb", EXP / "REACTOR_WALL_HATCH_OPEN_SLATE_02.glb", "hatch")

def place_scene(dst: trimesh.Scene, src: trimesh.Scene, prefix: str, T=None, hatch_slide=0.0, piston_stroke=0.0):
    if T is None:
        T = np.eye(4)
    for node in src.graph.nodes_geometry:
        local, gname = src.graph[node]
        extra = np.eye(4)
        if hatch_slide != 0.0:
            if "HATCH_LEFT" in gname:
                extra[1, 3] = -5.85 * hatch_slide
            elif "HATCH_RIGHT" in gname:
                extra[1, 3] = 5.85 * hatch_slide
        if piston_stroke != 0.0 and prefix.startswith("PISTON"):
            st = gname.split("__")[0]
            extra[0, 3] = {"STAGE1": 6.6, "STAGE2": 13.2, "STAGE3": 19.8, "PUSHER": 19.8}.get(st, 0.0) * piston_stroke
        dst.add_geometry(src.geometry[gname], geom_name=f"{prefix}_{node}_{gname}", transform=T @ extra @ local)

def rot_from_out(out_dir):
    d = np.asarray(out_dir, float); d /= np.linalg.norm(d)
    inward = -d; y_ax = np.array([0.0, 1.0, 0.0]); z_ax = np.cross(inward, y_ax); z_ax /= np.linalg.norm(z_ax)
    R = np.eye(4); R[:3, 0] = inward; R[:3, 1] = y_ax; R[:3, 2] = z_ax
    return R

def build_scene(deployed=False, include_window=True):
    sc = trimesh.Scene()
    slide = 1.0 if deployed else 0.0
    stroke = 1.0 if deployed else 0.0
    place_scene(sc, crown_glb, "CROWN_DECK", hatch_slide=slide)
    place_scene(sc, rev03_side, "REV03_SIDE")
    place_scene(sc, rev05_ver, "REV05_REAR")
    place_scene(sc, grille_glb, "APPROVED_GRILLES")
    place_scene(sc, turb_ver, "REAR_TURBINE")
    if include_window:
        place_scene(sc, win_glb, "WINDOW_FRAME")

    for label, dir0 in [
        ("UPPER", (0.0, 0.0, 1.0)), ("LEFT", (-1.0, 0.0, 0.0)), ("RIGHT", (1.0, 0.0, 0.0)),
        ("LOWER_LEFT", (-0.72, 0.0, -0.694)), ("LOWER_RIGHT", (0.72, 0.0, -0.694)), ("LOWER", (0.0, 0.0, -1.0)),
    ]:
        d = np.asarray(dir0, float); d /= np.linalg.norm(d)
        R = rot_from_out(d)
        T_em = R.copy(); T_em[:3, 3] = np.array([0.0, -2.70, 0.0]) + d * (16.17 if deployed else 35.97)
        place_scene(sc, emitter_glb, f"EMITTER_{label}", T_em)
        T_pi = R.copy(); T_pi[:3, 3] = np.array([0.0, -2.70, 0.0]) + d * 24.50
        place_scene(sc, piston_glb, f"PISTON_{label}", T_pi, piston_stroke=stroke)
        if label in ("LEFT", "RIGHT"):
            place_scene(sc, hatch_open_glb if deployed else hatch_closed_glb, f"SIDE_HATCH_{label}", T_pi)
    return sc

def cam_pose(eye, target):
    eye = np.asarray(eye, float); target = np.asarray(target, float)
    f = target - eye; f /= np.linalg.norm(f)
    r = np.cross(f, (0.0, 0.0, 1.0)); r /= np.linalg.norm(r)
    up = np.cross(r, f)
    T = np.eye(4); T[:3, :3] = np.stack((r, up, -f), axis=1); T[:3, 3] = eye
    return T

def render_img(sc: trimesh.Scene, eye, target, fov=55, w=1280, h=800):
    ps = pyrender.Scene.from_trimesh_scene(sc, bg_color=[0.020, 0.025, 0.036, 1.0], ambient_light=[0.24, 0.25, 0.28])
    lights = [
        ((0.0, -48.0, 6.0),    (0.92, 0.94, 1.00), 620.0),
        ((-16.0, -10.0, 15.0), (0.88, 0.92, 1.00), 350.0),
        (( 16.0, -10.0, 15.0), (0.88, 0.92, 1.00), 350.0),
        ((0.0, 4.0, 3.0),      (0.90, 0.94, 1.00), 280.0),
        ((0.0, -6.0, -14.0),   (0.84, 0.89, 0.98), 250.0),
        ((0.0, 15.48, 11.0),   (0.28, 0.58, 1.00), 42.0),
        ((0.0, 20.5, 2.2),     (0.82, 0.90, 1.00), 105.0),
        ((0.0, 29.5, 2.5),     (0.85, 0.92, 1.00), 135.0),
        ((-22.0, 28.0, 12.0),  (0.86, 0.91, 1.00), 260.0),
    ]
    for loc, rgb, intens in lights:
        lp = np.eye(4); lp[:3, 3] = loc
        ps.add(pyrender.PointLight(color=np.array(rgb), intensity=intens), pose=lp)
    ps.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)), pose=cam_pose(eye, target))
    rd = pyrender.OffscreenRenderer(w, h)
    rgba, _ = rd.render(ps, flags=pyrender.RenderFlags.RGBA)
    rd.delete()
    return Image.fromarray(rgba, "RGBA").convert("RGB")

sc_cold = build_scene(deployed=False, include_window=True)
sc_open = build_scene(deployed=True, include_window=True)
sc_inside_open = build_scene(deployed=True, include_window=False)

im_cold          = render_img(sc_cold,        (0.0, -54.0, -3.0),  (0.0, 2.0, -0.5),  fov=52)
im_open          = render_img(sc_open,        (0.0, -54.0, -3.0),  (0.0, 2.0, -0.5),  fov=52)
im_fan_close     = render_img(sc_inside_open, (0.6,  -2.2,  2.2),  (0.0, 18.0,  3.2), fov=48)
im_inside_tunnel = render_img(sc_inside_open, (2.25, 19.8,  2.35), (-0.4, 33.5, 1.5), fov=66)
im_ext_plenum    = render_img(sc_inside_open, (-24.0, 38.0, 14.0), (0.0, 23.0,  2.0), fov=54)
im_ports_oblique = render_img(sc_inside_open, (-18.5, -16.5, 11.0),(3.5,  6.0, -8.5), fov=66)

im_fan_close.save(DBG / "TEST_01_ARKA_FAN_10KANAT_KESKIN_YAKIN.png")
im_inside_tunnel.save(DBG / "TEST_02_FAN_ARKASI_IC_TUNEL_NIKEL_CELIK.png")
im_ext_plenum.save(DBG / "TEST_03_DISARIDAN_ARKA_PLENUM_ODASI.png")
im_open.save(DBG / "TEST_04_COK_TONLU_GRIMSI_DEMIR_ODA_ACIK_POZ.png")
im_cold.save(DBG / "TEST_05_COK_TONLU_GRIMSI_DEMIR_ODA_KAPALI_POZ.png")

im_ref_full = Image.open(ROOT / "reactor_startup/reference/01_komut_110.jpg").convert("RGB")
rw, rh = im_ref_full.size
im_ref_chamber = im_ref_full.crop((int(rw * 0.03), int(rh * 0.22), int(rw * 0.97), int(rh * 0.67)))

board = Image.new("RGB", (2040, 1430), (13, 17, 25))
draw = ImageDraw.Draw(board)
bold_p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
reg_p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_title = ImageFont.truetype(bold_p, 27)
f_sub = ImageFont.truetype(reg_p, 16)
f_lbl = ImageFont.truetype(bold_p, 13)

draw.text((30, 16), "FAZ 2 PAKET A (REV03 — ÇOK TONLU GRİMSİ-DEMİR ODA + KESKİN 10 KANATLI ARKA TÜRBİN)", font=f_title, fill=(242, 246, 252))
draw.text((30, 54), "Bakırımsı tonlar tamamen kaldırıldı -> 01_komut_110 çok tonlu arduvaz-mavi / grafit-demir / zeytuni-gri paletine geçildi; fan 10 kanada düşürülüp CNC keskinliğine yükseltildi.", font=f_sub, fill=(176, 198, 224))

panels = [
    (im_cold,          30,  94, 640, 405, "1) COLD POZU (Camdan) • Çok Tonlu Grimsi-Demir Oda + 10 Kanatlı Arka Fan"),
    (im_open,         700,  94, 640, 405, "2) DEPLOYED POZU (Camdan) • 6 Kapak Açık + 6 Yayıcı İleride + Arka Türbin"),
    (im_ref_chamber, 1370,  94, 640, 405, "3) REFERANS ODA (01_komut_110) • Üst Mavi-Gri / Orta Grafit / Alt Haki-Gri Palet"),
    (im_fan_close,     30, 522, 640, 405, "4) KESKİN 10 KANATLI ARKA FAN YAKIN PLAN • Pahlı Çelik Hücum Kenarları & Üst Panjur"),
    (im_inside_tunnel,700, 522, 640, 405, "5) FAN ARKASI TÜNEL (İç Kamera) • Nikel-Çelik Eşanjör Boruları, Stator & Kedi Yolu"),
    (im_ports_oblique,1370,522, 640, 405, "6) ODA İÇİ GENEL • Çok Tonlu Sekizgen Duvarlar, 4 Sürgülü Kapak & Radyatörler"),
]

for im, x, y, w, h, cap in panels:
    contained = ImageOps.contain(im, (w - 6, h - 38), Image.Resampling.LANCZOS)
    board.paste(contained, (x + (w - contained.width) // 2, y + 33 + (h - 36 - contained.height) // 2))
    draw.rectangle((x, y, x + w, y + h), outline=(66, 84, 108), width=2)
    draw.rectangle((x, y, x + w, y + 31), fill=(22, 29, 42))
    draw.text((x + 10, y + 7), cap, font=f_lbl, fill=(238, 244, 252))

draw.rectangle((30, 950, 2010, 1402), fill=(18, 24, 35), outline=(58, 76, 98), width=2)
lines = [
    "UYGULANAN 3 ANA DÜZELTME ÖZETİ (Kullanıcı Onayı Bekliyor):",
    "  1) ÇOK TONLU GRİMSİ-DEMİR MİMARİ (01_komut_110 Birebir Renk Kalibrasyonu — %0 Bakırımsı Ton):",
    "      • Üst Kuşak (Z > +8.5): Soğuk Arduvaz Mavi-Gri Çelik  |  Orta Gövde: Grafit-Demir  |  Alt Kuşak & Radyatörler: Mat Zeytuni-Gri / Koyu Çelik + Sarı-Siyah & Beyaz-Gri Şeritler.",
    "  2) ARKA ANA FAN 10 KANATLI & JİLET GİBİ KESKİN HARD-SURFACE CNC KALİTESİ:",
    "      • Kanat sayısı 12 -> 10'a düşürüldü; bulanıklık yapan pürüzlü pas normal-map tamamen kaldırılıp keskin yüzey normalleri (hard-crease) + parlak çelik hücum kenarı pahları eklendi.",
    "  3) FAN ARKASI 18-STUD DOLU EGZOZ & NİKEL-ÇELİK EŞANJÖR ODASI (%0 Boşluk, %0 Bakır):",
    "      • Stator kolları, merkez motor gövdesi, soğutma boruları ve 12 kanatçıklı eşanjör borularının tamamı fırçalanmış nikel-çelik & koyu grafit metale çevrildi.",
    "",
    "CANLI GALERİ (8080): Hem bu panoyu hem de TEST_01..TEST_05 tam çözünürlüklü (1280x800) yakın plan karelerini 8080 portundan anında büyüterek inceleyebilirsin!",
]
cy = 966
for idx_l, line in enumerate(lines):
    ft = f_lbl if idx_l in (0, len(lines) - 1) else f_sub
    col = (245, 214, 138) if idx_l == 0 else ((132, 232, 194) if idx_l == len(lines) - 1 else (210, 222, 236))
    draw.text((48, cy), line, font=ft, fill=col)
    cy += 46 if idx_l == 0 else 44

OUT_SHEET = EXP / "FAZ2_PAKET_A_ODA_FAN_VE_4_YUVA_ONAY.png"
board.save(OUT_SHEET, optimize=True)
print(f"[OK] Master preview saved: {OUT_SHEET} ({OUT_SHEET.stat().st_size/1e6:.2f} MB)")
