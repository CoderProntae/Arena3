#!/usr/bin/env python3
"""GECICI TEST MODELI — Kriyo Basinc Regulator Istasyonu (referans esinli, ozgun).

Ayni uretim hatti: prosedurel PBR doku (numpy/PIL), (bolge, materyal) gruplari,
ZONE__mat adli gercek ucgen meshler, ici delik boru kabuklari, pyrender onay panosu.
Yazar uzayi: X yatay, Y derinlik (on yuz -Y), Z yukseklik. 1 birim = 1 stud.
Bu model hicbir onayli GLB'nin yerine gecmez; Studio'ya yazilmadi.
"""
from __future__ import annotations
import os, sys, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageChops

os.environ['PYOPENGL_PLATFORM'] = 'egl'
sys.path[:0] = ['/home/user/.cache/modeldeps', '/home/user/.cache/modelrender']
import pyglet; pyglet.options['headless'] = True  # EGL headless; viewer hic kullanilmaz
import trimesh, pyrender

ROOT = Path('/home/user')
OUT = ROOT / 'model_exports'; OUT.mkdir(exist_ok=True)
DBG = ROOT / '.cache/model_debug'; DBG.mkdir(parents=True, exist_ok=True)
TAU = math.tau

# ---------------------------------------------------------------- dokular
rng = np.random.default_rng(4242); W = H = 1024
co = np.asarray(Image.fromarray(rng.integers(0, 256, (48, 48), dtype=np.uint8), 'L').resize((W, H), Image.Resampling.BICUBIC), float) - 128
mid = np.asarray(Image.fromarray(rng.integers(0, 256, (220, 220), dtype=np.uint8), 'L').resize((W, H), Image.Resampling.BILINEAR), float) - 128
speck = rng.standard_normal((H, W)) * 3.0
mix = np.clip(.5 + .30 * np.tanh(co / 40) + .18 * np.tanh(mid / 34), .12, .88)
# Faz2 kalibreli soguk palet: ust arduvaz (101,113,134), grafit (74,79,94), dipte zeytuni (72,69,61)
img = mix[:, :, None] * np.array((101., 113., 134.)) + (1 - mix)[:, :, None] * np.array((74., 79., 94.))
olive_w = np.clip(np.linspace(0, 1, H)[:, None, None] ** 3 * .35, 0, .35)
img = img * (1 - olive_w) + np.array((72., 69., 61.)) * olive_w
img += speck[:, :, None]
pits = rng.random((H, W)) < .012; img[pits] -= rng.uniform(6, 26, pits.sum())[:, None]
TEX_SLATE = Image.fromarray(np.uint8(np.clip(img, 3, 250)), 'RGB')
height = mid * .27 + speck * .8
hgy, hgx = np.gradient(height)
nx, ny, nz = -hgx * .028, -hgy * .028, np.ones((H, W))
nrm = np.sqrt(nx * nx + ny * ny + nz * nz)
NORM_SLATE = Image.fromarray(np.uint8(np.clip((np.stack((nx / nrm, ny / nrm, nz / nrm), 2) * .5 + .5) * 255, 0, 255)), 'RGB')
mr = np.empty((H, W, 3), dtype=np.uint8); mr[:, :, 0] = 255
mr[:, :, 1] = np.uint8(np.clip((.62 - .18 * mix + np.maximum(speck, 0) * .003) * 255, 1, 255))
mr[:, :, 2] = np.uint8(np.clip((.55 + .30 * mix) * 255, 1, 255))
MR_SLATE = Image.fromarray(mr, 'RGB')

def font(size, bold=True):
    p = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    try: return ImageFont.truetype(p, size)
    except OSError: return ImageFont.load_default()

