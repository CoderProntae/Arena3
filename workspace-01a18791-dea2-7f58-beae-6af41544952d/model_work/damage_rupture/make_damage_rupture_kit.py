#!/usr/bin/env python3
"""FAZ 4 (3B Modelleme Paketi C) — M13: DAMAGE_PIPE_RUPTURE_KIT_01.glb

Faz 3 boru halkasındaki 4 adet PIPE_SPOOL_* kopma modülünün RUPTURED karşılıkları.
Sağlam spool'larla AYNI eksen/uç/flanş düzlemlerinde oturur (değişim: INTACT gizle
<-> RUPTURED göster). Her modül: iki flanşlı uç, ortadan yırtılmış iki boru güdüğü
(gerçek iç delik + et kalınlığı), dışa kıvrık yırtık metal dudaklar, ağız içinde
kriyojenik don halkası, fırlamış/yarılmış kriyo bantları, kopuk metal parçacıklar.

Koordinat: Faz 2/3 ile aynı author uzayı (X, Y=derinlik(ön -Y), Z=yukarı), 1 birim = 1 stud.
Spool tarifleri make_faz3_piping_and_service_bays.py ile birebir: r_main=0.50,
flange() formülü, bant konumları (UPPER y=-8.20..-1.20 bantlar -6.2/-3.2;
REAR z=7.80..1.60 bant 4.70).

Çıktı (ön-izleme onayı için, Studio'ya KURULMAZ):
  model_exports/DAMAGE_PIPE_RUPTURE_KIT_01.glb
  model_exports/DAMAGE_PIPE_RUPTURE_KIT_01_ONAY.png  (6 açılı kanıt sayfası)
"""
from __future__ import annotations
import math, os, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

os.environ["PYOPENGL_PLATFORM"] = "egl"
ROOT = Path("/home/user")
sys.path[:0] = [str(ROOT / ".cache/modeldeps"), str(ROOT / ".cache/modelrender")]
import pyglet
pyglet.options["headless"] = True
import trimesh, pyrender

EXP = ROOT / "model_exports"
EXP.mkdir(parents=True, exist_ok=True)

# ============================================================================
# 1. PBR PALETTE (Faz 3 ile birebir dokular + hasara özel 3 yeni malzeme)
# ============================================================================
W = H = 512
rng = np.random.default_rng(603091)

def wrap_noise(sigma):
    q = gaussian_filter(rng.standard_normal((H, W)), sigma=sigma, mode="wrap")
    return q / (q.std() + 1e-8)

macro = wrap_noise(14)
micro = wrap_noise(2.2)
grain = rng.standard_normal((H, W))
wear = np.clip(0.46 + 0.08 * macro + 0.08 * micro + 0.025 * grain, 0.14, 0.78)
scars = rng.random((H, W)) < 0.007

def make_brushed_metal_tex(rgb, seed=811, streak_sigma=22.0):
    rr = np.random.default_rng(seed)
    fine = rr.standard_normal((H, W)) * 2.2
    streak = gaussian_filter(rr.standard_normal((H, W)), sigma=(1.6, streak_sigma), mode="wrap") * 5.4
    coarse = gaussian_filter(rr.standard_normal((H, W)), sigma=16, mode="wrap") * 3.4
    arr = np.empty((H, W, 3), float)
    arr[:] = rgb
    arr += (fine + streak + coarse)[..., None] * np.array([0.94, 0.97, 1.02])
    return Image.fromarray(np.uint8(np.clip(arr, 10, 248)), "RGB")

NICKEL_PIPE_TEX = make_brushed_metal_tex((128, 136, 148), 812, 26.0)
GUNMETAL_TEX    = make_brushed_metal_tex((46, 51, 60),    819, 18.0)

MR = np.empty((H, W, 3), np.uint8)
MR[:, :, 0] = 255
MR[:, :, 1] = np.uint8(np.clip((0.36 + 0.18 * wear + 0.02 * np.abs(micro)) * 255, 1, 255))
MR[:, :, 2] = np.uint8(np.clip((0.88 - 0.18 * wear) * 255, 1, 255))
METAL_MR = Image.fromarray(MR, "RGB")

