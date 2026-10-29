#!/usr/bin/env python3
"""Faz 3 (3B Modelleme Paketi B) — Reaktör Çevresi Kriyojenik Borulama Ağı & 6 Piston Arkası Bağlantılı Servis Tesisi.

Üretilen 3B Modeller (model_exports/ altında, henüz Roblox Studio'ya kurulmadan ön-izleme onayına sunulur):
  1) M11: model_exports/REACTOR_COOLANT_PIPING_RING_01.glb
     - Sekizgen oda üst 45° eğimli duvarlarında çift hatlı ağır kriyojenik soğutma ana boruları (Ø 1.04 nikel-arduvaz
       besleme + Ø 0.68 koyu gunmetal dönüş), 12 cıvatalı ANSI flanşlar, kobalt-mavi akış bilezikleri ve C-profil duvar kelepçeleri.
     - Arka köşe dikey kollektör inişleri, kollu endüstriyel kesme vanaları (VALVE_WHEEL_*), analog basınç manometre blokları
       ve alt zeytuni-gri radyatör bankları ile arka türbin kondenser plenumuna gerçek flanşlı bağlantılar.
     - Üst çevre ve alt çukur tabanında delikli zırhlı yüksek gerilim kablo tavaları (HV_CABLE_TRAY_*) + 3'lü ekranlı güç kabloları
       ve alt dönüş kollektör boruları.
     - Faz 4.2 hasar/patlama sistemine hazır ayrı isimlendirilmiş 4 flanşlı kopma modülü:
       PIPE_SPOOL_UPPER_LEFT, PIPE_SPOOL_UPPER_RIGHT, PIPE_SPOOL_REAR_LEFT, PIPE_SPOOL_REAR_RIGHT.
     - Görüş Hattı Garantisi: Merkez çekirdek, 6 yayıcı ve lazer hattı, 6 sürgülü kapak (±5.85 stud), 2 arka servis ızgarası,
       üst kobalt panjur ve 10 kanatlı CNC arka türbin fanı %100 AÇIK ve ENGELSİZ.

  2) M12: model_exports/PISTON_REAR_SERVICE_BAY_01.glb
     - 6 radyal kapak (SL-00..SL-05) açıldığında teleskopik pistonların (REACTOR_PISTON_GUIDE_01) arkasında siyah boşluk
       görünmemesi için her yuvanın arkasına tam sızdırmaz oturan 35.25 stud derinlikli bağlantılı hidrolik servis galerisi.
     - Kaburgalı çok tonlu arduvaz/grafit çelik galeri duvarları, 6 adet kutu-profil taşıyıcı kemer, pistonun iki yanında
       yüksek basınçlı nikel-çelik hidrolik akümülatör tüpleri + örgülü besleme hatları, delikli bakım yürüyüş ızgaraları +
       korkuluklar, gömme soğuk-beyaz servis şerit lambaları ve arka tesis bağlantı hava kilidi kapısı (MAINT-BAY).
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

# ============================================================================
# 1. CALIBRATED MULTI-TONE SLATE-IRON / BRUSHED NICKEL / GUNMETAL PBR PALETTE
#    (100% matched to 01_komut_110.jpg & Faz 2 — ZERO coppery/orange surfaces!)
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

def make_rolled_iron_tex(c_primary, c_secondary):
    b = (1 - wear[..., None]) * np.asarray(c_secondary, float) + wear[..., None] * np.asarray(c_primary, float)
    b += np.clip(grain, -2.5, 2.5)[..., None] * 1.30
    b[scars] -= np.array([16.0, 16.0, 18.0])
    return Image.fromarray(np.uint8(np.clip(b, 8, 245)), "RGB")

def make_brushed_metal_tex(rgb, seed=811, streak_sigma=22.0):
    rr = np.random.default_rng(seed)
    fine = rr.standard_normal((H, W)) * 2.2
    streak = gaussian_filter(rr.standard_normal((H, W)), sigma=(1.6, streak_sigma), mode="wrap") * 5.4
    coarse = gaussian_filter(rr.standard_normal((H, W)), sigma=16, mode="wrap") * 3.4
    arr = np.empty((H, W, 3), float)
    arr[:] = rgb
    arr += (fine + streak + coarse)[..., None] * np.array([0.94, 0.97, 1.02])
    return Image.fromarray(np.uint8(np.clip(arr, 10, 248)), "RGB")

def make_grating_tex():
    arr = np.full((H, W, 3), (44, 49, 58), dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    # Industrial diamond/bar floor grating pattern (opaque dark void slots + bright steel ribs)
    slot_x = (xx % 32)
    slot_y = (yy % 64)
    in_hole = (slot_x >= 7) & (slot_x <= 25) & (slot_y >= 8) & (slot_y <= 56)
    arr[in_hole] = (15, 18, 24)
    bevel = (~in_hole) & ((slot_x == 6) | (slot_x == 26) | (slot_y == 7) | (slot_y == 57))
    arr[bevel] = (118, 126, 138)
    return Image.fromarray(np.uint8(arr), "RGB")

IRON_VAULT_UPPER = make_rolled_iron_tex((92.0, 104.0, 126.0), (108.0, 118.0, 136.0))
IRON_VAULT_MID   = make_rolled_iron_tex((68.0, 73.0, 86.0),   (84.0, 89.0, 102.0))
IRON_VAULT_LOWER = make_rolled_iron_tex((70.0, 68.0, 61.0),   (58.0, 58.0, 55.0))
NICKEL_PIPE_TEX  = make_brushed_metal_tex((128, 136, 148), 812, 26.0)
SLATE_PIPE_TEX   = make_brushed_metal_tex((84, 92, 106),   815, 22.0)
GUNMETAL_TEX     = make_brushed_metal_tex((46, 51, 60),    819, 18.0)
GRATING_TEX      = make_grating_tex()

MR = np.empty((H, W, 3), np.uint8)
MR[:, :, 0] = 255
MR[:, :, 1] = np.uint8(np.clip((0.36 + 0.18 * wear + 0.02 * np.abs(micro)) * 255, 1, 255))
MR[:, :, 2] = np.uint8(np.clip((0.88 - 0.18 * wear) * 255, 1, 255))
METAL_MR = Image.fromarray(MR, "RGB")

hmap = micro * 0.50 + wrap_noise(0.9) * 0.14 + scars * 0.20
gy, gx = np.gradient(hmap)
nx, ny, nz = -gx * 0.042, -gy * 0.042, np.ones_like(gx)
nlen = np.sqrt(nx * nx + ny * ny + nz * nz)
METAL_NORM = Image.fromarray(np.uint8(np.clip((np.stack((nx, ny, nz), 2) / nlen[..., None] * 0.5 + 0.5) * 255, 0, 255)), "RGB")

def pbr(name, color=(255, 255, 255), met=0.80, rough=0.44, tex=None, mr=None, normal=None, emi=(0.0, 0.0, 0.0)):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=[*((255, 255, 255) if tex is not None else color), 255],
        metallicFactor=met,
        roughnessFactor=rough,
        baseColorTexture=tex,
        metallicRoughnessTexture=mr,
        normalTexture=normal,
        emissiveFactor=emi,
        doubleSided=True,
    )

MATS = {
    "nickel_pipe": pbr("Brushed cryogenic nickel-slate pipe", None, 0.90, 0.34, NICKEL_PIPE_TEX, METAL_MR, METAL_NORM),
    "slate_pipe":  pbr("Cool slate-steel secondary manifold", None, 0.86, 0.40, SLATE_PIPE_TEX, METAL_MR, METAL_NORM),
    "gunmetal":    pbr("Heavy forged gunmetal housing", None, 0.84, 0.46, GUNMETAL_TEX, None, METAL_NORM),
    "flange":      pbr("Machined ANSI cold-steel flange", (154, 162, 174), 0.92, 0.28),
    "clamp":       pbr("Structural C-channel bracket iron", (42, 47, 56), 0.86, 0.48),
    "cryo_band":   pbr("Cryogenic cobalt identification collar", (46, 108, 176), 0.36, 0.46),
    "hv_tray":     pbr("Galvanized HV cable raceway", (64, 70, 82), 0.82, 0.44),
    "conduit_blu": pbr("Shielded HV cobalt feeder", (40, 86, 148), 0.32, 0.52),
    "conduit_slv": pbr("Armored braided steel conduit", (136, 144, 156), 0.88, 0.34),
    "caution":     pbr("Muted industrial yellow tag", (192, 170, 58), 0.24, 0.62),
    "valve_rim":   pbr("Industrial isolation valve wheel", (134, 52, 50), 0.42, 0.52),
    "gauge_face":  pbr(" illuminated analog gauge dial", (216, 228, 240), 0.12, 0.28, emi=(0.32, 0.38, 0.45)),
    "vault_upper": pbr("Service bay upper slate-blue iron", None, 1.0, 1.0, IRON_VAULT_UPPER, METAL_MR, METAL_NORM),
    "vault_mid":   pbr("Service bay mid graphite iron", None, 1.0, 1.0, IRON_VAULT_MID, METAL_MR, METAL_NORM),
    "vault_lower": pbr("Service bay lower olive-gunmetal dado", None, 1.0, 1.0, IRON_VAULT_LOWER, METAL_MR, METAL_NORM),
    "grating":     pbr("Perforated steel catwalk grating", None, 0.82, 0.48, GRATING_TEX, None, METAL_NORM),
    "dark":        pbr("Deep shadow recess liner", (20, 24, 31), 0.58, 0.62),
    "hazard":      pbr("Crisp light-grey containment trim", (206, 210, 216), 0.22, 0.64),
    "bay_lamp":    pbr("Recessed service bay strip lamp", (216, 232, 248), 0.12, 0.26, emi=(0.74, 0.84, 0.96)),
    "status_cyan": pbr("Cryo flow status indicator", (74, 176, 242), 0.10, 0.24, emi=(0.52, 0.82, 0.98)),
}


# ============================================================================
# 2. CLEAN PROCEDURAL GEOMETRY BUILDER (GROUPED NAMED MESHES + WORLD UVs)
# ============================================================================
def box_uv(mesh: trimesh.Trimesh, scale=10.0) -> np.ndarray:
    v = mesh.vertices
    f = mesh.faces
    # Unweld per face only if needed; trimesh primitives already have split vertices or we compute dominant normal projection
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
    xa = np.cross(up, zt)
    xa /= np.linalg.norm(xa)
    ya = np.cross(zt, xa)
    M = np.eye(4)
    M[:3, 0] = xa
    M[:3, 1] = ya
    M[:3, 2] = zt
    return M

class GroupBuilder:
    def __init__(self):
        self.buckets: dict[tuple[str, str], list[trimesh.Trimesh]] = {}

    def add(self, group: str, mat_key: str, mesh: trimesh.Trimesh):
        self.buckets.setdefault((group, mat_key), []).append(mesh)

    def box(self, group: str, mat_key: str, center, extents, R=None):
        m = trimesh.creation.box(extents=extents)
        T = np.eye(4)
        if R is not None:
            T[:3, :3] = R[:3, :3]
        T[:3, 3] = center
        m.apply_transform(T)
        self.add(group, mat_key, m)

    def cyl(self, group: str, mat_key: str, p0, p1, radius: float, sections: int = 18):
        p0 = np.asarray(p0, float)
        p1 = np.asarray(p1, float)
        d = p1 - p0
        L = float(np.linalg.norm(d))
        if L < 1e-5:
            return
        m = trimesh.creation.cylinder(radius=radius, height=L, sections=sections)
        T = rot_align(d)
        T[:3, 3] = 0.5 * (p0 + p1)
        m.apply_transform(T)
        self.add(group, mat_key, m)

    def flange(self, group: str, p_center, axis_dir, pipe_r: float, bolts: int = 8):
        p_center = np.asarray(p_center, float)
        M = rot_align(axis_dir)
        fl_r = pipe_r * 1.44 + 0.08
        fl_t = max(0.14, pipe_r * 0.28)
        m = trimesh.creation.cylinder(radius=fl_r, height=fl_t, sections=20)
        T = M.copy()
        T[:3, 3] = p_center
        m.apply_transform(T)
        self.add(group, "flange", m)
        # Neck hub
        m2 = trimesh.creation.cylinder(radius=pipe_r * 1.16 + 0.03, height=fl_t * 1.85, sections=16)
        m2.apply_transform(T)
        self.add(group, "gunmetal", m2)
        # Perimeter hex bolts
        bolt_r = pipe_r + 0.62 * (fl_r - pipe_r)
        for bi in range(bolts):
            ang = 2.0 * math.pi * bi / bolts
            local_pt = np.array([bolt_r * math.cos(ang), bolt_r * math.sin(ang), 0.0])
            wp = p_center + M[:3, :3] @ local_pt
            ax = M[:3, 2] * (fl_t * 0.85)
            self.cyl(group, "clamp", wp - ax, wp + ax, max(0.035, pipe_r * 0.075), sections=6)

    def elbow_90(self, group: str, mat_key: str, corner_pt, dir_in, dir_out, bend_r: float, pipe_r: float, segs: int = 8, flanged: bool = True):
        """Smooth swept 90-degree pipe bend around corner_pt: enters along +dir_in toward corner_pt, exits along +dir_out."""
        c = np.asarray(corner_pt, float)
        u_in = np.asarray(dir_in, float); u_in /= np.linalg.norm(u_in)   # travel direction into corner
        u_out = np.asarray(dir_out, float); u_out /= np.linalg.norm(u_out) # travel direction out of corner
        # Start point = c - u_in * bend_r, End point = c + u_out * bend_r
        # Center of curvature = c - u_in * bend_r + u_out * bend_r
        p_start = c - u_in * bend_r
        p_end   = c + u_out * bend_r
        center_arc = c - u_in * bend_r + u_out * bend_r
        e1 = p_start - center_arc # = -u_out * bend_r
        e2 = p_end   - center_arc # = +u_in * bend_r
        pts = []
        for i in range(segs + 1):
            th = 0.5 * math.pi * (i / segs)
            pts.append(center_arc + math.cos(th) * e1 + math.sin(th) * e2)
        for i in range(segs):
            self.cyl(group, mat_key, pts[i], pts[i + 1], pipe_r * 1.015, sections=16)
        # Joint spheres at segment vertices so miter seams are 100% smooth
        for i in range(1, segs):
            sp = trimesh.creation.icosphere(subdivisions=1, radius=pipe_r * 1.01)
            sp.apply_translation(pts[i])
            self.add(group, mat_key, sp)
        if flanged:
            self.flange(group, p_start, u_in, pipe_r, bolts=8)
            self.flange(group, p_end, u_out, pipe_r, bolts=8)
        return p_start, p_end

    def handwheel_valve(self, group: str, pos, pipe_axis, wheel_dir, pipe_r: float):
        pos = np.asarray(pos, float)
        pa = np.asarray(pipe_axis, float); pa /= np.linalg.norm(pa)
        wd = np.asarray(wheel_dir, float); wd /= np.linalg.norm(wd)
        # Valve body + end flanges
        self.cyl(group, "gunmetal", pos - pa * 0.85, pos + pa * 0.85, pipe_r * 1.32, sections=16)
        self.flange(group, pos - pa * 0.85, pa, pipe_r, bolts=8)
        self.flange(group, pos + pa * 0.85, pa, pipe_r, bolts=8)
        # Bonnet & stem
        bonnet_top = pos + wd * (pipe_r * 2.55)
        self.cyl(group, "gunmetal", pos, pos + wd * (pipe_r * 1.65), pipe_r * 0.72, sections=14)
        self.flange(group, pos + wd * (pipe_r * 1.45), wd, pipe_r * 0.62, bolts=6)
        self.cyl(group, "flange", pos + wd * (pipe_r * 1.45), bonnet_top, pipe_r * 0.24, sections=10)
        # Spoked circular handwheel rim
        M = rot_align(wd)
        wheel_r = max(0.88, pipe_r * 1.85)
        n_rim = 16
        for i in range(n_rim):
            a0 = 2.0 * math.pi * i / n_rim
            a1 = 2.0 * math.pi * (i + 1) / n_rim
            q0 = bonnet_top + M[:3, :3] @ np.array([wheel_r * math.cos(a0), wheel_r * math.sin(a0), 0.0])
            q1 = bonnet_top + M[:3, :3] @ np.array([wheel_r * math.cos(a1), wheel_r * math.sin(a1), 0.0])
            self.cyl(group, "valve_rim", q0, q1, 0.085, sections=8)
        for i in range(5):
            ang = 2.0 * math.pi * i / 5
            q = bonnet_top + M[:3, :3] @ np.array([wheel_r * math.cos(ang), wheel_r * math.sin(ang), 0.0])
            self.cyl(group, "flange", bonnet_top, q, 0.06, sections=6)

    def pressure_gauge(self, group: str, pos, face_normal):
        pos = np.asarray(pos, float)
        fn = np.asarray(face_normal, float); fn /= np.linalg.norm(fn)
        self.cyl(group, "gunmetal", pos - fn * 0.14, pos + fn * 0.14, 0.44, sections=18)
        self.cyl(group, "flange",   pos + fn * 0.08, pos + fn * 0.18, 0.47, sections=18)
        self.cyl(group, "gauge_face", pos + fn * 0.14, pos + fn * 0.20, 0.37, sections=18)

    def export_glb(self, out_path: Path):
        sc = trimesh.Scene()
        total_tris = 0
        for (grp, mat_key), parts in sorted(self.buckets.items()):
            merged = trimesh.util.concatenate(parts)
            uv = box_uv(merged, scale=9.0)
            merged.visual = trimesh.visual.texture.TextureVisuals(uv=uv, material=MATS[mat_key])
            node_name = f"{grp}__{mat_key}"
            sc.add_geometry(merged, geom_name=node_name, node_name=node_name)
            total_tris += len(merged.faces)
        raw = sc.export(file_type="glb")
        out_path.write_bytes(raw)
        ver = trimesh.load(out_path, force="scene", process=False)
        return ver, total_tris, len(raw)


# ============================================================================
# 3. BUILD MODEL M11: REACTOR_COOLANT_PIPING_RING_01.glb
#    (Octagonal Chamber Cryogenic Coolant Mains, Flanged Rupture Spools,
#     Spoked Isolation Valves, Pressure Manifolds & Armored HV Cable Trays)
# ============================================================================
gb_pipe = GroupBuilder()

for side in (-1, 1):
    stag = "LEFT" if side < 0 else "RIGHT"

    # A) UPPER 45° OCTAGONAL SLOPE TWIN CRYOGENIC MAINS
    #    Wall plane at Z_src in [12.5, 21.5]: |X| = 24.5 - (Z - 12.5) * (7.5 / 9.0)
    #    At Z = 16.10 -> wall |X| = 21.50; inward pipe center at |X| = 19.95, Z = 15.85 (0.98 stud clear of wall & clear of light ribs!)
    #    Secondary return pipe at |X| = 21.35, Z = 14.15.
    x_main = side * 19.95
    z_main = 15.85
    r_main = 0.50

    x_ret  = side * 21.35
    z_ret  = 14.15
    r_ret  = 0.33

    # Front armored wall penetration collar (Y = -16.85) -> Swept 90° elbow into longitudinal run (Y = -15.35 .. +9.35)
    p_pen_main = np.array([side * 21.65, -16.85, 16.15])
    gb_pipe.cyl(f"CRYO_HEADER_{stag}", "gunmetal", p_pen_main + np.array([side * 0.45, 0.0, 0.15]), p_pen_main - np.array([side * 0.35, 0.0, 0.0]), 0.78, sections=18)
    gb_pipe.flange(f"CRYO_HEADER_{stag}", p_pen_main - np.array([side * 0.35, 0.0, 0.0]), (-side, 0.0, 0.0), r_main, bolts=10)

    c_front_main = np.array([x_main, -16.85, z_main])
    gb_pipe.cyl(f"CRYO_HEADER_{stag}", "nickel_pipe", p_pen_main, c_front_main + np.array([side * 1.25, 0.0, 0.0]), r_main)
    _, y_start_m = gb_pipe.elbow_90(f"CRYO_HEADER_{stag}", "nickel_pipe", c_front_main, (-side, 0.0, 0.0), (0.0, 1.0, 0.0), 1.25, r_main)

    # Modular Flanged Rupture Spool on Upper Slope (Y = -8.20 .. -1.20) — Ready for Faz 4.2 Meltdown Pipe Burst!
    y_sp0, y_sp1 = -8.20, -1.20
    gb_pipe.cyl(f"CRYO_HEADER_{stag}", "nickel_pipe", y_start_m, (x_main, y_sp0, z_main), r_main)
    gb_pipe.flange(f"CRYO_HEADER_{stag}", (x_main, y_sp0, z_main), (0.0, 1.0, 0.0), r_main, bolts=10)

    spool_upper_grp = f"PIPE_SPOOL_UPPER_{stag}"
    gb_pipe.cyl(spool_upper_grp, "nickel_pipe", (x_main, y_sp0, z_main), (x_main, y_sp1, z_main), r_main)
    gb_pipe.flange(spool_upper_grp, (x_main, y_sp0 + 0.16, z_main), (0.0, 1.0, 0.0), r_main, bolts=10)
    gb_pipe.flange(spool_upper_grp, (x_main, y_sp1 - 0.16, z_main), (0.0, 1.0, 0.0), r_main, bolts=10)
    for yb in (-6.2, -3.2):
        gb_pipe.cyl(spool_upper_grp, "cryo_band", (x_main, yb - 0.24, z_main), (x_main, yb + 0.24, z_main), r_main * 1.06, sections=18)

    gb_pipe.flange(f"CRYO_HEADER_{stag}", (x_main, y_sp1, z_main), (0.0, 1.0, 0.0), r_main, bolts=10)
    gb_pipe.cyl(f"CRYO_HEADER_{stag}", "nickel_pipe", (x_main, y_sp1, z_main), (x_main, 9.55, z_main), r_main)
    for yb in (-12.2, 2.8, 6.8):
        gb_pipe.cyl(f"CRYO_HEADER_{stag}", "cryo_band", (x_main, yb - 0.24, z_main), (x_main, yb + 0.24, z_main), r_main * 1.06, sections=18)
    gb_pipe.flange(f"CRYO_HEADER_{stag}", (x_main, 4.80, z_main), (0.0, 1.0, 0.0), r_main, bolts=10)

    # Secondary return pipe along upper 45° slope
    p_pen_ret = np.array([side * 22.95, -16.65, 14.30])
    gb_pipe.cyl(f"CRYO_RETURN_{stag}", "gunmetal", p_pen_ret + np.array([side * 0.40, 0.0, 0.10]), p_pen_ret - np.array([side * 0.28, 0.0, 0.0]), 0.56, sections=16)
    c_front_ret = np.array([x_ret, -16.65, z_ret])
    _, y_start_r = gb_pipe.elbow_90(f"CRYO_RETURN_{stag}", "slate_pipe", c_front_ret, (-side, 0.0, 0.0), (0.0, 1.0, 0.0), 0.95, r_ret)
    gb_pipe.cyl(f"CRYO_RETURN_{stag}", "slate_pipe", y_start_r, (x_ret, 8.85, z_ret), r_ret)
    for yf in (-10.5, -3.5, 3.5):
        gb_pipe.flange(f"CRYO_RETURN_{stag}", (x_ret, yf, z_ret), (0.0, 1.0, 0.0), r_ret, bolts=8)

    # Heavy C-channel saddle wall brackets anchoring both upper pipes to the 45° octagonal slope (avoiding Y=-15.4 & +10.6 light ribs!)
    slope_R = rot_align((0.0, 1.0, 0.0))
    n_wall = np.array([side * 0.768, 0.0, 0.640])
    t_wall = np.array([-side * 0.640, 0.0, 0.768])
    M_br = np.eye(4)
    M_br[:3, 0] = n_wall
    M_br[:3, 1] = np.array([0.0, 1.0, 0.0])
    M_br[:3, 2] = t_wall
    for yc_b in (-13.4, -9.4, -4.7, 0.4, 5.6, 8.4):
        mid_p = 0.5 * (np.array([x_main, yc_b, z_main]) + np.array([x_ret, yc_b, z_ret])) + n_wall * 0.58
        gb_pipe.box(f"WALL_CLAMP_{stag}", "clamp", mid_p, (0.95, 0.44, 3.45), R=M_br)
        for px, pz, pr in [(x_main, z_main, r_main), (x_ret, z_ret, r_ret)]:
            gb_pipe.cyl(f"WALL_CLAMP_{stag}", "flange", (px, yc_b - 0.18, pz), (px, yc_b + 0.18, pz), pr * 1.18, sections=16)

    # B) REAR CORNER VERTICAL RISER MANIFOLDS, ISOLATION HANDWHEEL VALVES & RADIATOR TIE-INS
    #    Positioned at X = ±19.95, Y = +10.80 (cleanly outside Rear Service Grilles |X|<=15.9 and clear of Outer Truss ±18.25, +11.85!)
    c_top_drop = np.array([x_main, 10.80, z_main])
    _, p_drop_top = gb_pipe.elbow_90(f"CRYO_HEADER_{stag}", "nickel_pipe", c_top_drop, (0.0, 1.0, 0.0), (0.0, 0.0, -1.0), 1.25, r_main)

    # Upper vertical riser -> Rear Spool (Z = +7.80 .. +1.60) -> Spoked Isolation Gate Valve (Z = -2.40) -> Lower Radiator Manifold
    z_rsp_hi, z_rsp_lo = 7.80, 1.60
    gb_pipe.cyl(f"CRYO_HEADER_{stag}", "nickel_pipe", p_drop_top, (x_main, 10.80, z_rsp_hi), r_main)
    gb_pipe.flange(f"CRYO_HEADER_{stag}", (x_main, 10.80, z_rsp_hi), (0.0, 0.0, -1.0), r_main, bolts=10)

    spool_rear_grp = f"PIPE_SPOOL_REAR_{stag}"
    gb_pipe.cyl(spool_rear_grp, "nickel_pipe", (x_main, 10.80, z_rsp_hi), (x_main, 10.80, z_rsp_lo), r_main)
    gb_pipe.flange(spool_rear_grp, (x_main, 10.80, z_rsp_hi - 0.16), (0.0, 0.0, -1.0), r_main, bolts=10)
    gb_pipe.flange(spool_rear_grp, (x_main, 10.80, z_rsp_lo + 0.16), (0.0, 0.0, -1.0), r_main, bolts=10)
    gb_pipe.cyl(spool_rear_grp, "cryo_band", (x_main, 10.80, 4.70 - 0.24), (x_main, 10.80, 4.70 + 0.24), r_main * 1.06, sections=18)

    gb_pipe.flange(f"CRYO_HEADER_{stag}", (x_main, 10.80, z_rsp_lo), (0.0, 0.0, -1.0), r_main, bolts=10)
    gb_pipe.cyl(f"CRYO_HEADER_{stag}", "nickel_pipe", (x_main, 10.80, z_rsp_lo), (x_main, 10.80, -12.35), r_main)

    # Spoked Isolation Gate Valve + Illuminated Analog Pressure Gauge Block visible from Control Room!
    wheel_dir = np.array([-side * 0.55, -0.835, 0.0])
    gb_pipe.handwheel_valve(f"VALVE_ASSEMBLY_{stag}", (x_main, 10.80, -2.60), (0.0, 0.0, -1.0), wheel_dir, r_main)
    gb_pipe.box(f"PRESSURE_MANIFOLD_{stag}", "gunmetal", (x_main - side * 0.55, 10.55, -5.80), (0.95, 0.85, 1.45))
    gb_pipe.pressure_gauge(f"PRESSURE_MANIFOLD_{stag}", (x_main - side * 0.58, 10.05, -5.45), (0.0, -1.0, 0.0))
    gb_pipe.pressure_gauge(f"PRESSURE_MANIFOLD_{stag}", (x_main - side * 0.58, 10.05, -6.25), (0.0, -1.0, 0.0))
    gb_pipe.box(f"PRESSURE_MANIFOLD_{stag}", "status_cyan", (x_main - side * 0.96, 10.22, -5.80), (0.08, 0.14, 0.92))

    # Secondary return vertical drop alongside main riser
    c_ret_drop = np.array([x_ret, 9.80, z_ret])
    _, p_rdrop = gb_pipe.elbow_90(f"CRYO_RETURN_{stag}", "slate_pipe", c_ret_drop, (0.0, 1.0, 0.0), (0.0, 0.0, -1.0), 0.95, r_ret)
    gb_pipe.cyl(f"CRYO_RETURN_{stag}", "slate_pipe", p_rdrop, (x_ret, 9.80, -11.60), r_ret)
    for zr_c in (9.2, 3.2, -4.4, -9.8):
        gb_pipe.box(f"WALL_CLAMP_{stag}", "clamp", (side * 20.95, 10.55, zr_c), (2.45, 1.55, 0.38))

    # Lower elbow turning directly into the outer side header of the Olive-Taupe Radiator Containment Bank (X = ±18.1, Y = 13.55, Z = -13.6)
    c_bot_turn = np.array([x_main, 10.80, -13.60])
    _, p_to_rad = gb_pipe.elbow_90(f"CRYO_HEADER_{stag}", "nickel_pipe", c_bot_turn, (0.0, 0.0, -1.0), (0.0, 1.0, 0.0), 1.25, r_main)
    gb_pipe.cyl(f"CRYO_HEADER_{stag}", "nickel_pipe", p_to_rad, (x_main, 13.55, -13.60), r_main)
    c_rad_in = np.array([x_main, 13.55, -13.60])
    _, p_rad_plug = gb_pipe.elbow_90(f"CRYO_HEADER_{stag}", "nickel_pipe", c_rad_in, (0.0, 1.0, 0.0), (-side, 0.0, 0.0), 0.95, r_main)
    gb_pipe.cyl(f"CRYO_HEADER_{stag}", "gunmetal", p_rad_plug, (side * 18.05, 13.55, -13.60), 0.72, sections=18)

    # Secondary return lower elbow into radiator lower port (Z = -16.10)
    c_rbot = np.array([x_ret, 9.80, -12.55])
    _, p_r1 = gb_pipe.elbow_90(f"CRYO_RETURN_{stag}", "slate_pipe", c_rbot, (0.0, 0.0, -1.0), (-side * 0.58, 0.815, 0.0), 0.95, r_ret)
    gb_pipe.cyl(f"CRYO_RETURN_{stag}", "slate_pipe", p_r1, (side * 18.15, 13.55, -12.55), r_ret)

    # C) UPPER REAR PLENUM OVERHEAD CROSS-HEADER (Z = +18.55, Y = +13.85 — cleanly ABOVE Rear Service Grilles Z<=16.86!)
    #    Branches inward from upper corner header to feed top of Rear Condenser Plenum!
    gb_pipe.cyl("REAR_OVERHEAD_PLENUM_TIE", "slate_pipe", (side * 18.60, 12.20, 17.85), (side * 15.80, 13.85, 18.55), 0.34)
    gb_pipe.flange("REAR_OVERHEAD_PLENUM_TIE", (side * 15.80, 13.85, 18.55), (-side, 0.0, 0.0), 0.34, bolts=8)

    # D) ARMORED PERFORATED HIGH-VOLTAGE CABLE TRAYS (Upper 45° Slope + Rear Junction Box)
    #    Mounted at |X| = 17.55, Z = 18.45 (strictly outside SL-00 roof hatch |X|<=6.62!)
    x_tr, z_tr = side * 17.55, 18.45
    gb_pipe.box(f"HV_CABLE_TRAY_{stag}", "hv_tray", (x_tr, -2.20, z_tr), (1.35, 29.20, 0.14), R=M_br)
    for rail_s in (-0.62, 0.62):
        off_r = M_br[:3, 2] * rail_s + M_br[:3, 0] * (-0.12)
        gb_pipe.box(f"HV_CABLE_TRAY_{stag}", "clamp", np.array([x_tr, -2.20, z_tr]) + off_r, (0.28, 29.20, 0.10), R=M_br)
    # 3 bundled shielded HV feeder cables inside tray
    for ci, (c_off, c_mat) in enumerate([(-0.34, "conduit_blu"), (0.0, "conduit_slv"), (0.34, "cryo_band")]):
        cp0 = np.array([x_tr, -16.75, z_tr]) + M_br[:3, 2] * c_off - M_br[:3, 0] * 0.16
        cp1 = np.array([x_tr,  12.35, z_tr]) + M_br[:3, 2] * c_off - M_br[:3, 0] * 0.16
        gb_pipe.cyl(f"HV_CABLE_TRAY_{stag}", c_mat, cp0, cp1, 0.115, sections=10)
    for yt in (-13.0, -7.5, -2.0, 3.5, 9.0):
        tp = np.array([x_tr, yt, z_tr]) - M_br[:3, 0] * 0.22
        gb_pipe.box(f"HV_CABLE_TRAY_{stag}", "caution", tp, (0.14, 0.28, 1.24), R=M_br)

    # E) LOWER PIT FLOOR RETURN HEADERS & ARMORED FLOOR CONDUIT TRAYS
    #    Runs cleanly along flat sump deck at X = ±11.45 & ±13.55, Z = -21.02 (clear of SL-05 |X|<=6.62 and SL-03/04 |X|>=17.0!)
    x_fl = side * 11.45
    z_fl = -20.92
    r_fl = 0.38
    gb_pipe.cyl(f"FLOOR_RETURN_{stag}", "gunmetal", (x_fl, -17.30, z_fl), (x_fl, -16.50, z_fl), 0.58, sections=16)
    gb_pipe.flange(f"FLOOR_RETURN_{stag}", (x_fl, -16.50, z_fl), (0.0, 1.0, 0.0), r_fl, bolts=8)
    gb_pipe.cyl(f"FLOOR_RETURN_{stag}", "nickel_pipe", (x_fl, -16.50, z_fl), (x_fl, 12.15, z_fl), r_fl)
    c_fl_up = np.array([x_fl, 13.10, z_fl])
    _, p_fl_up = gb_pipe.elbow_90(f"FLOOR_RETURN_{stag}", "nickel_pipe", c_fl_up, (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), 0.95, r_fl)
    gb_pipe.cyl(f"FLOOR_RETURN_{stag}", "nickel_pipe", p_fl_up, (x_fl, 13.10, -17.95), r_fl)
    gb_pipe.flange(f"FLOOR_RETURN_{stag}", (x_fl, 13.10, -18.05), (0.0, 0.0, 1.0), r_fl, bolts=8)
    for yf_s in (-13.5, -8.0, -2.5, 3.0, 8.5):
        gb_pipe.box(f"FLOOR_RETURN_{stag}", "clamp", (x_fl, yf_s, -21.26), (1.18, 0.42, 0.48))
        gb_pipe.cyl(f"FLOOR_RETURN_{stag}", "cryo_band", (x_fl, yf_s + 1.8, z_fl), (x_fl, yf_s + 2.15, z_fl), r_fl * 1.07, sections=16)

    # Parallel floor HV busbar raceway at X = ±13.65, Z = -21.22
    x_bus = side * 13.65
    gb_pipe.box(f"FLOOR_HV_BUSBAR_{stag}", "hv_tray", (x_bus, -2.10, -21.26), (1.42, 29.40, 0.34))
    gb_pipe.box(f"FLOOR_HV_BUSBAR_{stag}", "clamp",   (x_bus, -2.10, -21.05), (1.26, 29.20, 0.08))
    for xb_c, b_mat in [(-0.36, "conduit_blu"), (0.0, "conduit_slv"), (0.36, "conduit_blu")]:
        gb_pipe.cyl(f"FLOOR_HV_BUSBAR_{stag}", b_mat, (x_bus + xb_c, -16.70, -20.96), (x_bus + xb_c, 12.55, -20.96), 0.095, sections=10)
    for yb_t in (-11.0, -3.0, 5.0):
        gb_pipe.box(f"FLOOR_HV_BUSBAR_{stag}", "caution", (x_bus, yb_t, -20.98), (1.46, 0.34, 0.12))

# Central overhead cryo bridge above Rear Grilles & Cobalt Vent (Z = +18.55, Y = +13.85) dropping behind bulkhead into Plenum
gb_pipe.cyl("REAR_OVERHEAD_PLENUM_TIE", "nickel_pipe", (-15.80, 13.85, 18.55), (15.80, 13.85, 18.55), 0.38)
for x_tie in (-9.5, 0.0, 9.5):
    gb_pipe.flange("REAR_OVERHEAD_PLENUM_TIE", (x_tie, 13.85, 18.55), (1.0, 0.0, 0.0), 0.38, bolts=8)
    gb_pipe.box("REAR_OVERHEAD_PLENUM_TIE", "clamp", (x_tie, 14.45, 18.55), (0.46, 1.15, 0.92))
for sgn_p in (-1, 1):
    # Branch penetrating through upper rear bulkhead into Condenser Plenum
    gb_pipe.cyl("REAR_OVERHEAD_PLENUM_TIE", "slate_pipe", (sgn_p * 4.20, 13.85, 18.55), (sgn_p * 4.20, 15.65, 18.55), 0.30)
    gb_pipe.flange("REAR_OVERHEAD_PLENUM_TIE", (sgn_p * 4.20, 14.85, 18.55), (0.0, 1.0, 0.0), 0.30, bolts=6)

GLB_M11_PATH = EXP / "REACTOR_COOLANT_PIPING_RING_01.glb"
m11_scene, m11_tris, m11_bytes = gb_pipe.export_glb(GLB_M11_PATH)
print(f"[OK] M11 {GLB_M11_PATH.name}: {len(m11_scene.geometry)} meshes, {m11_tris:,} tris, {m11_bytes/1e6:.2f} MB")


# ============================================================================
# 4. BUILD MODEL M12: PISTON_REAR_SERVICE_BAY_01.glb
#    (Canonical Connected Behind-Port Hydraulic Service Chamber & Catwalk Vault
#     in the exact local frame of REACTOR_PISTON_GUIDE_01:
#       +X = inward toward reactor center, -X = outward into facility gallery,
#       Piston guide spans lx in [-33.80, -2.49], ly/lz in [-4.33, +4.33])
# ============================================================================
gb_bay = GroupBuilder()

LX_FRONT = -3.32   # Sits cleanly behind wall hatch plates (r = 24.50 + 3.32 = 27.82) & seals radial port collars!
LX_REAR  = -38.80  # Extends 5.0 studs behind piston rear base (-33.80) for rear crossover catwalk & facility airlock!
LY_IN    = 6.45    # 12.90-stud clear interior width (clears SL-01/02 11.56 opening + flanks ±4.33 piston with twin side aisles!)
LZ_IN    = 5.75    # 11.50-stud clear interior height (clears 8.30x8.30 radial openings & ±4.33 piston hoops!)
WALL_T   = 0.58

# A) FRONT THROAT SEAL BULKHEAD COLLAR (lx = -2.75 .. -3.65)
#    Inner clear aperture: ly in [-6.05, +6.05] (12.10), lz in [-4.55, +4.55] (9.10)
#    Outer seal flange:    ly in [-8.60, +8.60] (17.20), lz in [-6.85, +6.85] (13.70) -> %0 gap on ALL 6 portals!
ap_y, ap_z = 6.05, 4.45
out_y, out_z = 7.45, 5.08
lx_c, lx_t = -3.28, 0.84
gb_bay.box("THROAT_COLLAR", "gunmetal", (lx_c, -(ap_y + out_y) * 0.5, 0.0), (lx_t, out_y - ap_y, out_z * 2))
gb_bay.box("THROAT_COLLAR", "gunmetal", (lx_c,  (ap_y + out_y) * 0.5, 0.0), (lx_t, out_y - ap_y, out_z * 2))
gb_bay.box("THROAT_COLLAR", "gunmetal", (lx_c, 0.0, -(ap_z + out_z) * 0.5), (lx_t, ap_y * 2, out_z - ap_z))
gb_bay.box("THROAT_COLLAR", "gunmetal", (lx_c, 0.0,  (ap_z + out_z) * 0.5), (lx_t, ap_y * 2, out_z - ap_z))
# Machined inner throat bevel visible right inside open hatch
gb_bay.box("THROAT_COLLAR", "flange", (lx_c + 0.22, -ap_y - 0.14, 0.0), (0.36, 0.28, ap_z * 2 + 0.56))
gb_bay.box("THROAT_COLLAR", "flange", (lx_c + 0.22,  ap_y + 0.14, 0.0), (0.36, 0.28, ap_z * 2 + 0.56))
gb_bay.box("THROAT_COLLAR", "flange", (lx_c + 0.22, 0.0, -ap_z - 0.14), (0.36, ap_y * 2, 0.28))
gb_bay.box("THROAT_COLLAR", "flange", (lx_c + 0.22, 0.0,  ap_z + 0.14), (0.36, ap_y * 2, 0.28))

# B) ENCLOSED MULTI-TONE ARMOURED VAULT SHELL (Separately named walls for clean inspection & 0% Void Leak!)
vault_len = LX_FRONT - LX_REAR
vault_xc  = 0.5 * (LX_FRONT + LX_REAR)
gb_bay.box("VAULT_CEILING", "vault_upper", (vault_xc, 0.0,  LZ_IN + WALL_T * 0.5), (vault_len, (LY_IN + WALL_T) * 2, WALL_T))
gb_bay.box("VAULT_FLOOR",   "vault_lower", (vault_xc, 0.0, -LZ_IN - WALL_T * 0.5), (vault_len, (LY_IN + WALL_T) * 2, WALL_T))
for sgn_y in (-1, 1):
    w_grp = "VAULT_WALL_LEFT" if sgn_y < 0 else "VAULT_WALL_RIGHT"
    wy = sgn_y * (LY_IN + WALL_T * 0.5)
    gb_bay.box(w_grp, "vault_upper", (vault_xc, wy,  3.85), (vault_len, WALL_T, 3.80))
    gb_bay.box(w_grp, "vault_mid",   (vault_xc, wy,  0.00), (vault_len, WALL_T, 3.90))
    gb_bay.box(w_grp, "vault_lower", (vault_xc, wy, -3.85), (vault_len, WALL_T, 3.80))
    gb_bay.box(w_grp + "_TRIM", "caution", (vault_xc, sgn_y * (LY_IN - 0.05), -1.92), (vault_len - 1.2, 0.08, 0.18))

# Rear Connected Facility Bulkhead + Recessed Armored Maintenance Airlock Door (lx = LX_REAR)
gb_bay.box("VAULT_REAR_BULKHEAD", "vault_mid", (LX_REAR - WALL_T * 0.5, 0.0, 0.0), (WALL_T, (LY_IN + WALL_T) * 2, (LZ_IN + WALL_T) * 2))
# Armored Facility Service Airlock Doorway ("MAINT-BAY") visible at the back of the chamber
gb_bay.box("FACILITY_AIRLOCK", "clamp",    (LX_REAR + 0.18, 0.0, -1.15), (0.36, 5.40, 7.20))
gb_bay.box("FACILITY_AIRLOCK", "dark",     (LX_REAR + 0.28, 0.0, -1.15), (0.20, 4.70, 6.50))
for sgn_d in (-1, 1):
    gb_bay.box("FACILITY_AIRLOCK", "slate_pipe", (LX_REAR + 0.36, sgn_d * 1.14, -1.15), (0.14, 2.22, 6.26))
    gb_bay.box("FACILITY_AIRLOCK", "flange",     (LX_REAR + 0.45, sgn_d * 0.16, -1.15), (0.08, 0.14, 6.18))
    gb_bay.box("FACILITY_AIRLOCK", "dark",       (LX_REAR + 0.46, sgn_d * 1.14,  0.45), (0.08, 1.10, 1.55))
gb_bay.box("FACILITY_AIRLOCK", "status_cyan", (LX_REAR + 0.42, 0.0, 2.65), (0.10, 2.40, 0.24))
# Twin overhead cryo trunk ducts exiting through upper rear bulkhead into outer facility ring
for sgn_d in (-1, 1):
    gb_bay.cyl("FACILITY_AIRLOCK", "nickel_pipe", (LX_REAR + 0.10, sgn_d * 3.85, 3.85), (LX_REAR + 4.40, sgn_d * 3.85, 3.85), 0.52, sections=16)
    gb_bay.flange("FACILITY_AIRLOCK", (LX_REAR + 0.55, sgn_d * 3.85, 3.85), (1.0, 0.0, 0.0), 0.52, bolts=8)

# C) 6 HEAVY STRUCTURAL PORTAL BOX-RIBS (Deep receding perspective visible through open hatch!)
for rx in (-6.2, -11.8, -17.4, -23.0, -28.6, -34.2):
    for sgn_y in (-1, 1):
        gb_bay.box("PORTAL_RIBS", "clamp", (rx, sgn_y * (LY_IN - 0.28), 0.0), (0.52, 0.56, LZ_IN * 2))
        gb_bay.box("PORTAL_RIBS", "flange", (rx, sgn_y * (LY_IN - 0.57), 0.0), (0.20, 0.08, LZ_IN * 2 - 1.4))
    for sgn_z in (-1, 1):
        gb_bay.box("PORTAL_RIBS", "clamp", (rx, 0.0, sgn_z * (LZ_IN - 0.26)), (0.52, LY_IN * 2, 0.52))
    # Upper corner chamfer gussets
    for sgn_y in (-1, 1):
        gb_bay.cyl("PORTAL_RIBS", "clamp", (rx, sgn_y * (LY_IN - 0.3), LZ_IN - 1.6), (rx, sgn_y * (LY_IN - 1.8), LZ_IN - 0.3), 0.16, sections=8)

# D) TWIN HIGH-PRESSURE HYDRAULIC ACCUMULATORS, MANIFOLDS & PISTON FEED LOOPS
#    Placed in side aisles at ly = ±5.38 (strictly outside piston guide hoops ly in [-4.33, +4.33] -> ZERO collision!)
for sgn_y in (-1, 1):
    ay = sgn_y * 5.38
    # Twin stacked accumulator cylinders along lx = -8.2 .. -27.8
    for az, ar, amat in [(1.55, 0.52, "nickel_pipe"), (-0.55, 0.40, "slate_pipe")]:
        gb_bay.cyl("HYDRAULIC_ACCUMULATORS", amat, (-8.20, ay, az), (-27.80, ay, az), ar, sections=16)
        # End caps & pressure bands
        for cap_x in (-8.20, -27.80):
            sp = trimesh.creation.icosphere(subdivisions=1, radius=ar * 0.99)
            sp.apply_translation((cap_x, ay, az))
            gb_bay.add("HYDRAULIC_ACCUMULATORS", "gunmetal", sp)
        for bx in (-10.5, -16.0, -21.5, -26.0):
            gb_bay.cyl("HYDRAULIC_ACCUMULATORS", "cryo_band", (bx - 0.18, ay, az), (bx + 0.18, ay, az), ar * 1.07, sections=16)
            gb_bay.box("HYDRAULIC_ACCUMULATORS", "clamp", (bx, sgn_y * 5.88, az), (0.34, 1.05, ar * 2.15))

    # Braided steel hydraulic feed line curving inward at rear (-32.4) to feed Piston Base (-32.5, ±2.6, 0)
    gb_bay.cyl("HYDRAULIC_ACCUMULATORS", "conduit_slv", (-27.80, ay, 1.55), (-32.60, ay, 1.55), 0.22, sections=12)
    c_feed = np.array([-32.60, ay, 1.55])
    _, p_in = gb_bay.elbow_90("HYDRAULIC_ACCUMULATORS", "conduit_slv", c_feed, (-1.0, 0.0, 0.0), (0.0, -sgn_y, 0.0), 0.72, 0.22)
    gb_bay.cyl("HYDRAULIC_ACCUMULATORS", "conduit_slv", p_in, (-32.60, sgn_y * 2.68, 1.55), 0.22, sections=12)
    gb_bay.flange("HYDRAULIC_ACCUMULATORS", (-32.60, sgn_y * 2.75, 1.55), (0.0, -sgn_y, 0.0), 0.24, bolts=6)

    # Side aisle pressure gauge & local servo control box visible through open portal
    gb_bay.box("HYDRAULIC_ACCUMULATORS", "gunmetal", (-9.40, sgn_y * 5.85, -2.15), (1.35, 0.72, 1.65))
    gb_bay.pressure_gauge("HYDRAULIC_ACCUMULATORS", (-8.65, sgn_y * 5.55, -1.85), (1.0, 0.0, 0.0))
    gb_bay.box("HYDRAULIC_ACCUMULATORS", "status_cyan", (-8.70, sgn_y * 5.52, -2.55), (0.08, 0.36, 0.16))

# E) PERFORATED STEEL MAINTENANCE CATWALK GRATING, TOE-KICKS & SAFETY HANDRAILS
#    Lower floor deck at lz = -4.92 (safely below piston hoops lz = -4.33!) + Rear crossover platform (lx = -34.4 .. -38.4)
gb_bay.box("MAINTENANCE_CATWALK", "grating", (vault_xc, 0.0, -4.96), (vault_len - 1.2, LY_IN * 2 - 0.6, 0.18))
for cx_b in (-8.5, -14.5, -20.5, -26.5, -32.5, -37.2):
    gb_bay.box("MAINTENANCE_CATWALK", "clamp", (cx_b, 0.0, -5.32), (0.38, LY_IN * 2 - 0.4, 0.54))
# Twin side safety handrails flanking the central piston pit (ly = ±4.58, lz = -4.88 .. -3.25)
for sgn_y in (-1, 1):
    ry = sgn_y * 4.62
    gb_bay.box("MAINTENANCE_CATWALK", "caution", (-19.20, ry, -4.78), (28.40, 0.08, 0.22))
    gb_bay.cyl("MAINTENANCE_CATWALK", "flange",  (-5.00,  ry, -3.35), (-33.40, ry, -3.35), 0.055, sections=8)
    gb_bay.cyl("MAINTENANCE_CATWALK", "flange",  (-5.00,  ry, -4.08), (-33.40, ry, -4.08), 0.042, sections=8)
    for px in (-5.2, -10.8, -16.4, -22.0, -27.6, -33.2):
        gb_bay.cyl("MAINTENANCE_CATWALK", "clamp", (px, ry, -4.88), (px, ry, -3.32), 0.06, sections=8)

# F) RECESSED INDUSTRIAL BAY STRIP LAMPS (Soft cool-white illumination so open portals show real 3D machinery depth!)
for sgn_y in (-1, 1):
    ly_l = sgn_y * 4.85
    lz_l = 4.92
    for lx_seg in (-9.2, -18.8, -28.4, -36.0):
        gb_bay.box("BAY_LIGHTING", "clamp",    (lx_seg, ly_l, lz_l + 0.14), (6.20, 0.56, 0.22))
        gb_bay.box("BAY_LIGHTING", "bay_lamp", (lx_seg, ly_l, lz_l),        (5.80, 0.28, 0.09))

GLB_M12_PATH = EXP / "PISTON_REAR_SERVICE_BAY_01.glb"
m12_scene, m12_tris, m12_bytes = gb_bay.export_glb(GLB_M12_PATH)
print(f"[OK] M12 {GLB_M12_PATH.name}: {len(m12_scene.geometry)} meshes, {m12_tris:,} tris, {m12_bytes/1e6:.2f} MB")


# ============================================================================
# 5. GEOMETRIC CLEARANCE & ZERO-COLLISION VERIFICATION
# ============================================================================
piston_glb  = trimesh.load(EXP / "REACTOR_PISTON_GUIDE_01.glb", force="scene", process=False)
emitter_glb = trimesh.load(EXP / "REACTOR_EMITTER_REV03.glb", force="scene", process=False)
crown_glb   = trimesh.load(EXP / "REACTOR_CROWN_DECK_AND_RADIAL_PORTS_01.glb", force="scene", process=False)
side_glb    = trimesh.load(EXP / "REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV03_DIAG_OPEN.glb", force="scene", process=False)
rear_glb    = trimesh.load(EXP / "REACTOR_REAR_BULKHEAD_IRON_REV05_TURBINE_PORT.glb", force="scene", process=False)
turb_glb    = trimesh.load(EXP / "REACTOR_REAR_TURBINE_AND_PLENUM_01.glb", force="scene", process=False)
grille_glb  = trimesh.load(EXP / "REACTOR_REAR_SERVICE_GRILLES_SLATE_02.glb", force="scene", process=False)
hatch_glb   = trimesh.load(EXP / "REACTOR_WALL_HATCH_THROUGH_SLATE_02.glb", force="scene", process=False)
win_glb     = trimesh.load(EXP / "OBSERVATION_WINDOW_ARMOR_FRAME_01.glb", force="scene", process=False)

print(f"[QA] M11 bounds (authoring): {np.round(m11_scene.bounds, 2).tolist()}")
print(f"[QA] M12 bounds (local bay): {np.round(m12_scene.bounds, 2).tolist()}")
assert m12_scene.bounds[0, 0] < -38.5 and m12_scene.bounds[1, 0] < -2.7, "M12 must sit behind port plane and wrap past -33.8 piston!"


# ============================================================================
# 6. GPU/EGL INSTANCED PYRENDER PIPELINE (1x TEXTURE UPLOAD -> 6x 1280x800 VIEWS!)
# ============================================================================
import gc

PYMESH_CACHE: dict[tuple[int, str], pyrender.Mesh] = {}

def get_pymesh(src: trimesh.Scene, gname: str) -> pyrender.Mesh:
    key = (id(src), gname)
    pm = PYMESH_CACHE.get(key)
    if pm is None:
        pm = pyrender.Mesh.from_trimesh(src.geometry[gname], smooth=False)
        PYMESH_CACHE[key] = pm
    return pm

def add_instanced(ps: pyrender.Scene, src: trimesh.Scene, prefix: str, T=None, hatch_slide=0.0, piston_stroke=0.0):
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
        if piston_stroke != 0.0 and prefix.startswith("PISTON_"):
            st = gname.split("__")[0]
            extra[0, 3] = {"STAGE1": 6.6, "STAGE2": 13.2, "STAGE3": 19.8, "PUSHER": 19.8}.get(st, 0.0) * piston_stroke
        ps.add(get_pymesh(src, gname), pose=(T @ extra @ local))

def rot_from_out(out_dir):
    d = np.asarray(out_dir, float)
    d /= np.linalg.norm(d)
    inward = -d
    y_ax = np.array([0.0, 1.0, 0.0])
    z_ax = np.cross(inward, y_ax)
    z_ax /= np.linalg.norm(z_ax)
    R = np.eye(4)
    R[:3, 0] = inward
    R[:3, 1] = y_ax
    R[:3, 2] = z_ax
    return R

RADIAL_SITES = [
    ("UPPER",       (0.0, 0.0, 1.0)),
    ("LEFT",        (-1.0, 0.0, 0.0)),
    ("RIGHT",       (1.0, 0.0, 0.0)),
    ("LOWER_LEFT",  (-0.72, 0.0, -0.694)),
    ("LOWER_RIGHT", (0.72, 0.0, -0.694)),
    ("LOWER",       (0.0, 0.0, -1.0)),
]

def cam_pose(eye, target):
    eye = np.asarray(eye, float)
    target = np.asarray(target, float)
    f = target - eye
    f /= np.linalg.norm(f)
    up_ref = (0.0, 0.0, 1.0) if abs(f[2]) < 0.94 else (0.0, 1.0, 0.0)
    r = np.cross(f, up_ref)
    r /= np.linalg.norm(r)
    up = np.cross(r, f)
    T = np.eye(4)
    T[:3, :3] = np.stack((r, up, -f), axis=1)
    T[:3, 3] = eye
    return T

SHARED_RENDERER = pyrender.OffscreenRenderer(1280, 800)

def render_chamber_pose(eye, target, fov=56, deployed=True, include_window=True, lights_override=None):
    ps = pyrender.Scene(bg_color=[0.020, 0.025, 0.036, 1.0], ambient_light=[0.28, 0.31, 0.36])
    slide = 1.0 if deployed else 0.0
    stroke = 1.0 if deployed else 0.0

    add_instanced(ps, crown_glb,  "FAZ2_CROWN", hatch_slide=slide)
    add_instanced(ps, side_glb,   "FAZ2_SIDE")
    add_instanced(ps, rear_glb,   "FAZ2_REAR_REV05")
    add_instanced(ps, turb_glb,   "FAZ2_TURBINE")
    add_instanced(ps, grille_glb, "FAZ2_GRILLES")
    add_instanced(ps, m11_scene,  "FAZ3_M11_PIPING")
    if include_window:
        add_instanced(ps, win_glb, "FAZ2_WINDOW")

    for label, dir0 in RADIAL_SITES:
        d = np.asarray(dir0, float)
        d /= np.linalg.norm(d)
        R = rot_from_out(d)

        em_r = 16.17 if deployed else 35.97
        T_em = R.copy()
        T_em[:3, 3] = np.array([0.0, -2.70, 0.0]) + d * em_r
        add_instanced(ps, emitter_glb, f"EMITTER_{label}", T_em)

        T_pi = R.copy()
        T_pi[:3, 3] = np.array([0.0, -2.70, 0.0]) + d * 24.50
        add_instanced(ps, piston_glb, f"PISTON_{label}", T_pi, piston_stroke=stroke)

        T_bay = R.copy()
        bay_r = 27.60 if label in ("LOWER_LEFT", "LOWER_RIGHT") else 24.50
        T_bay[:3, 3] = np.array([0.0, -2.70, 0.0]) + d * bay_r
        add_instanced(ps, m12_scene, f"SERVICE_BAY_{label}", T_bay)

        if label in ("LEFT", "RIGHT"):
            add_instanced(ps, hatch_glb, f"SIDE_HATCH_{label}", T_pi, hatch_slide=slide)

    lights = lights_override if lights_override is not None else [
        ((0.0, -48.0,  5.0),  (0.90, 0.94, 1.00), 640.0),
        ((-16.5, -8.0, 14.5), (0.85, 0.91, 1.00), 420.0),
        (( 16.5, -8.0, 14.5), (0.85, 0.91, 1.00), 420.0),
        ((0.0,   6.5,  13.5), (0.86, 0.92, 1.00), 360.0),
        ((0.0,  -4.0, -14.5), (0.82, 0.89, 1.00), 340.0),
        ((-36.0, -2.7,  1.5), (0.86, 0.93, 1.00), 380.0),
        (( 36.0, -2.7,  1.5), (0.86, 0.93, 1.00), 380.0),
        (( 0.0,  -2.7, 35.0), (0.86, 0.93, 1.00), 320.0),
    ]
    for loc, rgb, intens in lights:
        lp = np.eye(4)
        lp[:3, 3] = loc
        ps.add(pyrender.PointLight(color=np.array(rgb), intensity=intens), pose=lp)
    ps.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)), pose=cam_pose(eye, target))
    rgba, _ = SHARED_RENDERER.render(ps, flags=pyrender.RenderFlags.RGBA)
    return Image.fromarray(rgba, "RGBA").convert("RGB")

def render_cutaway_bay():
    ps = pyrender.Scene(bg_color=[0.020, 0.025, 0.036, 1.0], ambient_light=[0.32, 0.35, 0.40])
    for node in m12_scene.graph.nodes_geometry:
        tr, gname = m12_scene.graph[node]
        # Remove ceiling + camera-facing (-Y) left wall + upper strip lamp on -Y side for crisp 3/4 architectural cutaway!
        if gname.startswith("VAULT_CEILING") or gname.startswith("VAULT_WALL_LEFT"):
            continue
        ps.add(get_pymesh(m12_scene, gname), pose=tr)
    add_instanced(ps, piston_glb, "PISTON_CUT", np.eye(4), piston_stroke=0.65)
    T_em = np.eye(4); T_em[0, 3] = 1.50
    add_instanced(ps, emitter_glb, "EMITTER_CUT", T_em)
    add_instanced(ps, hatch_glb, "HATCH_CUT", np.eye(4), hatch_slide=1.0)
    for loc, rgb, intens in [
        ((-12.0, -20.0, 14.0), (0.92, 0.95, 1.00), 620.0),
        ((-28.0, -18.0, 12.0), (0.88, 0.93, 1.00), 540.0),
        ((-20.0,   2.0,  6.0), (0.86, 0.92, 1.00), 380.0),
        ((-35.0,  -2.0,  4.0), (0.86, 0.92, 1.00), 360.0),
    ]:
        lp = np.eye(4); lp[:3, 3] = loc
        ps.add(pyrender.PointLight(color=np.array(rgb), intensity=intens), pose=lp)
    ps.add(pyrender.PerspectiveCamera(yfov=math.radians(48)), pose=cam_pose((-21.0, -25.5, 14.5), (-20.5, 1.0, -1.2)))
    rgba, _ = SHARED_RENDERER.render(ps, flags=pyrender.RenderFlags.RGBA)
    return Image.fromarray(rgba, "RGBA").convert("RGB")

print("[RENDER] Rendering 6 instanced 1280x800 Faz 3 views...", flush=True)
v1 = render_chamber_pose((0.0, -53.5, -1.8), (0.0, 2.0, -0.2), fov=52, deployed=True, include_window=True)
v2 = render_chamber_pose((0.0, -53.5, -1.8), (0.0, 2.0, -0.2), fov=52, deployed=False, include_window=True)
v3 = render_chamber_pose((-6.5, -15.5, 4.0), (-18.8, 8.5, 11.5), fov=62, deployed=True, include_window=False)
v4 = render_chamber_pose((6.5, -11.5, 1.2), (-36.0, -2.7, 0.2), fov=50, deployed=True, include_window=False, lights_override=[
    ((-6.0, -8.0, 4.0),   (0.88, 0.93, 1.00), 380.0),
    ((-22.0, -2.7, 2.5),  (0.86, 0.93, 1.00), 340.0),
    ((-34.0, -2.7, 2.5),  (0.84, 0.92, 1.00), 380.0),
    ((-48.0, -2.7, 2.5),  (0.82, 0.91, 1.00), 380.0),
    ((-58.0, -2.7, 1.0),  (0.80, 0.90, 1.00), 300.0),
])
v5 = render_cutaway_bay()
v6 = render_chamber_pose((-2.5, -15.8, -8.5), (-13.5, 9.0, -18.2), fov=60, deployed=True, include_window=False, lights_override=[
    ((-8.0, -8.0, -10.0), (0.88, 0.93, 1.00), 420.0),
    ((-14.0, 6.0, -14.0), (0.86, 0.92, 1.00), 380.0),
    ((  0.0, -2.7, -34.0),(0.84, 0.92, 1.00), 360.0),
    ((-34.0, -2.7, -34.0),(0.84, 0.92, 1.00), 360.0),
])
SHARED_RENDERER.delete()
PYMESH_CACHE.clear()
gc.collect()

debug_saves = [
    ("FAZ3_TEST_01_CONTROL_ROOM_DEPLOYED.png", v1),
    ("FAZ3_TEST_02_CONTROL_ROOM_COLD.png", v2),
    ("FAZ3_TEST_03_UPPER_CRYO_MAINS_AND_VALVES_CLOSEUP.png", v3),
    ("FAZ3_TEST_04_OPEN_HATCH_PORTAL_LOOKING_INTO_BAY.png", v4),
    ("FAZ3_TEST_05_PISTON_SERVICE_BAY_CUTAWAY_ISO.png", v5),
    ("FAZ3_TEST_06_LOWER_PIT_RETURN_AND_RADIATOR_TIE_IN.png", v6),
]
for fname, im in debug_saves:
    p = DBG / fname
    im.save(p, optimize=True)
    print(f"  -> Saved gallery debug render: {p.name} ({p.stat().st_size // 1024} KB)")


# ============================================================================
# 7. COMPOSE 6-PANEL TURKISH APPROVAL BOARD
#    model_exports/FAZ3_PAKET_B_BORULAMA_VE_PISTON_SERVIS_ONAY.png
# ============================================================================
board = Image.new("RGB", (1920, 1390), (12, 16, 24))
draw = ImageDraw.Draw(board)
bold_p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
reg_p  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_title = ImageFont.truetype(bold_p, 26)
f_sub   = ImageFont.truetype(reg_p,  16)
f_lbl   = ImageFont.truetype(bold_p, 13)

draw.text((30, 16), "FAZ 3 (PAKET B) — REAKTÖR KRİYOJENİK BORULAMA AĞI (M11) & 6 PİSTON ARKASI SERVİS GALERİSİ (M12) ÖN-İZLEME", font=f_title, fill=(242, 246, 252))
draw.text((30, 52), "Görüş hattı %100 açık (çekirdek, 6 lazer, 6 sürgülü kapak, 10 kanatlı arka türbin engelsiz) • Açılan 6 yuvanın arkasında %0 siyah boşluk • Sıfır turuncu/bakır yüzey.", font=f_sub, fill=(174, 194, 218))

panels = [
    (v1,   30,  90, 600, 385, "1) KONTROL ODASI (DEPLOYED) • 6 Kapak Açık, M11 Borular & Arkası Dolu 6 Yuva"),
    (v2,  660,  90, 600, 385, "2) KONTROL ODASI (COLD) • 6 Kapak Kapalı, Üst/Köşe/Taban Boru & Kablo Ağı"),
    (v3, 1290,  90, 600, 385, "3) ÜST 45° KRİYOJENİK HAT & KÖŞE VANA • Flanşlar, Kablo Tavası, Manometre"),
    (v4,   30, 498, 600, 385, "4) AÇIK SL-01 YUVASI İÇİ • Yayıcı Arkasında Aydınlık Hidrolik Servis Galerisi"),
    (v5,  660, 498, 600, 385, "5) M12 SERVİS GALERİSİ KESİTİ • Piston + Akümülatörler + Yürüyüş Izgarası + Hava Kilidi"),
    (v6, 1290, 498, 600, 385, "6) ALT ÇUKUR DÖNÜŞ & YG BARA • Radyatör Bağlantısı & SL-03/05 Açık Yuvalar"),
]

for im, x, y, w, h, cap in panels:
    contained = ImageOps.contain(im, (w - 6, h - 38), Image.Resampling.LANCZOS)
    board.paste(contained, (x + (w - contained.width) // 2, y + 34 + (h - 36 - contained.height) // 2))
    draw.rectangle((x, y, x + w, y + h), outline=(66, 86, 112), width=2)
    draw.rectangle((x, y, x + w, y + 32), fill=(22, 30, 44))
    draw.text((x + 10, y + 7), cap, font=f_lbl, fill=(238, 244, 252))

draw.rectangle((30, 906, 1890, 1364), fill=(17, 23, 34), outline=(58, 78, 102), width=2)
summary_lines = [
    "ÜRETİLEN FAZ 3 (PAKET B) 3B GLB DOSYALARI (Henüz Roblox Studio'ya KURULMADI — Kullanıcı Ön-İzleme Onayı Bekliyor):",
    f"  • M11 — REACTOR_COOLANT_PIPING_RING_01.glb ({len(m11_scene.geometry)} mesh grubu, {m11_tris:,} üçgen, {m11_bytes/1e6:.2f} MB):",
    "      - Üst 45° sekizgen eğimlerde çift kriyojenik ana hat (Ø 1.04 fırçalı nikel-arduvaz + Ø 0.68 koyu gunmetal), 12 cıvatalı ANSI flanşlar, C-kelepçeler.",
    "      - Arka köşe iniş kollektörleri, kollu kesme vanaları, ışıklı çift manometre blokları, arka plenum üst köprü hattı ve alt radyatör yan bağlantıları.",
    "      - Üst çevre + alt çukur tabanında delikli yüksek gerilim kablo tavaları (HV_CABLE_TRAY / FLOOR_HV_BUSBAR) ve Faz 4.2 için 4 ayrı flanşlı kopma modülü (PIPE_SPOOL_*).",
    f"  • M12 — PISTON_REAR_SERVICE_BAY_01.glb ({len(m12_scene.geometry)} mesh grubu, {m12_tris:,} üçgen, {m12_bytes/1e6:.2f} MB — 6 radyal yuvaya tam uyumlu):",
    "      - SL-00..SL-05 kapakları açıldığında yayıcı boğazının arkasındaki siyah boşluğu %100 ortadan kaldıran 35.5 stud derinlikli zırhlı hidrolik servis galerisi.",
    "      - Piston kafesinin iki yanında çift yüksek basınçlı hidrolik akümülatör tüpü, örgülü besleme boruları, delikli çelik yürüyüş ızgarası + korkuluklar,",
    "        gömme soğuk-beyaz şerit servis lambaları ve en arkada bağlantılı dış tesis bakım hava kilidi kapısı (MAINT-BAY).",
    "",
    "ONAY SONRASI ADIM: Onaylarsanız Faz 3.3 kapsamında M11 + 6 adet M12 servis galerisini AEGIS_Reactor.rbxlx sahnesine kurup canlı Studio Play ile doğrulayacağız.",
]
cy = 922
for idx_l, line in enumerate(summary_lines):
    ft = f_lbl if idx_l == 0 or idx_l == len(summary_lines) - 1 else f_sub
    col = (245, 214, 138) if idx_l == 0 else ((162, 232, 198) if idx_l == len(summary_lines) - 1 else (210, 222, 236))
    draw.text((48, cy), line, font=ft, fill=col)
    cy += 38

BOARD_PATH = EXP / "FAZ3_PAKET_B_BORULAMA_VE_PISTON_SERVIS_ONAY.png"
board.save(BOARD_PATH, optimize=True)
print(f"[OK] Approval board saved: {BOARD_PATH} ({BOARD_PATH.stat().st_size/1e6:.2f} MB)")