def gauge_texture(needle_frac, label):
    S = 512; c = S // 2
    im = Image.new('RGB', (S, S), (233, 230, 218)); d = ImageDraw.Draw(im)
    d.ellipse((8, 8, S - 8, S - 8), outline=(38, 44, 54), width=10)
    start, sweep = 135.0, 270.0  # PIL arc: 0=east, saat yonu
    d.arc((52, 52, S - 52, S - 52), start + sweep * .8, start + sweep, fill=(198, 48, 38), width=26)
    for i in range(41):
        fr = i / 40; a = math.radians(135 + 270 * fr)  # matematiksel aci (y asagi tersinecek)
        big = (i % 5 == 0); r1 = 168 if big else 184; r2 = 202
        x1, y1 = c + r1 * math.cos(a), c + r1 * math.sin(a)
        x2, y2 = c + r2 * math.cos(a), c + r2 * math.sin(a)
        d.line((x1, y1, x2, y2), fill=(30, 36, 46), width=7 if big else 3)
        if big:
            tx, ty = c + 128 * math.cos(a), c + 128 * math.sin(a)
            d.text((tx, ty), str(int(fr * 8)), font=font(44), fill=(30, 36, 46), anchor='mm')
    a = math.radians(135 + 270 * needle_frac)
    d.line((c, c, c + 150 * math.cos(a), c + 150 * math.sin(a)), fill=(198, 48, 38), width=13)
    d.ellipse((c - 24, c - 24, c + 24, c + 24), fill=(38, 44, 54))
    d.text((c, c + 118), label, font=font(40), fill=(58, 66, 78), anchor='mm')
    d.text((c, c + 162), 'x100 PSI', font=font(30, False), fill=(110, 116, 126), anchor='mm')
    return im

def plate_texture():
    im = Image.new('RGB', (1024, 256), (20, 26, 36)); d = ImageDraw.Draw(im)
    d.rectangle((10, 10, 1013, 245), outline=(148, 160, 175), width=6)
    d.text((512, 66), 'TEST-01', font=font(84), fill=(238, 242, 248), anchor='mm')
    d.text((512, 150), 'KRİYO BASINÇ REGÜLATÖRÜ', font=font(52), fill=(172, 198, 222), anchor='mm')
    d.text((512, 212), 'GEÇİCİ TEST MODELİ', font=font(36, False), fill=(97, 214, 226), anchor='mm')
    return im

def hazard_texture():
    S = 256; im = Image.new('RGB', (S, S), (24, 24, 26)); d = ImageDraw.Draw(im)
    for k in range(-4, 10):
        d.polygon([(k * 64, S), (k * 64 + 32, S), (k * 64 + 32 + S, 0), (k * 64 + S, 0)], fill=(214, 164, 32))
    return im

def pmat(name, rgb=None, met=.6, rough=.55, tex=None, mrr=None, norm=None, emission=(0, 0, 0)):
    return trimesh.visual.material.PBRMaterial(
        name=name, baseColorFactor=[*((255, 255, 255) if tex is not None else rgb), 255],
        baseColorTexture=tex, metallicFactor=met, roughnessFactor=rough,
        metallicRoughnessTexture=mrr, normalTexture=norm,
        emissiveFactor=list(emission), doubleSided=True)

MAT = {
    'slate':  pmat('01 - Soguk arduvaz/grafit dokulu demir', met=1., rough=1., tex=TEX_SLATE, mrr=MR_SLATE, norm=NORM_SLATE),
    'gunmetal': pmat('02 - Weathered gunmetal', (36, 42, 47), .71, .62),
    'rib':    pmat('03 - Forged dark support iron', (48, 53, 59), .79, .55),
    'edge':   pmat('04 - Worn steel edges', (158, 166, 174), .76, .36),
    'pipe':   pmat('05 - Brushed pipe steel', (112, 122, 132), .75, .42),
    'soot':   pmat('06 - Crevice and bore', (6, 9, 12), .32, .88),
    'orange': pmat('07 - Safety enamel', (198, 92, 34), .35, .55),
    'hazard': pmat('08 - Hazard stripe enamel', met=.25, rough=.6, tex=hazard_texture()),
    'gauge_a': pmat('09 - Gauge face A', met=.02, rough=.38, tex=gauge_texture(.38, 'COOLANT')),
    'gauge_b': pmat('10 - Gauge face B', met=.02, rough=.38, tex=gauge_texture(.66, 'MANIFOLD')),
    'plate':  pmat('11 - Engraved nameplate', met=.3, rough=.5, tex=plate_texture()),
    'lamp_r': pmat('12 - Red status lens', (150, 30, 26), .05, .3, emission=(.55, .03, .02)),
    'lamp_a': pmat('13 - Amber status lens', (196, 120, 22), .05, .3, emission=(.55, .22, .01)),
    'lamp_m': pmat('14 - Mint status lens', (40, 150, 96), .05, .3, emission=(.03, .45, .18)),
    'cyan':   pmat('15 - Cyan indicator', (23, 140, 190), .06, .3, emission=(.01, .3, .6)),
    'rubber': pmat('16 - Cable rubber', (14, 16, 18), .1, .85),
}
SPECIAL_UV = {'gauge_a', 'gauge_b', 'plate', 'hazard'}
BUCKET = {}