hmap = micro * 0.50 + wrap_noise(0.9) * 0.14 + scars * 0.20
gy, gx = np.gradient(hmap)
nx_, ny_, nz_ = -gx * 0.042, -gy * 0.042, np.ones_like(gx)
nlen = np.sqrt(nx_ * nx_ + ny_ * ny_ + nz_ * nz_)
METAL_NORM = Image.fromarray(np.uint8(np.clip((np.stack((nx_, ny_, nz_), 2) / nlen[..., None] * 0.5 + 0.5) * 255, 0, 255)), "RGB")

def pbr(name, color=(255, 255, 255), met=0.80, rough=0.44, tex=None, mr=None, normal=None, emi=(0.0, 0.0, 0.0)):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=[*((255, 255, 255) if tex is not None else color), 255],
        metallicFactor=met, roughnessFactor=rough,
        baseColorTexture=tex, metallicRoughnessTexture=mr, normalTexture=normal,
        emissiveFactor=emi, doubleSided=True,
    )

MATS = {
    "nickel_pipe": pbr("Brushed cryogenic nickel-slate pipe", None, 0.90, 0.34, NICKEL_PIPE_TEX, METAL_MR, METAL_NORM),
    "gunmetal":    pbr("Heavy forged gunmetal housing", None, 0.84, 0.46, GUNMETAL_TEX, None, METAL_NORM),
    "flange":      pbr("Machined ANSI cold-steel flange", (154, 162, 174), 0.92, 0.28),
    "clamp":       pbr("Structural C-channel bracket iron", (42, 47, 56), 0.86, 0.48),
    "cryo_band":   pbr("Cryogenic cobalt identification collar", (46, 108, 176), 0.36, 0.46),
    # FAZ 4 yeni malzemeler (turuncu sahte parlama YOK):
    "pipe_bore":   pbr("Dark pipe inner bore", (24, 28, 35), 0.55, 0.58),
    "torn_steel":  pbr("Heat-blued torn steel lip", (70, 60, 62), 0.85, 0.52, None, METAL_MR, METAL_NORM),
    "frost":       pbr("Cryogenic frost ring", (168, 188, 210), 0.05, 0.95),
}

# ============================================================================
# 2. BUILDER (Faz 3 GroupBuilder çekirdeği + yırtık güdük yardımcıları)
# ============================================================================
def box_uv(mesh: trimesh.Trimesh, scale=9.0) -> np.ndarray:
    v = mesh.vertices
    uv = np.zeros((len(v), 2), dtype=np.float32)
    uv[:, 0] = (v[:, 0] + v[:, 1] * 0.73) / scale
    uv[:, 1] = (v[:, 2] + v[:, 1] * 0.29) / scale
    return uv

def rot_align(z_target):
    zt = np.asarray(z_target, float)
    L = np.linalg.norm(zt)
    if L < 1e-8:
        return np.eye(4)
    zt /= L
    up = np.array([0.0, 0.0, 1.0]) if abs(zt[2]) < 0.92 else np.array([1.0, 0.0, 0.0])
    xa = np.cross(up, zt); xa /= np.linalg.norm(xa)
    ya = np.cross(zt, xa)
    M = np.eye(4); M[:3, 0] = xa; M[:3, 1] = ya; M[:3, 2] = zt
    return M

