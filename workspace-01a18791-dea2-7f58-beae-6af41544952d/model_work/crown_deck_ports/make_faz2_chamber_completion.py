#!/usr/bin/env python3
"""Faz 2 Paket A — Complete Octagonal Chamber Shell, 4 Radial Sliding-Hatch Ports & Panoramic Armor Window Frame.

Exports (offline authoring space: X right, Y front(-18)->rear(+15.5), Z up; optical center = (0, -2.70, 0)):
  1) model_exports/REACTOR_CROWN_DECK_AND_RADIAL_PORTS_01.glb
     - Stepped octagonal ceiling crown (X = -17..+17, Z = +21.5..+24.6) in matching oxidized dark iron + gunmetal
       with stepped octagonal recessed white contour strips (reference image-3 / 01_komut_110)
     - Octagonal reactor pit deck (X = -17..+17, Z = -21.5..-24.6) + lower slatted radiator containment banks
       with worn amber-black hazard stripes (reference 01_komut_110 & image-3)
     - 4 vertical open-web steel lattice corner trusses + vertical recessed strip worklight housings
     - 4 genuine open-through radial port housings + 8 separately named sliding mechanical hatch leaves
       (UPPER, LOWER, LOWER_LEFT, LOWER_RIGHT) matching approved SL-01/SL-02 +/-5.85 Y sliding travel!
  2) model_exports/REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV03_DIAG_OPEN.glb
     - Preserves 100% of Rev02's oxidized iron PBR, UVs, waist portals, and upper/lower octagonal folds,
       while cutting genuine watertight through-openings in the lower diagonal blocks for LOWER_LEFT & LOWER_RIGHT
       so opening the diagonal hatches reveals real behind-wall depth (zero blocking sheet!).
  3) model_exports/OBSERVATION_WINDOW_ARMOR_FRAME_01.glb
     - Front panoramic 3-pane beveled armor window bulkhead at Y = -18.0..-20.6 (mullions at X = +/-14.8,
       unobstructed 29.6-stud center view, full SL-01/SL-02 side visibility, solid outer bulkhead wings sealing
       behind-wall pistons from the control room).

Existing approved GLBs in model_exports/ remain 100% UNMODIFIED. Nothing is written to Roblox Studio before user approval.
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
EXP.mkdir(parents=True, exist_ok=True)

# ============================================================================
# 1. MULTI-TONE INDUSTRIAL SLATE / GRAPHITE / OLIVE-TAUPE IRON PBR PALETTE
#    (Calibrated pixel-for-pixel from 01_komut_110.jpg normal white lighting — ZERO coppery tint!)
# ============================================================================
W = H = 512
rng = np.random.default_rng(602061)
def wrap_noise(sigma):
    q = gaussian_filter(rng.standard_normal((H, W)), sigma=sigma, mode="wrap")
    return q / (q.std() + 1e-8)

macro = wrap_noise(14)
micro = wrap_noise(2.4)
grain = rng.standard_normal((H, W))
wear = np.clip(0.46 + 0.08 * macro + 0.08 * micro + 0.025 * grain, 0.14, 0.78)
scars = rng.random((H, W)) < 0.008

def make_rolled_iron_tex(c_primary, c_secondary):
    b = (1 - wear[..., None]) * np.asarray(c_secondary, float) + wear[..., None] * np.asarray(c_primary, float)
    b += np.clip(grain, -2.5, 2.5)[..., None] * 1.35
    b[scars] -= np.array([18.0, 18.0, 20.0])
    return Image.fromarray(np.uint8(np.clip(b, 8, 245)), "RGB")

# Exact 3-zone multi-tone industrial iron courses from 01_komut_110.jpg:
IRON_UPPER_SLATE = make_rolled_iron_tex((94.0, 106.0, 128.0), (112.0, 122.0, 140.0))  # Z > +8.5: Cool Slate-Blue Steel
IRON_MID_GRAPHITE = make_rolled_iron_tex((72.0, 77.0, 90.0), (90.0, 95.0, 106.0))     # Z in [-2..+8.5]: Cool Graphite-Iron
IRON_LOWER_DADO = make_rolled_iron_tex((74.0, 72.0, 64.0), (60.0, 60.0, 58.0))        # Z < -2.0: Olive-Taupe / Gunmetal Dado
IRON_CROWN_DARK = make_rolled_iron_tex((62.0, 66.0, 79.0), (80.0, 85.0, 98.0))        # Ceiling Crown & Sump Deck

MR = np.empty((H, W, 3), np.uint8)
MR[:, :, 0] = 255
MR[:, :, 1] = np.uint8(np.clip((0.42 + 0.20 * wear + 0.02 * np.abs(micro)) * 255, 1, 255))
MR[:, :, 2] = np.uint8(np.clip((0.88 - 0.22 * wear) * 255, 1, 255))
IRON_MR = Image.fromarray(MR, "RGB")

hmap = micro * 0.55 + wrap_noise(0.9) * 0.14 + scars * 0.22
gy, gx = np.gradient(hmap)
nx, ny, nz = -gx * 0.045, -gy * 0.045, np.ones_like(gx)
nlen = np.sqrt(nx * nx + ny * ny + nz * nz)
IRON_NORM = Image.fromarray(np.uint8(np.clip((np.stack((nx, ny, nz), 2) / nlen[..., None] * 0.5 + 0.5) * 255, 0, 255)), "RGB")

def make_brushed_steel(rgb, seed=715):
    rr = np.random.default_rng(seed)
    fine = rr.standard_normal((512, 512)) * 2.1
    coarse = gaussian_filter(rr.standard_normal((512, 512)), sigma=18, mode="wrap") * 3.8
    arr = np.empty((512, 512, 3), float)
    arr[:] = rgb
    arr += (fine + coarse)[..., None] * np.array([0.92, 0.96, 1.0])
    return Image.fromarray(np.uint8(np.clip(arr, 10, 245)), "RGB")

PLATE_TEX = make_brushed_steel((82, 88, 98), 715)
GUNMETAL_TEX = make_brushed_steel((46, 51, 60), 719)
RADIATOR_TEX = make_brushed_steel((80, 75, 64), 723)  # Exact muted olive-taupe radiator panel from 01_komut_110.jpg!

def make_sign_tex(code_txt, sub_txt="Muhafaza"):
    im = make_brushed_steel((52, 56, 64), 760).resize((512, 224))
    d = ImageDraw.Draw(im)
    d.rectangle((8, 8, 503, 215), outline=(92, 98, 108), width=3)
    try:
        f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    for txt, font, cy, ink in [(code_txt, f1, 68, (206, 212, 220)), (sub_txt, f2, 148, (176, 184, 196))]:
        bb = d.textbbox((0, 0), txt, font=font)
        ww, hh = bb[2] - bb[0], bb[3] - bb[1]
        d.text(((512 - ww) // 2, cy - hh // 2 - bb[1]), txt, font=font, fill=ink)
    return im

def pbr(name, color=(255, 255, 255), met=0.78, rough=0.50, tex=None, mr=None, normal=None, emi=(0.0, 0.0, 0.0)):
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
    "iron": pbr("Rolled slate-graphite chamber iron", None, 1.0, 1.0, IRON_CROWN_DARK, IRON_MR, IRON_NORM),
    "iron_upper": pbr("Upper frieze cool slate-blue steel", None, 1.0, 1.0, IRON_UPPER_SLATE, IRON_MR, IRON_NORM),
    "iron_mid": pbr("Mid bulkhead cool graphite-slate iron", None, 1.0, 1.0, IRON_MID_GRAPHITE, IRON_MR, IRON_NORM),
    "iron_lower": pbr("Lower dado olive-taupe gunmetal iron", None, 1.0, 1.0, IRON_LOWER_DADO, IRON_MR, IRON_NORM),
    "gunmetal": pbr("Heavy structural gunmetal", None, 0.84, 0.45, GUNMETAL_TEX, None, IRON_NORM),
    "plate": pbr("Brushed containment door steel", None, 0.86, 0.34, PLATE_TEX, None, IRON_NORM),
    "radiator": pbr("Slatted olive-taupe radiator housing", None, 0.72, 0.54, RADIATOR_TEX, None, IRON_NORM),
    "frame": pbr("Dark charcoal wrought structural frame", (46, 50, 58), 0.86, 0.46),
    "dark": pbr("Deep recessed shaft liner", (24, 28, 35), 0.65, 0.58),
    "edge": pbr("Machined cold-steel bevel", (142, 149, 158), 0.91, 0.31),
    "hazard": pbr("Crisp light-grey containment stripe enamel", (204, 208, 214), 0.22, 0.66),
    "caution_yel": pbr("Industrial muted yellow dado caution trim", (192, 170, 58), 0.24, 0.64),
    "lumen": pbr("Recessed octagonal architectural strip", (230, 242, 252), 0.12, 0.32, emi=(0.88, 0.94, 1.0)),
    "worklight": pbr("Recessed vertical corner worklight lens", (218, 232, 248), 0.15, 0.28, emi=(0.76, 0.85, 0.98)),
    "pocket": pbr("Satin slider pocket steel", (78, 83, 92), 0.84, 0.48),
    "red": pbr("Unlit containment signal lens", (124, 52, 48), 0.56, 0.46),
    "sign_u": pbr("Plaque SL-00", None, 0.22, 0.74, make_sign_tex("SL-00", "Muhafaza")),
    "sign_d": pbr("Plaque SL-05", None, 0.22, 0.74, make_sign_tex("SL-05", "Muhafaza")),
    "sign_ll": pbr("Plaque SL-03", None, 0.22, 0.74, make_sign_tex("SL-03", "Muhafaza")),
    "sign_lr": pbr("Plaque SL-04", None, 0.22, 0.74, make_sign_tex("SL-04", "Muhafaza")),
}

def world_uv(verts):
    # Isotropic 12-stud world projection so iron/steel grain matches Rev02 seamlessly
    u = (verts[:, 0] + verts[:, 1] + 24.0) / 12.0
    v = (verts[:, 2] + verts[:, 1] * 0.35 + 24.0) / 12.0
    return np.stack((u, v), axis=1)

class SceneBuilder:
    def __init__(self):
        self.bins = {}

    def add(self, node_name: str, mat_key: str, mesh: trimesh.Trimesh, uv=None):
        if len(mesh.faces) == 0:
            return
        v = np.asarray(mesh.vertices, float)
        f = np.asarray(mesh.faces, int)
        u = np.asarray(uv, float) if uv is not None else world_uv(v)
        bucket = self.bins.setdefault((node_name, mat_key), [[], [], []])
        off = sum(len(x) for x in bucket[0])
        bucket[0].append(v)
        bucket[1].append(f + off)
        bucket[2].append(u)

    def box(self, node_name: str, mat_key: str, center, extents, T=None):
        g = trimesh.creation.box(extents=extents)
        g.apply_translation(center)
        if T is not None:
            g.apply_transform(T)
        self.add(node_name, mat_key, g)

    def cyl(self, node_name: str, mat_key: str, a, b, r, sections=12, T=None):
        a = np.asarray(a, float)
        b = np.asarray(b, float)
        d = b - a
        L = np.linalg.norm(d)
        if L < 1e-5:
            return
        g = trimesh.creation.cylinder(radius=r, height=L, sections=sections)
        g.apply_transform(trimesh.geometry.align_vectors((0, 0, 1), d / L))
        g.apply_translation((a + b) * 0.5)
        if T is not None:
            g.apply_transform(T)
        self.add(node_name, mat_key, g)

    def quad(self, node_name: str, mat_key: str, pts, T=None, uv=None):
        pts_arr = np.asarray(pts, float)
        if T is not None:
            hom = np.c_[pts_arr, np.ones(len(pts_arr))]
            pts_arr = (T @ hom.T).T[:, :3]
        faces = [[0, 1, 2], [0, 2, 3]]
        g = trimesh.Trimesh(vertices=pts_arr, faces=faces, process=False)
        if uv is None:
            uv = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
        self.add(node_name, mat_key, g, uv=uv)

    def export_glb(self, out_path: Path):
        sc = trimesh.Scene()
        tris = 0
        for (node_name, mat_key), (vs, fs, uvs) in self.bins.items():
            g = trimesh.Trimesh(vertices=np.concatenate(vs), faces=np.concatenate(fs), process=False)
            g.remove_unreferenced_vertices()
            # Recompute UV if vertex removal compacted indices
            if len(g.vertices) == sum(len(x) for x in vs):
                uv_all = np.concatenate(uvs)
            else:
                uv_all = world_uv(g.vertices)
            g.visual = trimesh.visual.texture.TextureVisuals(uv=uv_all, material=MATS[mat_key])
            gname = f"{node_name}__{mat_key}"
            sc.add_geometry(g, geom_name=gname, node_name=gname)
            tris += len(g.faces)
        data = sc.export(file_type="glb")
        out_path.write_bytes(data)
        ver = trimesh.load(out_path, force="scene", process=False)
        assert len(ver.geometry) == len(sc.geometry)
        return ver, tris, len(data)


# ============================================================================
# 2. HELPER: BUILD ONE RADIAL CONTAINMENT PORT + 2 SLIDING HATCH LEAVES
# ============================================================================
def add_radial_port_module(sb: SceneBuilder, prefix: str, sign_key: str, outward_dir, radius_seat=24.35, bay_half_w=6.2):
    """Creates a local port frame + two separately named sliding hatch leaves.

    Local frame convention (matching approved REACTOR_WALL_HATCH_THROUGH_01):
      +X_local = inward toward (0, -2.70, 0)
      +Y_local = chamber depth (+Y_world, rearwards; leaves slide +/-5.85 along Y_local!)
      +Z_local = cross-width perpendicular to outward_dir and Y_world
    Clear opening: Y_local in [-5.60, +5.60] (11.20 studs), Z_local in [-3.55, +3.55] (7.10 studs),
    giving generous visible clearance around the 3.07-radius approved emitter!
    """
    d = np.asarray(outward_dir, float)
    d /= np.linalg.norm(d)
    inward = -d
    y_ax = np.array([0.0, 1.0, 0.0])
    z_ax = np.cross(inward, y_ax)
    z_ax /= np.linalg.norm(z_ax)

    T = np.eye(4)
    T[:3, 0] = inward
    T[:3, 1] = y_ax
    T[:3, 2] = z_ax
    T[:3, 3] = np.array([0.0, -2.70, 0.0]) + d * radius_seat

    open_y = 5.60
    open_z = 3.55
    frame_y = 11.95
    frame_z = bay_half_w
    depth_t = 2.15  # recessed open shaft from X_local = +0.08 back to -2.07 (NO rear backplate!)

    # 4 structural surround frame bars around the genuine through-hole
    # Top & bottom Z bands (spanning full Y track length)
    for sgn in (-1, 1):
        zc = sgn * (open_z + (frame_z - open_z) * 0.5)
        zh = frame_z - open_z
        sb.box(f"{prefix}_PORT_FRAME", "gunmetal", (-depth_t * 0.5, 0.0, zc), (depth_t, frame_y * 2, zh), T=T)
        sb.box(f"{prefix}_PORT_CLADDING", "iron", (0.06, 0.0, zc), (0.12, frame_y * 2 - 0.3, zh - 0.18), T=T)
    # Front & rear Y bridge pillars outside the +/-5.60 aperture (with recessed slider pockets!)
    for sgn in (-1, 1):
        yc = sgn * (open_y + (frame_y - open_y) * 0.5)
        yw = frame_y - open_y
        # Rear pocket wall sits at X_local = -0.55 so sliding leaves at X_local = +0.16..+0.34 travel freely!
        sb.box(f"{prefix}_PORT_POCKET", "pocket", (-1.30, yc, 0.0), (1.50, yw, open_z * 2), T=T)
        # Front retaining fascia outside Y = +/-6.05
        outer_y0 = 6.05
        if frame_y > outer_y0 + 0.2:
            yc2 = sgn * (outer_y0 + (frame_y - outer_y0) * 0.5)
            yw2 = frame_y - outer_y0
            sb.box(f"{prefix}_PORT_FRAME", "gunmetal", (0.42, yc2, 0.0), (0.20, yw2, open_z * 2 + 0.5), T=T)

    # Inner dark shaft bevel lining (4 open walls, 0% backplate!)
    sb.box(f"{prefix}_SHAFT_LINER", "dark", (-1.0, 0.0, open_z + 0.06), (depth_t, open_y * 2, 0.12), T=T)
    sb.box(f"{prefix}_SHAFT_LINER", "dark", (-1.0, 0.0, -open_z - 0.06), (depth_t, open_y * 2, 0.12), T=T)
    for zc in (-open_z, open_z):
        sb.cyl(f"{prefix}_PORT_BEVEL", "edge", (0.14, -open_y, zc), (0.14, open_y, zc), 0.065, sections=8, T=T)
        # Guide rails for the two sliding hatch leaves
        sb.box(f"{prefix}_HATCH_RAILS", "frame", (0.22, 0.0, sgn_val := (zc + (0.22 if zc > 0 else -0.22))), (0.28, frame_y * 1.94, 0.24), T=T)

    # Amber-black diagonal warning bands along the surround frame (matching reference!)
    if frame_z - open_z >= 1.45:
        for sgn in (-1, 1):
            zc = sgn * (open_z + (frame_z - open_z) * 0.52)
            sb.box(f"{prefix}_HAZARD_BACK", "dark", (0.15, 0.0, zc), (0.04, 15.2, 0.68), T=T)
            for yy in np.arange(-7.1, 6.8, 1.45):
                pts = [
                    (0.18, yy, zc - 0.29),
                    (0.18, yy + 0.68, zc - 0.29),
                    (0.18, yy + 1.12, zc + 0.29),
                    (0.18, yy + 0.44, zc + 0.29),
                ]
                sb.quad(f"{prefix}_HAZARD_STRIPE", "hazard", pts, T=T)

    # Flush equipment sign on the +Z side if space allows
    if frame_z - open_z >= 1.9:
        zc_sign = open_z + 1.05
        sb.quad(
            f"{prefix}_EQUIPMENT_SIGN",
            sign_key,
            [
                (0.19, -3.1, zc_sign - 0.72),
                (0.19,  3.1, zc_sign - 0.72),
                (0.19,  3.1, zc_sign + 0.72),
                (0.19, -3.1, zc_sign + 0.72),
            ],
            T=T,
        )

    # TWO SEPARATELY NAMED SLIDING CONTAINMENT LEAVES (<PREFIX>_HATCH_LEFT & <PREFIX>_HATCH_RIGHT)
    # Closed pose covers Y_local in [-5.75, 0.02] and [-0.02, +5.75]; slides +/-5.85 along chamber Y (Studio Z)!
    for leaf_tag, y0, y1 in [("HATCH_LEFT", -5.76, 0.02), ("HATCH_RIGHT", -0.02, 5.76)]:
        node = f"{prefix}_{leaf_tag}"
        yc = (y0 + y1) * 0.5
        yw = y1 - y0
        sb.box(node, "plate", (0.20, yc, 0.0), (0.18, yw, open_z * 2 + 0.16), T=T)
        sb.box(node, "dark", (0.30, yc, 0.0), (0.05, yw - 0.48, open_z * 2 - 0.62), T=T)
        sb.box(node, "plate", (0.33, yc, 0.0), (0.04, yw - 0.86, open_z * 2 - 1.05), T=T)
        # Center meeting interlocking seam + vertical stiffening ribs
        seam_y = y1 - 0.08 if leaf_tag == "HATCH_LEFT" else y0 + 0.08
        sb.box(node, "edge", (0.26, seam_y, 0.0), (0.22, 0.14, open_z * 2 + 0.12), T=T)
        # Subtle warning chevron near center seam (matching approved HATCH_THROUGH_01!)
        chev_y = -0.85 if leaf_tag == "HATCH_LEFT" else 0.85
        sb.box(node, "hazard", (0.36, chev_y, 0.0), (0.02, 0.42, open_z * 1.45), T=T)


# ============================================================================
# 3. BUILD MODEL A: REACTOR_CROWN_DECK_AND_RADIAL_PORTS_01.glb
# ============================================================================
sb_crown = SceneBuilder()

Y_FRONT, Y_REAR = -18.0, 15.48
PORT_HOLE_X = 6.20        # matches bay_half_w of UPPER & LOWER port modules
PORT_HOLE_Y0 = -14.65     # matches frame_y around Y = -2.70 (-2.70 - 11.95)
PORT_HOLE_Y1 = 9.25       # (-2.70 + 11.95)

# A) Stepped Octagonal Ceiling Crown (Z = +21.5..+24.6) & Reactor Pit Deck (Z = -21.5..-24.6)
for sgn, section in [(1, "ROOF"), (-1, "DECK")]:
    z_inner = sgn * 21.50
    z_mid = sgn * 22.85
    thick = 2.60

    # Left and Right continuous lateral ceiling/floor slabs flanking the central port bay (X = -17..-6.2 and +6.2..+17)
    for x0, x1 in [(-17.05, -PORT_HOLE_X), (PORT_HOLE_X, 17.05)]:
        xc, xw = (x0 + x1) * 0.5, (x1 - x0)
        yc, yw = (Y_FRONT + Y_REAR) * 0.5, (Y_REAR - Y_FRONT)
        sb_crown.box(f"{section}_STRUCTURAL_SLAB", "gunmetal", (xc, yc, z_mid), (xw, yw, thick))
        sb_crown.box(f"{section}_ROLLED_IRON_SKIN", "iron", (xc, yc, z_inner + sgn * 0.12), (xw - 0.22, yw - 0.28, 0.22))

    # Front and Rear bridge slabs around the port module (X = -6.2..+6.2, Y = -18..-14.65 and +9.25..+15.48)
    for y0, y1 in [(Y_FRONT, PORT_HOLE_Y0), (PORT_HOLE_Y1, Y_REAR)]:
        yc, yw = (y0 + y1) * 0.5, (y1 - y0)
        sb_crown.box(f"{section}_BRIDGE_SLAB", "gunmetal", (0.0, yc, z_mid), (PORT_HOLE_X * 2, yw, thick))
        sb_crown.box(f"{section}_ROLLED_IRON_SKIN", "iron", (0.0, yc, z_inner + sgn * 0.12), (PORT_HOLE_X * 2 - 0.18, yw - 0.18, 0.22))

    # Heavy octagonal transverse steel arch ribs (matching industrial chamber ribs)
    for y_rib in (-16.8, -14.8, 9.5, 13.8):
        sb_crown.box(f"{section}_ARCH_GIRDER", "frame", (0.0, y_rib, z_inner - sgn * 0.22), (33.8, 0.62, 0.46))
        sb_crown.cyl(f"{section}_ARCH_BEVEL", "edge", (-16.8, y_rib, z_inner - sgn * 0.44), (16.8, y_rib, z_inner - sgn * 0.44), 0.075, sections=10)

    # Stepped Octagonal Recessed White Contour Channels on Ceiling & Pit Perimeter (seen in image-3 & 01_komut_110!)
    for y_line in (-15.4, 10.6):
        # Horizontal segment across roof/floor
        sb_crown.box(f"{section}_CONTOUR_HOUSING", "frame", (0.0, y_line, z_inner - sgn * 0.08), (32.8, 0.42, 0.16))
        sb_crown.box(f"{section}_CONTOUR_LUMEN", "lumen", (0.0, y_line, z_inner - sgn * 0.15), (32.2, 0.13, 0.07))
        # Diagonal stepped continuations down/up the octagonal slopes (X: +/-16.4 -> +/-23.2, Z: +/-21.4 -> +/-13.5)
        for side in (-1, 1):
            a_pt = (side * 16.4, y_line, sgn * 21.35)
            b_pt = (side * 23.1, y_line, sgn * 13.55)
            sb_crown.cyl(f"{section}_CONTOUR_HOUSING", "frame", a_pt, b_pt, 0.17, sections=8)
            a_lm = (side * 16.32, y_line - 0.04, sgn * 21.26)
            b_lm = (side * 23.02, y_line - 0.04, sgn * 13.48)
            sb_crown.cyl(f"{section}_CONTOUR_LUMEN", "lumen", a_lm, b_lm, 0.065, sections=8)

# Install UPPER and LOWER radial sliding-hatch port modules flush at Z = +/-21.55!
add_radial_port_module(sb_crown, "UPPER", "sign_u", (0.0, 0.0, 1.0), radius_seat=21.75, bay_half_w=6.20)
add_radial_port_module(sb_crown, "LOWER", "sign_d", (0.0, 0.0, -1.0), radius_seat=21.75, bay_half_w=6.20)

# B) Lower-Left & Lower-Right 43.9-Degree Armored Containment Port Bays + Sliding Hatches
#    Seated FLUSH into the sloped octagonal wall at r = 26.10 (still clearing retracted emitter tip at r = 26.64
#    and piston cage at r = 26.99 in COLD mode, eliminating any inward-protruding box step!)
for side, p_tag, s_key in [(-1, "LOWER_LEFT", "sign_ll"), (1, "LOWER_RIGHT", "sign_lr")]:
    out_d = np.array([side * 0.72, 0.0, -0.694], float)
    out_d /= np.linalg.norm(out_d)
    add_radial_port_module(sb_crown, p_tag, s_key, out_d, radius_seat=26.10, bay_half_w=5.15)
    # Flush perimeter weld trim tying the port cleanly into the sloped iron sheet
    for y_gus in (-14.55, 9.15):
        p_top = np.array([side * 23.95, y_gus, -12.6])
        p_bot = np.array([side * 16.95, y_gus, -21.35])
        sb_crown.cyl(f"{p_tag}_STRUCTURAL_TIE", "frame", p_top, p_bot, 0.20, sections=10)

# C) Reference Lower Louvered Radiator Containment Banks + Hazard Stripes (01_komut_110.jpg bottom rear wall!)
for side in (-1, 1):
    r_tag = "LEFT_RADIATOR_BANK" if side < 0 else "RIGHT_RADIATOR_BANK"
    xc = side * 12.6
    yc = 13.55
    zc = -14.8
    # Angled radiator cabinet along lower rear bulkhead flanking central bay
    sb_crown.box(r_tag, "gunmetal", (xc, yc, zc), (11.2, 1.25, 6.4))
    sb_crown.box(r_tag, "dark", (xc, yc - 0.56, zc - 0.25), (10.2, 0.24, 4.6))
    # Vertical radiator louvers (seen directly in 01_komut_110.jpg!)
    for lx in np.linspace(xc - 4.7, xc + 4.7, 22):
        sb_crown.box(r_tag, "radiator", (lx, yc - 0.62, zc - 0.25), (0.24, 0.22, 4.35))
    # Top muted-yellow & charcoal diagonal caution header bar above radiator bank (matching 01_komut_110.jpg!)
    sb_crown.box(r_tag, "dark", (xc, yc - 0.64, zc + 2.55), (10.8, 0.14, 0.44))
    for hx in np.linspace(xc - 5.0, xc + 4.5, 14):
        pts = [
            (hx, yc - 0.72, zc + 2.36),
            (hx + 0.36, yc - 0.72, zc + 2.36),
            (hx + 0.60, yc - 0.72, zc + 2.74),
            (hx + 0.24, yc - 0.72, zc + 2.74),
        ]
        sb_crown.quad(r_tag, "caution_yel", pts)
    # Bottom floor-apron crisp light-grey diagonal containment stripes (matching 01_komut_110.jpg floor sill!)
    sb_crown.box(r_tag, "dark", (xc, yc - 0.68, -20.85), (10.8, 0.18, 0.78))
    for sx_i in np.linspace(xc - 4.8, xc + 4.2, 8):
        pts_s = [
            (sx_i, yc - 0.79, -21.20),
            (sx_i + 0.56, yc - 0.79, -21.20),
            (sx_i + 0.92, yc - 0.79, -20.52),
            (sx_i + 0.36, yc - 0.79, -20.52),
        ]
        sb_crown.quad(r_tag, "hazard", pts_s)

# D) 4 Vertical Octagonal Corner Open-Web Steel Lattice Trusses + Vertical Strip Worklights (01_komut_110.jpg & image-3!)
for side in (-1, 1):
    # Inner pair flanking center core bay on rear bulkhead (X = +/-6.4, Y = 14.3, Z = -11..+16)
    x_in = side * 6.45
    y_in = 14.35
    for dx in (-0.32, 0.32):
        sb_crown.cyl("REAR_TRUSS_COLUMN", "frame", (x_in + dx, y_in, -11.5), (x_in + dx, y_in, 16.5), 0.11, sections=8)
    for z_step in np.arange(-11.0, 15.8, 1.85):
        sb_crown.cyl("REAR_TRUSS_WEB", "edge", (x_in - 0.32, y_in - 0.05, z_step), (x_in + 0.32, y_in - 0.05, z_step + 0.92), 0.055, sections=6)
        sb_crown.cyl("REAR_TRUSS_WEB", "edge", (x_in + 0.32, y_in - 0.05, z_step + 0.92), (x_in - 0.32, y_in - 0.05, z_step + 1.85), 0.055, sections=6)
    # Upper AND Lower vertical strip worklight fixtures on inner column (both visible in REF_REAR_FAN_ZOOM.png!)
    for z_wl, h_wl in [(11.6, 5.4), (-3.6, 4.6)]:
        sb_crown.box("CORNER_STRIP_WORKLIGHT_FRAME", "frame", (x_in, y_in - 0.22, z_wl), (0.52, 0.26, h_wl))
        sb_crown.box("CORNER_STRIP_WORKLIGHT_LENS", "worklight", (x_in, y_in - 0.36, z_wl), (0.28, 0.08, h_wl - 0.45))

    # Outer pair along rear-to-side octagonal corners (X = +/-18.2, Y = 11.8, Z = -12.2..+12.8)
    x_out = side * 18.25
    y_out = 11.85
    for dx in (-0.34, 0.34):
        sb_crown.cyl("OUTER_CORNER_TRUSS", "frame", (x_out + dx * 0.7, y_out + dx * 0.7, -12.0), (x_out + dx * 0.7, y_out + dx * 0.7, 12.6), 0.12, sections=8)
    for z_step in np.arange(-11.5, 11.8, 2.0):
        sb_crown.cyl("OUTER_CORNER_TRUSS", "edge", (x_out - 0.24, y_out - 0.24, z_step), (x_out + 0.24, y_out + 0.24, z_step + 1.0), 0.06, sections=6)
        sb_crown.cyl("OUTER_CORNER_TRUSS", "edge", (x_out + 0.24, y_out + 0.24, z_step + 1.0), (x_out - 0.24, y_out - 0.24, z_step + 2.0), 0.06, sections=6)

GLB_CROWN_PATH = EXP / "REACTOR_CROWN_DECK_AND_RADIAL_PORTS_01.glb"
crown_scene, crown_tris, crown_bytes = sb_crown.export_glb(GLB_CROWN_PATH)
print(f"[OK] {GLB_CROWN_PATH.name}: {len(crown_scene.geometry)} meshes, {crown_tris:,} tris, {crown_bytes/1e6:.2f} MB")


# ============================================================================
# 4. BUILD MODEL B: REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV03_DIAG_OPEN.glb
#    (Preserves Rev02 100%, cutting real watertight through-ports in lower slopes!)
# ============================================================================
YFRONT, YREAR = -18.0, 12.93
HATCH_Y = -2.70
SHEETLO, SHEETHI = HATCH_Y - 10.28, HATCH_Y + 10.28
RAILLO, RAILHI = HATCH_Y - 12.05, HATCH_Y + 12.05
ZOLO, ZOHI = -10.42, 10.42
SLIDELO, SLIDEHI = -4.10, 4.10
zbase, ztop, xin, xtop = 12.5, 21.5, 24.5, 17.0

def rear_y_x(ax):
    t = np.clip((ax - 16.14) / (24.5 - 16.14), 0, 1)
    return 15.48 - 2.55 * t * t * (3 - 2 * t)

def warp_corner(y, z):
    zt = np.clip((abs(z) - 12.5) / 9.0, 0, 1)
    base_x = 24.5 - 7.5 * zt
    strength = 1.0 - zt
    y0 = rear_y_x(base_x)
    t = np.clip((y - 9.7) / (y0 - 9.7), 0, 1)
    sm = t * t * (3 - 2 * t)
    inside = base_x - 3.30 * strength * sm
    y_real = y + sm * (rear_y_x(inside) - y0)
    return inside, y_real

def close_volume(vertices, front_faces, front_to_back):
    fs = list(front_faces)
    for a, b, c in front_faces:
        fs.append((front_to_back[a], front_to_back[c], front_to_back[b]))
    edges = {}
    for a, b, c in front_faces:
        for j, k in ((a, b), (b, c), (c, a)):
            p = (min(j, k), max(j, k))
            edges.setdefault(p, []).append((j, k))
    for uses in edges.values():
        if len(uses) != 1:
            continue
        a, b = uses[0]
        A, B = front_to_back[a], front_to_back[b]
        fs.extend(((a, B, b), (a, A, B)))
    g = trimesh.Trimesh(vertices=np.asarray(vertices), faces=np.asarray(fs), process=False)
    g.remove_unreferenced_vertices()
    return g

def front_y(z):
    t = np.clip((abs(z) - zbase) / (ztop - zbase), 0, 1)
    return YFRONT + 2.35 * t

def facet_x(side, z):
    t = np.clip((abs(z) - zbase) / (ztop - zbase), 0, 1)
    return side * (xin + (xtop - xin) * t)

def rear_y(z):
    return rear_y_x(abs(facet_x(1, z)))

def folded_facet_with_cutout(side, zlow, zhigh, front_push, back_push, hole_y=None, hole_z=None):
    # Grid along Y (world) and Z (world) with exact cell boundaries around the diagonal port opening!
    y_grid = [-18.0, -14.70, -8.55, 3.15, 9.30, 11.5, 13.5, 15.48]
    z_grid = sorted(set(list(np.linspace(zlow, zhigh, 9)) + (list(hole_z) if hole_z else [])))
    z_grid = [z for z in z_grid if zlow - 1e-6 <= z <= zhigh + 1e-6]

    verts, fidx, bidx, fs = [], {}, {}, []
    def get_v(yv, zv, back=False):
        D = bidx if back else fidx
        key = (round(float(yv), 5), round(float(zv), 5))
        if key not in D:
            yf = front_y(zv)
            yr = rear_y(zv)
            yc = np.clip(yv, yf, yr)
            mag, real_y = warp_corner(yc, zv)
            x = side * (mag + (back_push if back else -front_push))
            D[key] = len(verts)
            verts.append((x, real_y, zv))
        return D[key]

    for ya, yb in zip(y_grid[:-1], y_grid[1:]):
        for za, zb in zip(z_grid[:-1], z_grid[1:]):
            yc, zc = 0.5 * (ya + yb), 0.5 * (za + zb)
            if hole_y and hole_z:
                if (hole_y[0] <= yc <= hole_y[1]) and (hole_z[0] <= zc <= hole_z[1]):
                    continue
            # Skip degenerate cells clipped outside front_y..rear_y
            if yb <= front_y(zc) + 0.05 or ya >= rear_y(zc) - 0.05:
                continue
            a = get_v(ya, za, False)
            b = get_v(yb, za, False)
            c = get_v(yb, zb, False)
            d = get_v(ya, zb, False)
            fs.extend(((a, b, c), (a, c, d)) if side < 0 else ((a, c, b), (a, d, c)))
            for yk, zk in ((ya, za), (yb, za), (yb, zb), (ya, zb)):
                get_v(yk, zk, True)
    pairs = {fidx[k]: bidx[k] for k in fidx}
    return close_volume(verts, fs, pairs)

# Clone Rev02 geometry, upgrade ALL courses to the authentic 3-zone cool slate-blue / graphite / olive-taupe
# industrial iron palette of 01_komut_110.jpg (ZERO coppery brown!), and cut true lower-diagonal apertures!
rev02 = trimesh.load(EXP / "REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV02.glb", force="scene", process=False)
rev03 = trimesh.Scene()
for node in rev02.graph.nodes_geometry:
    tr, gname = rev02.graph[node]
    if "LOWER_DIAGONAL_STRUCTURAL_BLOCK" in gname or "LOWER_SLOPED_ROLLED_IRON" in gname:
        continue
    gc = rev02.geometry[gname].copy()
    uv_exist = getattr(gc.visual, "uv", None)
    if uv_exist is None or len(uv_exist) != len(gc.vertices):
        uv_exist = world_uv(gc.vertices)
    if "UPPER_SLOPED_ROLLED_IRON" in gname or "STAMPED_WAIST_COURSE_3" in gname:
        new_m = MATS["iron_upper"]
    elif "STAMPED_WAIST_COURSE_2" in gname:
        new_m = MATS["iron_mid"]
    elif "STAMPED_WAIST_COURSE_1" in gname:
        new_m = MATS["iron_lower"]
    elif "__liner" in gname or "__frame" in gname:
        new_m = MATS["frame"]
    elif "__pocket" in gname:
        new_m = MATS["pocket"]
    elif "__edge" in gname:
        new_m = MATS["edge"]
    else:
        new_m = MATS["red"]
    gc.visual = trimesh.visual.texture.TextureVisuals(uv=uv_exist, material=new_m)
    rev03.add_geometry(gc, geom_name=gname, node_name=node, transform=tr)

# Punch genuine open passage Y in [-8.55, +3.15], Z in [-21.15, -14.25] for LOWER_LEFT & LOWER_RIGHT!
DIAG_HOLE_Y = (-8.55, 3.15)
DIAG_HOLE_Z = (-21.15, -14.25)
for side in (-1, 1):
    tag = "LEFT" if side < 0 else "RIGHT"
    g_struct = folded_facet_with_cutout(side, -21.5, -12.5, 0.0, 3.22, DIAG_HOLE_Y, DIAG_HOLE_Z)
    u_s = (g_struct.vertices[:, 1] + 18.0) / 12.0 * (-1 if side < 0 else 1)
    v_s = (g_struct.vertices[:, 2] + 22.0) / 12.0
    g_struct.visual = trimesh.visual.texture.TextureVisuals(uv=np.stack((u_s, v_s), 1), material=MATS["frame"])
    nm = f"{tag}_LOWER_DIAGONAL_TRUE_PORT__liner"
    rev03.add_geometry(g_struct, geom_name=nm, node_name=nm)

    g_iron = folded_facet_with_cutout(side, -21.45, -12.55, 0.41, -0.105, DIAG_HOLE_Y, DIAG_HOLE_Z)
    u_i = (g_iron.vertices[:, 1] + 18.0) / 12.0 * (-1 if side < 0 else 1)
    v_i = (g_iron.vertices[:, 2] + 22.0) / 12.0
    g_iron.visual = trimesh.visual.texture.TextureVisuals(uv=np.stack((u_i, v_i), 1), material=MATS["iron_lower"])
    nm_i = f"{tag}_LOWER_SLOPED_ROLLED_IRON_OPEN__iron"
    rev03.add_geometry(g_iron, geom_name=nm_i, node_name=nm_i)

GLB_REV03_PATH = EXP / "REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV03_DIAG_OPEN.glb"
GLB_REV03_PATH.write_bytes(rev03.export(file_type="glb"))
rev03_ver = trimesh.load(GLB_REV03_PATH, force="scene", process=False)
rev03_tris = sum(len(m.faces) for m in rev03_ver.geometry.values())
print(f"[OK] {GLB_REV03_PATH.name}: {len(rev03_ver.geometry)} meshes, {rev03_tris:,} tris, {GLB_REV03_PATH.stat().st_size/1e6:.2f} MB")


# ============================================================================
# 5. BUILD MODEL C: OBSERVATION_WINDOW_ARMOR_FRAME_01.glb
#    (Clean rectangular 3-pane panoramic armored window at Y = -18.0..-20.6,
#     matching 01_komut_110.jpg with ZERO corner triangles blocking the glass,
#     plus recessed behind-frame spandrel collar sealing outside the octagon!)
# ============================================================================
sb_win = SceneBuilder()
YW = -19.20
YW_THICK = 2.40
WIN_X = 24.15     # Exact match to octagonal chamber inner width (+/-24.5) -> seals 100% of exterior pistons!
WIN_Z_LO = -15.60 # Panoramic landscape 3-pane aspect matching 01_komut_110.jpg!
WIN_Z_HI = 15.60
OUTER_X = 48.0    # Seals full control-room front bulkhead width
OUTER_Z_LO = -29.0
OUTER_Z_HI = 29.0

# Solid armored bulkhead wings (Left, Right, Upper Header, Lower Sill) — ZERO gap outside octagonal chamber!
for sgn in (-1, 1):
    xc = sgn * (WIN_X + (OUTER_X - WIN_X) * 0.5)
    xw = OUTER_X - WIN_X
    sb_win.box("BULKHEAD_SIDE_WING", "gunmetal", (xc, YW, 0.0), (xw, YW_THICK, OUTER_Z_HI - OUTER_Z_LO))
    sb_win.box("BULKHEAD_SIDE_CLAD", "plate", (xc, YW - YW_THICK * 0.5 - 0.08, 0.0), (xw - 0.4, 0.16, OUTER_Z_HI - OUTER_Z_LO - 0.6))
    # Dark forged steel lower kickband on control-room side (clean gunmetal, ZERO orange patch!)
    sb_win.box("BULKHEAD_KICKBAND", "frame", (xc, YW - YW_THICK * 0.5 - 0.14, WIN_Z_LO + 1.8), (xw - 0.6, 0.12, 3.4))

for z0, z1, part_tag in [(WIN_Z_HI, OUTER_Z_HI, "BULKHEAD_UPPER_HEADER"), (OUTER_Z_LO, WIN_Z_LO, "BULKHEAD_LOWER_SILL")]:
    zc, zh = 0.5 * (z0 + z1), (z1 - z0)
    sb_win.box(part_tag, "gunmetal", (0.0, YW, zc), (WIN_X * 2, YW_THICK, zh))
    sb_win.box(part_tag + "_CLAD", "plate", (0.0, YW - YW_THICK * 0.5 - 0.08, zc), (WIN_X * 2 - 0.2, 0.16, zh - 0.3))

# Heavy beveled perimeter armor window frame (100% clean rectangular aperture — NO corner triangles!)
sb_win.box("WINDOW_ARMOR_BEVEL", "frame", (0.0, YW, WIN_Z_HI - 0.36), (WIN_X * 2 + 1.2, YW_THICK + 0.65, 0.72))
sb_win.box("WINDOW_ARMOR_BEVEL", "frame", (0.0, YW, WIN_Z_LO + 0.36), (WIN_X * 2 + 1.2, YW_THICK + 0.65, 0.72))
for sgn in (-1, 1):
    sb_win.box("WINDOW_ARMOR_BEVEL", "frame", (sgn * (WIN_X - 0.36), YW, 0.0), (0.72, YW_THICK + 0.65, (WIN_Z_HI - WIN_Z_LO) + 1.2))
    # Two slim side mullions at X = +/-13.95 (exact 01_komut_110.jpg 3-pane proportions!)
    sb_win.box("WINDOW_SIDE_MULLION", "frame", (sgn * 13.95, YW - 0.25, 0.0), (0.56, 1.35, WIN_Z_HI - WIN_Z_LO - 0.3))
    sb_win.cyl("WINDOW_MULLION_TRIM", "edge", (sgn * 13.95, YW - 0.96, WIN_Z_LO + 0.3), (sgn * 13.95, YW - 0.96, WIN_Z_HI - 0.3), 0.065, sections=8)

# Exterior-only spandrel seal BEHIND the octagonal sloped edges at Y = -16.8..-18.0 (strictly OUTSIDE the octagon,
# so through the clean rectangular glass corner you see dark recessed industrial housing instead of empty void!)
for sgn_x in (-1, 1):
    for sgn_z in (-1, 1):
        # At Z = 12.5, octagon X = 24.5; at Z = 21.5, octagon X = 17.0. Seal ONLY outside the octagon!
        tri_v = np.array([
            [sgn_x * 24.6, -18.0, sgn_z * 12.5],
            [sgn_x * 24.6, -18.0, sgn_z * 21.6],
            [sgn_x * 16.9, -18.0, sgn_z * 21.6],
            [sgn_x * 24.6, -15.6, sgn_z * 12.5],
            [sgn_x * 24.6, -15.6, sgn_z * 21.6],
            [sgn_x * 16.9, -15.6, sgn_z * 21.6],
        ], float)
        if sgn_x * sgn_z > 0:
            tri_f = [[0, 1, 2], [3, 5, 4], [0, 3, 4], [0, 4, 1], [1, 4, 5], [1, 5, 2], [2, 5, 3], [2, 3, 0]]
        else:
            tri_f = [[0, 2, 1], [3, 4, 5], [0, 4, 3], [0, 1, 4], [1, 5, 4], [1, 2, 5], [2, 3, 5], [2, 0, 3]]
        sb_win.add("EXTERIOR_SPANDREL_SEAL", "dark", trimesh.Trimesh(vertices=tri_v, faces=tri_f, process=False))

GLB_WIN_PATH = EXP / "OBSERVATION_WINDOW_ARMOR_FRAME_01.glb"
win_scene, win_tris, win_bytes = sb_win.export_glb(GLB_WIN_PATH)
print(f"[OK] {GLB_WIN_PATH.name}: {len(win_scene.geometry)} meshes, {win_tris:,} tris, {win_bytes/1e6:.2f} MB")


# ============================================================================
# 6. RENDER 6-PANEL HIGH-RES TRUE-MESH PBR APPROVAL SHEET
# ============================================================================
rear_glb = trimesh.load(EXP / "REACTOR_REAR_BULKHEAD_IRON_REV04.glb", force="scene", process=False)
grille_glb = trimesh.load(EXP / "REACTOR_REAR_SERVICE_GRILLES_01.glb", force="scene", process=False)
emitter_glb = trimesh.load(EXP / "REACTOR_EMITTER_REV03.glb", force="scene", process=False)
piston_glb = trimesh.load(EXP / "REACTOR_PISTON_GUIDE_01.glb", force="scene", process=False)
hatch_closed_glb = trimesh.load(EXP / "REACTOR_WALL_HATCH_THROUGH_01.glb", force="scene", process=False)
hatch_open_glb = trimesh.load(EXP / "REACTOR_WALL_HATCH_OPEN_INSPECTION_01.glb", force="scene", process=False)

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

def assemble_full_chamber(deployed=False, include_window=True):
    sc = trimesh.Scene()
    slide = 1.0 if deployed else 0.0
    stroke = 1.0 if deployed else 0.0
    place_scene(sc, crown_scene, "NEW_CROWN_DECK", hatch_slide=slide)
    place_scene(sc, rev03_ver, "REV03_SIDE_DIAG")
    place_scene(sc, rear_glb, "APPROVED_REAR")
    place_scene(sc, grille_glb, "APPROVED_GRILLES")
    if include_window:
        place_scene(sc, win_scene, "NEW_WINDOW_FRAME")

    radial_sites = [
        ("UPPER",       (0.0, 0.0, 1.0)),
        ("LEFT",        (-1.0, 0.0, 0.0)),
        ("RIGHT",       (1.0, 0.0, 0.0)),
        ("LOWER_LEFT",  (-0.72, 0.0, -0.694)),
        ("LOWER_RIGHT", (0.72, 0.0, -0.694)),
        ("LOWER",       (0.0, 0.0, -1.0)),
    ]
    for label, dir0 in radial_sites:
        d = np.asarray(dir0, float)
        d /= np.linalg.norm(d)
        R = rot_from_out(d)
        em_r = 16.17 if deployed else 35.97
        T_em = R.copy()
        T_em[:3, 3] = np.array([0.0, -2.70, 0.0]) + d * em_r
        place_scene(sc, emitter_glb, f"EMITTER_{label}", T_em)

        T_pi = R.copy()
        T_pi[:3, 3] = np.array([0.0, -2.70, 0.0]) + d * 24.50
        place_scene(sc, piston_glb, f"PISTON_{label}", T_pi, piston_stroke=stroke)

        if label in ("LEFT", "RIGHT"):
            h_src = hatch_open_glb if deployed else hatch_closed_glb
            place_scene(sc, h_src, f"SIDE_HATCH_{label}", T_pi)
    return sc

def cam_pose(eye, target):
    eye = np.asarray(eye, float)
    target = np.asarray(target, float)
    f = target - eye
    f /= np.linalg.norm(f)
    r = np.cross(f, (0.0, 0.0, 1.0))
    r /= np.linalg.norm(r)
    up = np.cross(r, f)
    T = np.eye(4)
    T[:3, :3] = np.stack((r, up, -f), axis=1)
    T[:3, 3] = eye
    return T

def render_view(sc: trimesh.Scene, eye, target, fov=62, w=920, h=560):
    ps = pyrender.Scene.from_trimesh_scene(sc, bg_color=[0.025, 0.030, 0.042, 1.0], ambient_light=[0.22, 0.24, 0.28])
    lights = [
        ((0.0, -48.0, 6.0),   (0.88, 0.92, 1.00), 620.0),
        ((-18.0, -14.0, 16.0),(0.82, 0.89, 1.00), 360.0),
        ((18.0, -14.0, 16.0), (0.82, 0.89, 1.00), 360.0),
        ((0.0, 3.0, 14.0),    (0.85, 0.90, 1.00), 280.0),
        ((0.0, -6.0, -14.0),  (0.76, 0.84, 0.98), 260.0),
        ((-26.0, -6.0, -18.0),(0.90, 0.78, 0.68), 180.0),
        ((26.0, -6.0, -18.0), (0.90, 0.78, 0.68), 180.0),
    ]
    for loc, rgb, intens in lights:
        lp = np.eye(4)
        lp[:3, 3] = loc
        ps.add(pyrender.PointLight(color=np.array(rgb), intensity=intens), pose=lp)
    ps.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)), pose=cam_pose(eye, target))
    renderer = pyrender.OffscreenRenderer(w, h)
    rgba, _ = renderer.render(ps, flags=pyrender.RenderFlags.RGBA)
    renderer.delete()
    return Image.fromarray(rgba, "RGBA").convert("RGB")

sc_cold_win = assemble_full_chamber(deployed=False, include_window=True)
sc_open_win = assemble_full_chamber(deployed=True, include_window=True)
sc_open_inside = assemble_full_chamber(deployed=True, include_window=False)

im_cold = render_view(sc_cold_win, (0.0, -54.0, -3.0), (0.0, 2.0, -0.5), fov=52)
im_open = render_view(sc_open_win, (0.0, -54.0, -3.0), (0.0, 2.0, -0.5), fov=52)
im_up_oblique = render_view(sc_open_inside, (-19.5, -17.5, -10.0), (4.0, 4.0, 11.5), fov=66)
im_low_oblique = render_view(sc_open_inside, (-18.5, -17.0, 12.5), (4.5, 4.0, -12.5), fov=66)
im_diag_back = render_view(sc_open_inside, (-36.0, -16.0, -28.0), (-14.0, -2.7, -14.0), fov=58)
im_ref = Image.open(ROOT / "reactor_startup/reference/01_komut_110.jpg").convert("RGB")

board = Image.new("RGB", (1920, 1380), (13, 17, 25))
draw = ImageDraw.Draw(board)
bold_p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
reg_p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f_title = ImageFont.truetype(bold_p, 28)
f_sub = ImageFont.truetype(reg_p, 17)
f_lbl = ImageFont.truetype(bold_p, 13)

draw.text((32, 18), "FAZ 2 PAKET A — SEKİZGEN TAVAN/ZEMİN, 4 RADYAL KAPAKLI YUVA & ZIRHLI GÖZLEM PENCERESİ (ÖN-İZLEME)", font=f_title, fill=(242, 246, 252))
draw.text((32, 56), "Onaylı 7 GLB korundu • Tavan/zemin/yan duvar aynı paslı-demir PBR ailesinde • 6 başlığın 6'sı da gerçek sürgülü kapaklı deliklerden çıkar • Dış pistonlar camdan görünmez.", font=f_sub, fill=(176, 194, 216))

panels = [
    (im_cold,        30,  96, 600, 385, "1) COLD POZU (Pencereden) • 6 Kapak Kapalı + 3 Bölmeli Dikdörtgen Zırhlı Cam"),
    (im_open,       660,  96, 600, 385, "2) DEPLOYED POZU (Pencereden) • 6 Sürgülü Kapak Açık + 6 Yayıcı Rijit İleride"),
    (im_ref,       1290,  96, 600, 385, "3) REFERANS 1280×1024 (01_komut_110) • 3 Bölmeli Cam, Kirişler, Alt Radyatörler"),
    (im_up_oblique,  30, 505, 600, 385, "4) İÇ AÇI ÜST • Sekizgen Tavan, Beyaz Konturlar, SL-00 Sürgülü Kapak & Kirişler"),
    (im_low_oblique,660, 505, 600, 385, "5) İÇ AÇI ALT • Gömme 43.9° Çapraz Kapaklar, SL-05 Alt Kapak & Radyatörler"),
    (im_diag_back, 1290, 505, 600, 385, "6) DIŞ/ARKA TEKNİK KESİT • Rev03 Alt Çaprazda Gerçek Delik (Arkası Açık)"),
]

for im, x, y, w, h, cap in panels:
    contained = ImageOps.contain(im, (w - 6, h - 40), Image.Resampling.LANCZOS)
    board.paste(contained, (x + (w - contained.width) // 2, y + 34 + (h - 37 - contained.height) // 2))
    draw.rectangle((x, y, x + w, y + h), outline=(66, 84, 108), width=2)
    draw.rectangle((x, y, x + w, y + 32), fill=(22, 29, 42))
    draw.text((x + 10, y + 7), cap, font=f_lbl, fill=(238, 244, 252))

# Summary footer box
draw.rectangle((30, 915, 1890, 1350), fill=(18, 24, 35), outline=(58, 76, 98), width=2)
summary_lines = [
    "ÜRETİLEN 3B GLB DOSYALARI (Henüz Roblox Studio'ya KURULMADI — Kullanıcı Onayı Bekliyor):",
    f"  • REACTOR_CROWN_DECK_AND_RADIAL_PORTS_01.glb ({len(crown_scene.geometry)} mesh, {crown_tris:,} üçgen, {crown_bytes/1e6:.2f} MB):",
    "      - Kademeli sekizgen tavan (ROOF_*) + beyaz gömme ışık konturları + alt çukur tabanı (DECK_*) + alt ızgaralı radyatör bankları (//// ikaz şeritli).",
    "      - 4 adet köşe çelik kafes kiriş (REAR_TRUSS_COLUMN / OUTER_CORNER_TRUSS) ve dikey köşe çalışma lambası yuvaları.",
    "      - UPPER (SL-00), LOWER (SL-05), LOWER_LEFT (SL-03) ve LOWER_RIGHT (SL-04) için gerçek açık geçişli zırhlı yuvalar + 8 ayrı sürgülü kapak (HATCH_LEFT / HATCH_RIGHT).",
    f"  • REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV03_DIAG_OPEN.glb ({len(rev03_ver.geometry)} mesh, {rev03_tris:,} üçgen, {GLB_REV03_PATH.stat().st_size/1e6:.2f} MB):",
    "      - Onaylı Rev02 paslı-demir yan duvarın birebir malzemesi/UV'si korunarak yalnızca alt 43.9° çapraz bloklara gerçek geçiş deliği açıldı (yayıcılar sacın içinden doğmaz).",
    f"  • OBSERVATION_WINDOW_ARMOR_FRAME_01.glb ({len(win_scene.geometry)} mesh, {win_tris:,} üçgen, {win_bytes/1e6:.2f} MB):",
    "      - Kontrol odası ile sekizgen reaktör ağzını birleştiren 3 bölmeli panoramik zırhlı pencere çerçevesi + dış pistonları gizleyen yan zırh kanatları (orta görüş tamamen açık).",
    "",
    "ONAY SONRASI SONRAKİ ADIM: Onay verirseniz Studio için Y-up dönüşümlü paketi hazırlayıp 6 kapak çiftinin tamamını (12 sürgülü kanat) sunucu animasyonuna bağlayacağız.",
]
cy = 932
for idx_l, line in enumerate(summary_lines):
    ft = f_lbl if idx_l == 0 or idx_l == len(summary_lines) - 1 else f_sub
    col = (245, 214, 138) if idx_l == 0 else ((162, 232, 198) if idx_l == len(summary_lines) - 1 else (210, 222, 236))
    draw.text((48, cy), line, font=ft, fill=col)
    cy += 36

PREVIEW_PATH = EXP / "FAZ2_PAKET_A_ODA_VE_4_YUVA_ONAY.png"
board.save(PREVIEW_PATH, optimize=True)
print(f"[OK] Preview saved: {PREVIEW_PATH} ({PREVIEW_PATH.stat().st_size/1e6:.2f} MB)")