def add(zone, mat, mesh):
    v = np.asarray(mesh.vertices, float); f = np.asarray(mesh.faces)
    if mat in SPECIAL_UV and getattr(mesh.visual, 'uv', None) is not None:
        uv = np.asarray(mesh.visual.uv, float)
    elif mat == 'slate':
        uv = np.stack(((v[:, 0] + 6) / 12, v[:, 2] / 14), axis=1)
    else:
        uv = np.zeros((len(v), 2))
    BUCKET.setdefault((zone, mat), []).append((v, f, uv))

def box(zone, mat, cx, cy, cz, sx, sy, sz, rotx=0.0):
    g = trimesh.creation.box(extents=(sx, sy, sz))
    if rotx:
        g.apply_transform(trimesh.transformations.rotation_matrix(rotx, [1, 0, 0], [0, 0, 0]))
    g.apply_translation((cx, cy, cz)); add(zone, mat, g)

def bar(zone, mat, a, b, r, sections=12):
    a = np.asarray(a, float); b = np.asarray(b, float); d = b - a; L = np.linalg.norm(d)
    if L < 1e-4: return
    g = trimesh.creation.cylinder(radius=r, height=L, sections=sections)
    g.apply_transform(trimesh.geometry.align_vectors((0, 0, 1), d / L))
    g.apply_translation((a + b) * .5); add(zone, mat, g)

def nut(zone, mat, center, axis=(0, 0, 1), r=.13, h=.11):
    g = trimesh.creation.cylinder(radius=r, height=h, sections=6)
    g.apply_transform(trimesh.geometry.align_vectors((0, 0, 1), np.asarray(axis, float)))
    g.apply_translation(center); add(zone, mat, g)

def shell_x(outer, inner, n=48):
    """Emitter usulu: X ekseninde ici delik profil kabugu."""
    contour = list(outer) + list(reversed(inner)); verts = []
    for (x, r) in contour:
        for j in range(n):
            th = TAU * j / n; verts.append((x, r * math.cos(th), r * math.sin(th)))
    faces = []; ln = len(contour)
    for k in range(ln):
        q = (k + 1) % ln
        for j in range(n):
            j1 = (j + 1) % n; a = k * n + j; b = k * n + j1; c = q * n + j; d = q * n + j1
            faces.extend(((a, b, c), (b, d, c)))
    return trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces), process=False)

def tube(zone, mat, pts, r, sections=12, closed=False, cap=True):
    """Nokta dizisi boyunca paralel tasiyici cerceve ile tup sar."""
    P = [np.asarray(p, float) for p in pts]
    rings = len(P) if not closed else len(P)
    frames = []; tangents = []
    for i in range(rings):
        i0 = (i - 1) % len(P) if closed else max(i - 1, 0)
        i1 = (i + 1) % len(P) if closed else min(i + 1, len(P) - 1)
        t = P[i1] - P[i0]; t /= np.linalg.norm(t); tangents.append(t)
    n0 = np.array([0., 0., 1.])
    if abs(np.dot(n0, tangents[0])) > .9: n0 = np.array([1., 0., 0.])
    n0 = n0 - tangents[0] * np.dot(n0, tangents[0]); n0 /= np.linalg.norm(n0)
    verts = []; N = n0
    for i in range(rings):
        t = tangents[i]; N = N - t * np.dot(N, t)
        if np.linalg.norm(N) < 1e-6: N = np.cross(t, [1., 0., 0.])
        N = N / np.linalg.norm(N); B = np.cross(t, N)
        for j in range(sections):
            th = TAU * j / sections
            verts.append(P[i] + r * (math.cos(th) * N + math.sin(th) * B))
        N = N.copy()
    faces = []; rr = rings if closed else rings - 1
    for i in range(rr):
        i2 = (i + 1) % rings
        for j in range(sections):
            j2 = (j + 1) % sections
            a = i * sections + j; b = i * sections + j2; c = i2 * sections + j; d = i2 * sections + j2
            faces.extend(((a, b, c), (b, d, c)))
    if cap and not closed:
        base = len(verts); verts.append(P[0]); verts.append(P[-1])
        for j in range(sections):
            j2 = (j + 1) % sections
            faces.append((base, j2, j))
            a = (rings - 1) * sections + j; b = (rings - 1) * sections + j2
            faces.append((base + 1, a, b))
    add(zone, mat, trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces), process=False))