class GroupBuilder:
    def __init__(self):
        self.buckets: dict[tuple[str, str], list[trimesh.Trimesh]] = {}

    def add(self, group, mat_key, mesh):
        self.buckets.setdefault((group, mat_key), []).append(mesh)

    def cyl(self, group, mat_key, p0, p1, radius, sections=18):
        p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
        d = p1 - p0; L = float(np.linalg.norm(d))
        if L < 1e-5: return
        m = trimesh.creation.cylinder(radius=radius, height=L, sections=sections)
        T = rot_align(d); T[:3, 3] = 0.5 * (p0 + p1)
        m.apply_transform(T)
        self.add(group, mat_key, m)

    def flange(self, group, p_center, axis_dir, pipe_r, bolts=10):
        p_center = np.asarray(p_center, float)
        M = rot_align(axis_dir)
        fl_r = pipe_r * 1.44 + 0.08
        fl_t = max(0.14, pipe_r * 0.28)
        m = trimesh.creation.cylinder(radius=fl_r, height=fl_t, sections=20)
        T = M.copy(); T[:3, 3] = p_center
        m.apply_transform(T); self.add(group, "flange", m)
        m2 = trimesh.creation.cylinder(radius=pipe_r * 1.16 + 0.03, height=fl_t * 1.85, sections=16)
        m2.apply_transform(T); self.add(group, "gunmetal", m2)
        bolt_r = pipe_r + 0.62 * (fl_r - pipe_r)
        for bi in range(bolts):
            ang = 2.0 * math.pi * bi / bolts
            local_pt = np.array([bolt_r * math.cos(ang), bolt_r * math.sin(ang), 0.0])
            wp = p_center + M[:3, :3] @ local_pt
            ax = M[:3, 2] * (fl_t * 0.85)
            self.cyl(group, "clamp", wp - ax, wp + ax, max(0.035, pipe_r * 0.075), sections=6)

    # --- FAZ 4: yırtık boru güdüğü (dış + iç delik + yırtık dudak + don) ---
    def torn_stub(self, group, origin, direction, length, r_out=0.50, r_in=0.44, seed=7, petal_phase=0.0, damage=1.0):
        """Yirtik guduk: boyuna dikis patlamasi + tek yone sismis, duzensiz disli agiz.
        damage>1 daha agir hasar (B gudugu)."""
        jr = np.random.default_rng(seed)
        origin = np.asarray(origin, float)
        M = rot_align(direction)
        R = M[:3, :3]
        NSEG = 36
        stations = np.array([0.0, 0.20, 0.42, 0.62, 0.76, 0.87, 0.95, 1.0])
        th0 = petal_phase  # patlama yonu / dikis acisi
        seg_rand = jr.uniform(0.45, 1.0, NSEG)
        seg_rand = 0.5 * (seg_rand + np.roll(seg_rand, 1))
        finger = jr.uniform(0.0, 1.0, NSEG)
        def flare(t):
            if t < 0.76: return 1.0
            u = (t - 0.76) / 0.24
            return 1.0 + 0.34 * damage * (u * u * (3 - 2 * u))
        def ang_dist(a, b):
            d = abs(a - b) % (2 * math.pi)
            return min(d, 2 * math.pi - d)
        def deform(th, t, rim=False):
            u = 0.0 if t < 0.62 else (t - 0.62) / 0.38
            bulge = 0.30 * damage * (max(0.0, math.cos(th - th0)) ** 2) * u
            seam = math.exp(-(ang_dist(th, th0) ** 2) / (2 * 0.28 ** 2)) * (0.20 * damage * (u ** 1.5))
            k = 1.0 + bulge + seam
            ax = 0.0
            if rim:
                idx = int(round(th / (2 * math.pi) * NSEG)) % NSEG
                k *= 1.0 + 0.17 * damage * seg_rand[idx] * math.sin(7 * th + petal_phase)
                ax = (finger[idx] - 0.55) * 0.16 * length * 0.35 - seam * 0.10
            return k, ax
        def ring_pts(t, r_base, rim=False):
            pts = []
            for i in range(NSEG):
                th = 2 * math.pi * i / NSEG
                k, ax = deform(th, t, rim)
                r = r_base * flare(t) * k
                pts.append(origin + R @ np.array([r * math.cos(th), r * math.sin(th), t * length + ax]))
            return np.array(pts)
        outer = [ring_pts(t, r_out, rim=(k == len(stations) - 1)) for k, t in enumerate(stations)]
        inner = []
        for k, t in enumerate(stations):
            pts = []
            for i in range(NSEG):
                th = 2 * math.pi * i / NSEG
                kk, ax = deform(th, t, rim=(k == len(stations) - 1))
                r = r_in * flare(t) * (1.0 + (kk - 1.0) * 0.85)
                a2 = t * length + ax
                if k == len(stations) - 1:
                    a2 -= 0.09
                pts.append(origin + R @ np.array([r * math.cos(th), r * math.sin(th), a2]))
            inner.append(np.array(pts))

        def strip(rings, i0, i1, flip=False):
            vs, fs = [], []
            for k in range(i0, i1):
                a, b = rings[k], rings[k + 1]
                base = len(vs)
                vs.extend(a); vs.extend(b)
                for i in range(NSEG):
                    j = (i + 1) % NSEG
                    q = [base + i, base + NSEG + i, base + NSEG + j, base + j]
                    if flip: q = q[::-1]
                    fs.append([q[0], q[1], q[2]]); fs.append([q[0], q[2], q[3]])
            return trimesh.Trimesh(vertices=np.array(vs), faces=np.array(fs), process=False)

        # dış gövde: sağlam kısım nickel, yırtık flare kuşağı torn_steel
        self.add(group, "nickel_pipe", strip(outer, 0, 5))
        self.add(group, "torn_steel",  strip(outer, 5, 7))
        # iç delik: bore + don kuşağı (istasyon 4..6 arası içte hafif içerlek)
        self.add(group, "pipe_bore", strip(inner, 0, 7, flip=True))
        frost_rings = []
        for k in (5, 6):
            t = stations[k]
            pts = []
            for i in range(NSEG):
                th = 2 * math.pi * i / NSEG
                r = (r_in - 0.014) * flare(t)
                pts.append(origin + R @ np.array([r * math.cos(th), r * math.sin(th), t * length]))
            frost_rings.append(np.array(pts))
        self.add(group, "frost", strip(frost_rings, 0, 1, flip=True))
        # dudak kenarı (dış rim -> iç rim) + arka halka kapağı
        rim_o, rim_i = outer[-1], inner[-1]
        vs = list(rim_o) + list(rim_i); fs = []
        for i in range(NSEG):
            j = (i + 1) % NSEG
            fs.append([i, NSEG + i, NSEG + j]); fs.append([i, NSEG + j, j])
        self.add(group, "torn_steel", trimesh.Trimesh(vertices=np.array(vs), faces=np.array(fs), process=False))
        b_o, b_i = outer[0], inner[0]
        vs = list(b_o) + list(b_i); fs = []
        for i in range(NSEG):
            j = (i + 1) % NSEG
            fs.append([i, j, NSEG + j]); fs.append([i, NSEG + j, NSEG + i])
        self.add(group, "nickel_pipe", trimesh.Trimesh(vertices=np.array(vs), faces=np.array(fs), process=False))
        # ağız merkezi (parçacıklar için geri ver)
        return origin + R @ np.array([0.0, 0.0, length]), R

    def curled_shard(self, group, mat_key, base, R, th, r_base=0.52, w=0.16, ln=0.42, curl=0.9):
        cw, sw = math.cos(th), math.sin(th)
        vs, fs = [], []
        steps = 4
        for k in range(steps + 1):
            u = k / steps
            rr = r_base + 0.30 * u + curl * 0.16 * u * u
            ax = ln * u - curl * 0.22 * u * u
            c = base + R @ np.array([rr * cw, rr * sw, ax])
            tw = R @ np.array([-sw, cw, 0.0]) * (w * 0.5 * (1 - 0.5 * u))
            vs.append(c - tw); vs.append(c + tw)
        for k in range(steps):
            a = 2 * k
            fs.append([a, a + 2, a + 3]); fs.append([a, a + 3, a + 1])
        self.add(group, mat_key, trimesh.Trimesh(vertices=np.array(vs), faces=np.array(fs), process=False))

    def split_band(self, group, center, direction, r=0.60, width=0.48, arc=(0.3, 3.6), tilt=0.16):
        M = rot_align(direction); R = M[:3, :3]
        center = np.asarray(center, float)
        n = 22; vs, fs = [], []
        for k in range(n + 1):
            th = arc[0] + (arc[1] - arc[0]) * k / n
            for sgn in (-0.5, 0.5):
                p = center + R @ np.array([r * math.cos(th), r * math.sin(th),
                                            sgn * width + tilt * math.cos(th) * width])
                vs.append(p)
        for k in range(n):
            a = 2 * k
            fs.append([a, a + 2, a + 3]); fs.append([a, a + 3, a + 1])
        self.add(group, "cryo_band", trimesh.Trimesh(vertices=np.array(vs), faces=np.array(fs), process=False))

    def export_glb(self, out_path: Path):
        sc = trimesh.Scene()
        total = 0
        for (grp, mat_key), parts in sorted(self.buckets.items()):
            merged = trimesh.util.concatenate(parts)
            merged.visual = trimesh.visual.texture.TextureVisuals(uv=box_uv(merged), material=MATS[mat_key])
            nm = f"{grp}__{mat_key}"
            sc.add_geometry(merged, geom_name=nm, node_name=nm)
            total += len(merged.faces)
        raw = sc.export(file_type="glb")
        out_path.write_bytes(raw)
        trimesh.load(out_path, force="scene", process=False)
        return total, len(raw), len(sc.geometry)