def bezier(p0, p1, p2, n=10):
    p0, p1, p2 = map(lambda v: np.asarray(v, float), (p0, p1, p2))
    return [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2 for t in np.linspace(0, 1, n)]

def disc(zone, mat, cx, cy, cz, r, nseg=40):
    """On yuze (-Y) bakan, dokulu daire yuzu."""
    verts = [(cx, cy, cz)]; uvs = [(.5, .5)]; faces = []
    for j in range(nseg):
        th = TAU * j / nseg
        verts.append((cx + r * math.cos(th), cy, cz + r * math.sin(th)))
        uvs.append((.5 + .5 * math.cos(th), .5 + .5 * math.sin(th)))
    for j in range(nseg):
        j2 = (j + 1) % nseg; faces.append((0, 1 + j2, 1 + j))
    g = trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces), process=False)
    g.visual = trimesh.visual.texture.TextureVisuals(uv=np.array(uvs))
    add(zone, mat, g)

def quad(zone, mat, cx, cy, cz, w, h):
    """On yuze bakan dokulu duz plaka yuzeyi."""
    x0, x1, z0, z1 = cx - w / 2, cx + w / 2, cz - h / 2, cz + h / 2
    verts = np.array([(x0, cy, z0), (x1, cy, z0), (x1, cy, z1), (x0, cy, z1)], float)
    faces = np.array([(0, 1, 2), (0, 2, 3)])
    g = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
    g.visual = trimesh.visual.texture.TextureVisuals(uv=np.array([(0, 0), (1, 0), (1, 1), (0, 1)], float))
    add(zone, mat, g)

# ---------------------------------------------------------------- geometri
FRONT = -1.60  # kabin on yuzu
# Kaide: iki kademeli plint + ankraj somunlari + on ikaz seridi
box('PLINTH', 'rib', 0, 0, .35, 10.4, 4.8, .7)
box('PLINTH', 'gunmetal', 0, 0, .85, 9.4, 4.1, .34)
box('PLINTH', 'gunmetal', 0, -2.38, .62, 10.44, .1, .5)
for sx in (-4.6, -2.3, 2.3, 4.6):
    for sy in (-1.8, 1.8): nut('PLINTH', 'edge', (sx, sy, .76))
# Kabin govdesi: ana kutu + tavan kapagi + kose dikmeleri + yatay dikişler
box('CABINET', 'slate', 0, .15, 5.1, 8.4, 3.5, 8.2)
box('CABINET', 'gunmetal', 0, .1, 9.36, 8.9, 3.9, .34)
box('CABINET', 'gunmetal', 0, .15, 1.12, 8.7, 3.75, .3)
for sx in (-4.12, 4.12):
    for sy in (-1.5, 1.8): box('CABINET', 'rib', sx, sy, 5.1, .34, .34, 7.9)
for z in (3.2, 6.6): box('CABINET', 'soot', 0, FRONT - .03, z, 8.44, .08, .09)
# Yan yuzlerde gomme paneller + kucuk menfez citalari
for sx, sgn in ((-4.21, -1), (4.21, 1)):
    box('CABINET', 'gunmetal', sx, .15, 5.6, .08, 2.4, 4.6)
    for i in range(5):
        box('VENT', 'rib', sx + sgn * .10, .15, 4.2 + i * .62, .12, 1.9, .3, rotx=.0)
# On panel cercevesi (sol) + plaka
box('FRONT_PANEL', 'gunmetal', -1.6, FRONT - .08, 6.5, 4.2, .16, 3.9)
box('FRONT_PANEL', 'rib', -1.6, FRONT - .15, 6.5, 3.9, .1, 3.6)
for sx in (-3.45, .25):
    for sz in (4.85, 8.15): nut('FRONT_PANEL', 'edge', (sx, FRONT - .22, sz), axis=(0, 1, 0), r=.1, h=.09)
# Iki manometre
for zone, mat, cx in (('GAUGE_LEFT', 'gauge_a', -2.55), ('GAUGE_RIGHT', 'gauge_b', -.65)):
    bar(zone, 'edge', (cx, FRONT - .12, 7.35), (cx, FRONT - .5, 7.35), .88, sections=36)
    bar(zone, 'soot', (cx, FRONT - .5, 7.35), (cx, FRONT - .55, 7.35), .80, sections=36)
    disc(zone, mat, cx, FRONT - .56, 7.35, .78)
    bar(zone, 'pipe', (cx, FRONT - .3, 6.45), (cx, FRONT - .3, 5.8), .07)
# Direksiyon valf (handwheel): halka tup + 4 kol + gobek + cevirme sapı
WX, WY, WZ, WR = -1.6, FRONT - .95, 3.05, 1.5
ring = [(WX + WR * math.cos(TAU * j / 40), WY, WZ + WR * math.sin(TAU * j / 40)) for j in range(40)]
tube('HANDWHEEL', 'gunmetal', ring, .115, sections=12, closed=True)
for j in range(4):
    th = TAU * j / 4 + .4
    bar('HANDWHEEL', 'gunmetal', (WX, WY, WZ), (WX + WR * math.cos(th), WY, WZ + WR * math.sin(th)), .07)
bar('HANDWHEEL', 'edge', (WX, WY + .25, WZ), (WX, WY - .25, WZ), .2, sections=18)
bar('HANDWHEEL', 'pipe', (WX, FRONT, WZ), (WX, WY + .2, WZ), .12, sections=14)
hx, hz = WX + WR * math.cos(2.25), WZ + WR * math.sin(2.25)
bar('HANDWHEEL', 'orange', (hx, WY - .05, hz), (hx, WY - .55, hz), .1, sections=12)
# Sag on: panjur bolmesi + isim plakasi + kol
box('VENT', 'gunmetal', 2.25, FRONT - .08, 6.7, 3.1, .16, 3.1)
for i in range(5):
    box('VENT', 'rib', 2.25, FRONT - .2, 5.65 + i * .52, 2.6, .12, .3, rotx=-.65)
box('NAMEPLATE', 'gunmetal', 2.25, FRONT - .09, 4.35, 3.0, .14, .95)
quad('NAMEPLATE', 'plate', 2.25, FRONT - .17, 4.35, 2.9, .85)
quad('PLINTH', 'hazard', 0, -2.44, .62, 10.44, .5)
for sx in (.95, 3.55):
    for sz in (3.98, 4.72): nut('NAMEPLATE', 'edge', (sx, FRONT - .18, sz), axis=(0, 1, 0), r=.07, h=.07)
bar('LEVER', 'edge', (2.25, FRONT - .1, 2.3), (2.25, FRONT - .5, 2.3), .22, sections=16)
bar('LEVER', 'pipe', (2.25, FRONT - .5, 2.3), (2.95, FRONT - .62, 3.15), .075)
g = trimesh.creation.icosphere(subdivisions=2, radius=.17); g.apply_translation((2.95, FRONT - .62, 3.15)); add('LEVER', 'orange', g)
# Kucuk cyan gosterge lambalari (plaka ustu)
for i, cx in enumerate((1.45, 1.95, 2.45)):
    disc('FRONT_PANEL', 'cyan', cx, FRONT - .18, 4.98, .09, nseg=20)
# Ust manifold: gercek delikli yatay boru + flanslar + uclarda somunlar
MZ, MY = 10.15, .95
m = shell_x([(-4.7, .56), (-4.45, .60), (4.45, .60), (4.7, .56)], [(-4.7, .40), (4.7, .40)])
m.apply_translation((0, MY, MZ)); add('MANIFOLD', 'pipe', m)
for xe in (-4.55, 4.55):
    f = shell_x([(-.14, .86), (.14, .86)], [(-.14, .40), (.14, .40)], n=36)
    f.apply_translation((xe, MY, MZ)); add('MANIFOLD', 'edge', f)
    for j in range(8):
        th = TAU * j / 8
        nut('MANIFOLD', 'gunmetal', (xe + (.17 if xe > 0 else -.17), MY + .70 * math.cos(th), MZ + .70 * math.sin(th)), axis=(1, 0, 0), r=.085, h=.09)