# ============================================================================
# 3. RUPTURED SPOOL ÜRETİMİ (4 modül, sağlam karşılıklarıyla aynı uçlarda)
# ============================================================================
def build_ruptured(gb: GroupBuilder, gid: str, p0, p1, bands_from_p0, seed):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    axis = p1 - p0; L = float(np.linalg.norm(axis)); d = axis / L
    grp = f"PIPE_SPOOL_{gid}_RUPTURED"
    gb.flange(grp, p0 + d * 0.16, d, 0.50, bolts=10)
    gb.flange(grp, p1 - d * 0.16, d, 0.50, bolts=10)
    lenA, lenB = 0.42 * L, 0.40 * L
    mouthA, RA = gb.torn_stub(grp, p0, d, lenA, seed=seed, petal_phase=seed * 0.7, damage=0.9)
    # B güdüğü: basınçla hafif eksen kaçırmış (2.2 derece + 0.09 stud)
    M = rot_align(d); perp = M[:3, 0]
    dB = -d + perp * math.tan(math.radians(3.0)); dB /= np.linalg.norm(dB)
    mouthB, RB = gb.torn_stub(grp, p1 + perp * 0.09, dB, lenB, seed=seed + 37, petal_phase=seed * 1.3 + 2.0, damage=1.25)
    # kıvrık yırtık parçacıklar
    for k, th in enumerate((0.6, 2.5, 4.4)):
        gb.curled_shard(grp, "torn_steel", mouthA - (RA[:3, 2] * 0.10), RA, th + seed, r_base=0.58, ln=0.34 - 0.04 * k)
    for th in (1.4, 3.9):
        gb.curled_shard(grp, "torn_steel", mouthB - (RB[:3, 2] * 0.10), RB, th + seed, r_base=0.60)
    # bantlar: güdük üstünde kalan sağlam, kopma bölgesindeki yarık/fırlamış
    for sb in bands_from_p0:
        c = p0 + d * sb
        if sb < lenA - 0.35:
            gb.cyl(grp, "cryo_band", c - d * 0.24, c + d * 0.24, 0.50 * 1.06, sections=18)
        elif sb > L - lenB + 0.15:
            gb.split_band(grp, c + perp * 0.09, dB, r=0.545, arc=(0.4, 4.1))
            gb.split_band(grp, c + perp * 0.09 - d * 0.05, dB, r=0.545, arc=(4.5, 6.0))
        else:
            gb.split_band(grp, p0 + d * (lenA - 0.55), d, r=0.545, arc=(1.1, 4.6), tilt=0.22)
    # kopmuş cıvata + küçük kelepçe parçası (ağıza takılı, statik)
    bolt_p = mouthA - RA[:3, 2] * 0.04 + RA[:3, 0] * 0.60
    gb.cyl(grp, "clamp", bolt_p - RA[:3, 2] * 0.10, bolt_p + RA[:3, 2] * 0.16 + RA[:3, 1] * 0.06, 0.0375, sections=6)