bar('MANIFOLD', 'pipe', (1.2, MY, MZ + .55), (1.2, MY, MZ + 1.15), .1)
g = trimesh.creation.icosphere(subdivisions=2, radius=.16); g.apply_translation((1.2, MY, MZ + 1.22)); add('MANIFOLD', 'cyan', g)
# Iki inis borusu (dirsekli, tup yolu)
for sgn in (-1, 1):
    pts = [np.array([sgn * 4.45, MY, MZ])] + bezier((sgn * 4.45, MY, MZ), (sgn * 4.9, MY, MZ), (sgn * 4.9, MY, MZ - 1.1), 8)[1:] + \
          [np.array([sgn * 4.9, MY, 9.2]), np.array([sgn * 4.9, MY, 8.0])]
    tube('PIPES', 'pipe', pts, .42, sections=20)
    f = shell_x([(-.6, .52), (.6, .52)], [(-.6, .43), (.6, .43)], n=24)
    f.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-90), [0, 1, 0]))
    f.apply_translation((sgn * 4.9, MY, 8.55)); add('PIPES', 'edge', f)
# Iki akumulator sisesi (X profili -> Z'ye cevrildi) + boyun vanalari + kelepceler
for zone, cx in (('BOTTLE_A', -2.7), ('BOTTLE_B', -.9)):
    prof = [(0, .58), (.25, .79), (.9, .85), (2.0, .85), (2.7, .62), (3.05, .3), (3.2, .16)]
    inner = [(0, 0.01), (3.2, .05)]
    b = shell_x(prof, inner, n=36)
    b.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-90), [0, 1, 0]))
    b.apply_translation((cx, .95, 9.62)); add(zone, 'slate', b)
    bar(zone, 'gunmetal', (cx, .95, 9.5), (cx, .95, 9.72), .94, sections=28)
    bar(zone, 'pipe', (cx, .95, 12.68), (cx, .95, 13.0), .14)
    bar(zone, 'edge', (cx - .3, .95, 13.0), (cx + .3, .95, 13.0), .07)
    for cz in (10.3, 11.7):
        k = shell_x([(-.09, .9), (.09, .9)], [(-.09, .84), (.09, .84)], n=36)
        k.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-90), [0, 1, 0]))
        k.apply_translation((cx, .95, cz)); add(zone, 'gunmetal', k)
    tube(zone, 'pipe', bezier((cx, .95, 12.8), (cx, 1.7, 11.8), (cx, 1.85, 10.2), 10), .11, sections=12)
# Durum lamba kulesi (sag ust)
box('LAMP_STACK', 'gunmetal', 3.55, .9, 10.5, .9, .8, 2.3)
box('LAMP_STACK', 'rib', 3.55, .9, 11.76, 1.0, .9, .22)
for cz, mat in ((11.25, 'lamp_r'), (10.5, 'lamp_a'), (9.75, 'lamp_m')):
    bar('LAMP_STACK', 'soot', (3.55, .48, cz), (3.55, .42, cz), .3, sections=20)
    disc('LAMP_STACK', mat, 3.55, .41, cz, .26, nseg=24)
# Sol yan baglanti kutusu + sarkan kablolar
box('CABLES', 'gunmetal', -4.55, -.4, 7.6, .55, 1.5, 1.9)
box('CABLES', 'rib', -4.86, -.4, 7.6, .1, 1.2, 1.5)
tube('CABLES', 'rubber', bezier((-4.7, -.4, 6.7), (-5.5, -.4, 4.6), (-4.4, -.4, 1.3), 14), .11, sections=10)
tube('CABLES', 'rubber', bezier((1.2, 1.2, 11.2), (.2, 2.1, 10.0), (-.6, 1.95, 9.3), 12), .07, sections=8)

# ---------------------------------------------------------------- disa aktar
scene = trimesh.Scene(); names = []; total = 0
for (zone, mat), items in sorted(BUCKET.items()):
    vs, fs, us, off = [], [], [], 0
    for v, f, u in items:
        vs.append(v); us.append(u); fs.append(f + off); off += len(v)
    mesh = trimesh.Trimesh(vertices=np.concatenate(vs), faces=np.concatenate(fs), process=False)
    mesh.visual = trimesh.visual.texture.TextureVisuals(uv=np.concatenate(us), material=MAT[mat])
    name = f'{zone}__{mat}'; scene.add_geometry(mesh, geom_name=name)
    names.append(name); total += len(mesh.faces)
GLB = OUT / 'TEST_KRIYO_REGULATOR_01.glb'
GLB.write_bytes(scene.export(file_type='glb'))
back = trimesh.load(GLB, force='scene', process=False)
print(f'EXPORT {GLB.name} {GLB.stat().st_size/1e6:.2f} MB | {len(names)} mesh | {total:,} ucgen | reload: {len(back.geometry)} geometri')
print('bounds:', np.round(back.bounds, 2).tolist())

# ---------------------------------------------------------------- render + pano (onceki ONAY duzeni)
rs = pyrender.Scene.from_trimesh_scene(scene, bg_color=np.array([.014, .017, .025, 1.]), ambient_light=[.27, .29, .34])
def look(eye, target):
    eye = np.asarray(eye, float); target = np.asarray(target, float)
    fwd = target - eye; fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 0, 1.]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd); M = np.eye(4); M[:3, 0] = right; M[:3, 1] = up; M[:3, 2] = -fwd; M[:3, 3] = eye
    return M
for pos, rgb, inten in [((-6, -14, 18), (.75, .83, .93), 340.), ((10, -6, 9), (.15, .5, .85), 120.), ((-10, 8, 6), (1., .45, .18), 70.)]:
    T = np.eye(4); T[:3, 3] = pos
    rs.add(pyrender.PointLight(color=np.asarray(rgb, float), intensity=inten), pose=T)
renderer = pyrender.OffscreenRenderer(1060, 720)
def render(eye, center, fov=36):
    node = rs.add(pyrender.PerspectiveCamera(yfov=math.radians(fov)), pose=look(eye, center))
    rgba, _ = renderer.render(rs, flags=pyrender.RenderFlags.RGBA); rs.remove_node(node)
    art = Image.fromarray(rgba, 'RGBA').convert('RGB')
    bloom = art.point(lambda v: max(0, (v - 165) * 1.05)).filter(ImageFilter.GaussianBlur(12))
    return ImageChops.add(art, bloom, scale=1.2)
C = (0, 0, 6.2)
front = render((0, -27, 9), C, 33)
iso = render((-18, -19, 14), C, 36)
close = render((-6.5, -12, 9.2), (-1.2, -1.2, 5.9), 40)
rear = render((17, -13, 16), (.4, .6, 7.4), 37)
renderer.delete()
for im, nm in ((front, 'front'), (iso, 'iso'), (close, 'close'), (rear, 'rear')):
    im.save(DBG / f'TEST_KRIYO_REGULATOR_{nm}.png')
board = Image.new('RGB', (1920, 1400), (13, 18, 30)); d = ImageDraw.Draw(board)
ft, fl, fm = font(34), font(21), font(17, False)
def panel(im, x, y, w, h, s):
    q = ImageOps.contain(im, (w, h), Image.Resampling.LANCZOS)
    d.rectangle((x, y, x + w, y + h), fill=(23, 30, 47))
    board.paste(q, (x + (w - q.width) // 2, y + (h - q.height) // 2))
    d.rectangle((x, y, x + w, y + h), outline=(73, 88, 118), width=2)
    d.text((x + 14, y + 12), s, font=fl, fill=(239, 243, 250), stroke_width=1, stroke_fill=(11, 16, 24))
d.text((45, 26), 'GEÇİCİ TEST MODELİ — KRİYO BASINÇ REGÜLATÖR İSTASYONU', font=ft, fill=(241, 245, 253))
d.text((45, 74), 'Gerçek 3B mesh renderı  •  içi delik manifold  •  2 manometre  •  el çarkı valf  •  2 akümülatör şişesi', font=fl, fill=(176, 194, 219))
panel(front, 45, 115, 910, 590, 'ÖN • gerçek GLB mesh render')
panel(iso, 980, 115, 895, 590, '3/4 • sol-ön üst açı')
panel(close, 45, 730, 910, 575, 'YAKIN • manometreler + el çarkı + düzgün isim plakası')
panel(rear, 980, 730, 895, 575, 'ÜST ARKA AÇI • manifold, şişeler, lamba kulesi')
d.text((45, 1335), f'GLB: TEST_KRIYO_REGULATOR_01.glb  •  {total:,} üçgen  •  {len(names)} adlandırılmış mesh  •  Studio dışı test — sahneye konmadı', font=fm, fill=(171, 188, 211))
PRE = OUT / 'TEST_KRIYO_REGULATOR_01_ONAY.png'; board.save(PRE, optimize=True)
print('Preview:', PRE)