gb = GroupBuilder()
build_ruptured(gb, "UPPER_LEFT",  (-19.95, -8.20, 15.85), (-19.95, -1.20, 15.85), [2.0, 5.0], seed=11)
build_ruptured(gb, "UPPER_RIGHT", ( 19.95, -8.20, 15.85), ( 19.95, -1.20, 15.85), [2.0, 5.0], seed=23)
build_ruptured(gb, "REAR_LEFT",   (-19.95, 10.80,  7.80), (-19.95, 10.80,  1.60), [3.1],      seed=31)
build_ruptured(gb, "REAR_RIGHT",  ( 19.95, 10.80,  7.80), ( 19.95, 10.80,  1.60), [3.1],      seed=47)

glb_path = EXP / "DAMAGE_PIPE_RUPTURE_KIT_01.glb"
tris, nbytes, nmesh = gb.export_glb(glb_path)
print(f"GLB: {glb_path} | {nmesh} mesh | {tris} ucgen | {nbytes/1e6:.2f} MB")

# ============================================================================
# 4. ONAY RENDERI — 6 açı (author (x,y,z_up) -> render (x, z_up, -y))
# ============================================================================
scene = trimesh.load(glb_path, force="scene", process=False)
Tswap = np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]], float)
scene.apply_transform(Tswap)
ps = pyrender.Scene(bg_color=np.array([13, 16, 22, 255]), ambient_light=np.array([0.35, 0.38, 0.45]))
for node_name in scene.graph.nodes_geometry:
    T, geom = scene.graph[node_name]
    ps.add(pyrender.Mesh.from_trimesh(scene.geometry[geom], smooth=True), pose=T)

def V(x, y, z):  # author noktası -> render noktası
    return np.array([x, z, -y], float)

def look_pose(cam, target, up=np.array([0, 1, 0.0])):
    fwd = target - cam; fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, up); right /= np.linalg.norm(right)
    upv = np.cross(right, fwd)
    M = np.eye(4)
    M[:3, 0] = right; M[:3, 1] = upv; M[:3, 2] = -fwd; M[:3, 3] = cam
    return M

UL = V(-19.95, -4.70, 15.85); ULgap = V(-19.95, -4.63, 15.85)
UR = V( 19.95, -4.70, 15.85)
RL = V(-19.95, 10.80,  4.70)
PAIR = V(-19.95, 3.05, 10.28)
views = [
    ("1) UST SOL SPOOL - 3/4",        UL + np.array([5.4, 2.7, 6.8]),  UL),
    ("2) YIRTIK AGIZ - MAKRO",        ULgap + np.array([1.7, 0.9, 2.1]), ULgap),
    ("3) ARKA SOL (DIKEY) - 3/4",     RL + np.array([4.2, 1.6, 5.2]),  RL),
    ("4) ARKA AGIZ - YANDAN MAKRO",   RL + np.array([2.0, 0.8, 2.3]),  RL + np.array([0, 0.2, 0])),
    ("5) UST SAG - YAN PROFIL",       UR + np.array([8.8, 1.5, 3.6]),  UR),
    ("6) SOL KOSE CIFTI (UST+ARKA)",  PAIR + np.array([8.0, 3.0, 9.5]), PAIR),
]

Wpx = 820
rend = pyrender.OffscreenRenderer(Wpx, Wpx)
key = pyrender.DirectionalLight(color=np.ones(3), intensity=3.2)
fill = pyrender.DirectionalLight(color=np.array([0.75, 0.82, 1.0]), intensity=1.1)
tiles = []
for label, cam, tgt in views:
    cam_node = ps.add(pyrender.PerspectiveCamera(yfov=math.radians(42)), pose=look_pose(cam, tgt))
    k_node = ps.add(key, pose=look_pose(cam + np.array([6, 9, 4.0]), tgt))
    f_node = ps.add(fill, pose=look_pose(cam + np.array([-7, 3, -5.0]), tgt))
    col, _ = rend.render(ps)
    ps.remove_node(cam_node); ps.remove_node(k_node); ps.remove_node(f_node)
    img = Image.fromarray(col)
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, Wpx - 44, Wpx, Wpx], fill=(10, 12, 18))
    dr.text((14, Wpx - 32), label, fill=(214, 226, 240))
    tiles.append(img)
    print("render:", label)

sheet = Image.new("RGB", (Wpx * 2 + 12, Wpx * 3 + 24), (8, 10, 14))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % 2) * (Wpx + 12), (i // 2) * (Wpx + 12)))
out_png = EXP / "DAMAGE_PIPE_RUPTURE_KIT_01_ONAY.png"
sheet.save(out_png)
print("ONAY SAYFASI:", out_png, sheet.size)
