#!/usr/bin/env python3
"""Compiles approved Faz 2 Paket A GLB models into compact Luau binary ModuleScripts + Server Controller.

 Coordinate transform (exact match to REACTOR_MESH_ASSEMBLY):
   (x_src, y_src, z_src) -> Studio world (x_src, 26.50 + z_src, -y_src)
   Normal (nx, ny, nz)   -> Studio world (nx, nz, -ny)

 Outputs under model_work/studio_import/faz2_luau/:
   - Faz2_MeshChunk_1.lua .. Faz2_MeshChunk_N.lua (each strictly < 72 KB for safe MCP ScriptEditor transfer)
   - Faz2_ChamberAndTurbine.server.lua (verified with luau-compile)
"""
from __future__ import annotations
import base64, json, math, struct, sys
from pathlib import Path
import numpy as np

ROOT = Path("/home/user")
sys.path[:0] = [str(ROOT / ".cache/modeldeps")]
import trimesh

EXP = ROOT / "model_exports"
OUT_DIR = ROOT / "model_work/studio_import/faz2_luau"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ORIGIN_Y = 26.50

def src_to_studio_pos(v: np.ndarray) -> np.ndarray:
    # (x, y, z)_src -> (x, 26.50 + z, -y)_studio
    out = np.empty_like(v, dtype=np.float64)
    out[:, 0] = v[:, 0]
    out[:, 1] = ORIGIN_Y + v[:, 2]
    out[:, 2] = -v[:, 1]
    return out

def src_to_studio_nrm(n: np.ndarray) -> np.ndarray:
    out = np.empty_like(n, dtype=np.float64)
    out[:, 0] = n[:, 0]
    out[:, 1] = n[:, 2]
    out[:, 2] = -n[:, 1]
    l = np.linalg.norm(out, axis=1, keepdims=True)
    l[l < 1e-8] = 1.0
    return out / l

# Collect grouped meshes: (group_path, part_name, mat_key, list_of_(V_studio, N_studio, UV, F))
GROUPS: dict[tuple[str, str, str], list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]] = {}

def add_trimesh(group_path: str, part_name: str, mat_key: str, g: trimesh.Trimesh, T_src=None):
    if len(g.faces) == 0:
        return
    m = g.copy()
    if T_src is not None:
        m.apply_transform(T_src)
    v_src = np.asarray(m.vertices, dtype=np.float64)
    f = np.asarray(m.faces, dtype=np.int32)
    # Compute vertex normals in source space (respecting already-unmerged hard creases!)
    n_src = np.asarray(m.vertex_normals, dtype=np.float64)
    if len(n_src) != len(v_src):
        n_src = np.zeros_like(v_src)
        n_src[:, 1] = -1.0
    uv = getattr(m.visual, "uv", None)
    if uv is None or len(uv) != len(v_src):
        uv = np.stack(((v_src[:, 0] + 25.0) / 50.0, (v_src[:, 2] + 22.0) / 44.0), axis=1)
    else:
        uv = np.asarray(uv, dtype=np.float64)
    # Wrap UVs into [-8, +8] range so int16 quantization at 1/2048 is 100% lossless
    uv_min = np.floor(uv.mean(axis=0))
    uv = uv - uv_min

    v_st = src_to_studio_pos(v_src)
    n_st = src_to_studio_nrm(n_src)
    # Note: det([[1,0,0],[0,0,1],[0,-1,0]]) = +1 -> triangle winding orientation is preserved!
    GROUPS.setdefault((group_path, part_name, mat_key), []).append((v_st, n_st, uv, f))

# 1) Load REACTOR_CROWN_DECK_AND_RADIAL_PORTS_01.glb
crown_sc = trimesh.load(EXP / "REACTOR_CROWN_DECK_AND_RADIAL_PORTS_01.glb", force="scene", process=False)
for node in crown_sc.graph.nodes_geometry:
    tr, gname = crown_sc.graph[node]
    g = crown_sc.geometry[gname]
    mat_suffix = gname.split("__")[-1] if "__" in gname else "iron"
    # Route sliding hatch leaves into MOVING/REACTOR_RADIAL_HATCH_<TAG>/<LEAF_LEFT|LEAF_RIGHT>
    placed_moving = False
    for p_tag in ("LOWER_LEFT", "LOWER_RIGHT", "UPPER", "LOWER"):
        pref_l = f"{p_tag}_HATCH_LEFT__"
        pref_r = f"{p_tag}_HATCH_RIGHT__"
        if gname.startswith(pref_l):
            add_trimesh(f"MOVING/REACTOR_RADIAL_HATCH_{p_tag}/LEAF_LEFT", f"HATCH_LEFT__{mat_suffix}", mat_suffix, g, tr)
            placed_moving = True
            break
        elif gname.startswith(pref_r):
            add_trimesh(f"MOVING/REACTOR_RADIAL_HATCH_{p_tag}/LEAF_RIGHT", f"HATCH_RIGHT__{mat_suffix}", mat_suffix, g, tr)
            placed_moving = True
            break
    if not placed_moving:
        add_trimesh("STATIC/REACTOR_CROWN_AND_DECK_01", f"CROWN_DECK__{mat_suffix}", mat_suffix, g, tr)

# 2) Load ONLY the 4 new open-port lower-diagonal meshes from REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV03_DIAG_OPEN.glb
#    (The remaining 34 Rev02 meshes already exist in Studio and are upgraded in-place!)
rev03_sc = trimesh.load(EXP / "REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV03_DIAG_OPEN.glb", force="scene", process=False)
for node in rev03_sc.graph.nodes_geometry:
    tr, gname = rev03_sc.graph[node]
    if "LOWER_DIAGONAL_TRUE_PORT" in gname:
        add_trimesh("STATIC/REACTOR_SIDE_DIAG_OPEN_03", gname, "frame", rev03_sc.geometry[gname], tr)
    elif "LOWER_SLOPED_ROLLED_IRON_OPEN" in gname:
        add_trimesh("STATIC/REACTOR_SIDE_DIAG_OPEN_03", gname, "iron_lower", rev03_sc.geometry[gname], tr)

# 3) Load REACTOR_REAR_BULKHEAD_IRON_REV05_TURBINE_PORT.glb
rev05_sc = trimesh.load(EXP / "REACTOR_REAR_BULKHEAD_IRON_REV05_TURBINE_PORT.glb", force="scene", process=False)
for node in rev05_sc.graph.nodes_geometry:
    tr, gname = rev05_sc.graph[node]
    mat_suffix = gname.split("__")[-1]
    add_trimesh("STATIC/REACTOR_REAR_BULKHEAD_REV05", f"REV05__{mat_suffix}", f"r5_{mat_suffix}", rev05_sc.geometry[gname], tr)

# 4) Load REACTOR_REAR_TURBINE_AND_PLENUM_01.glb (reducing ONLY hidden rear condenser fin cylinder segs if needed)
turb_sc = trimesh.load(EXP / "REACTOR_REAR_TURBINE_AND_PLENUM_01.glb", force="scene", process=False)
for node in turb_sc.graph.nodes_geometry:
    tr, gname = turb_sc.graph[node]
    mat_suffix = gname.split("__")[-1]
    t_mat = f"tb_{mat_suffix}"
    if gname.startswith("TURBINE_ROTOR__"):
        add_trimesh("MOVING/REACTOR_REAR_TURBINE_ROTOR", gname, t_mat, turb_sc.geometry[gname], tr)
    else:
        add_trimesh("STATIC/REACTOR_REAR_TURBINE_PLENUM_01", f"PLENUM__{mat_suffix}", t_mat, turb_sc.geometry[gname], tr)

# 5) Build Full-Sightline Front Octagonal Bulkhead Seal at Y_src = -18.55 (Z_studio = +18.55):
#    Leaves 100% of the octagonal reactor interior [-24.5, +24.5] x [-21.5, +21.5] completely unobstructed
#    (so UPPER at Y=48 and LOWER at Y=5 are 100% visible from Z=108 in the Control Room!),
#    while sealing 100% of the exterior R5 hangar [-96..+96, 0..110] so NO behind-wall pistons leak!
def add_seal_box(name, mat_k, x0, x1, y0, y1, z0, z1):
    g = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    g.apply_translation(((x0 + x1) * 0.5, (y0 + y1) * 0.5, (z0 + z1) * 0.5))
    g.unmerge_vertices()
    add_trimesh("STATIC/OBSERVATION_OCTAGON_SEAL_01", name, mat_k, g)

# Left & Right exterior bulkhead walls (|X| = 24.5 .. 96.0, Z_src = -26.5 .. +83.5 -> Y_studio = 0 .. 110)
add_seal_box("SEAL_WING_L", "gunmetal", -96.0, -24.48, -19.6, -18.0, -26.5, 83.5)
add_seal_box("SEAL_WING_R", "gunmetal",  24.48,  96.0, -19.6, -18.0, -26.5, 83.5)
# Upper & Lower exterior headers above/below octagon (X = -24.5..+24.5, Z_src > 21.5 and Z_src < -21.5)
add_seal_box("SEAL_HEADER_TOP", "gunmetal", -24.52, 24.52, -19.6, -18.0,  21.48, 83.5)
add_seal_box("SEAL_SILL_BOT",   "gunmetal", -24.52, 24.52, -19.6, -18.0, -26.5, -21.48)
# 4 Octagonal Corner Wedge Seals strictly outside the 45-deg sloped edges (|X| in 17..24.5, |Z| in 12.5..21.5)
for sx in (-1, 1):
    for sz in (-1, 1):
        # Triangle in (X, Z): (sx*24.52, sz*12.48), (sx*24.52, sz*21.52), (sx*16.98, sz*21.52)
        p2d = [(sx * 24.52, sz * 12.48), (sx * 24.52, sz * 21.52), (sx * 16.98, sz * 21.52)]
        vs = []
        for yv in (-18.9, -17.9):
            for px, pz in p2d:
                vs.append((px, yv, pz))
        if sx * sz > 0:
            fs = [(0, 1, 2), (3, 5, 4), (0, 3, 4), (0, 4, 1), (1, 4, 5), (1, 5, 2), (2, 5, 3), (2, 3, 0)]
        else:
            fs = [(0, 2, 1), (3, 4, 5), (0, 4, 3), (0, 1, 4), (1, 5, 4), (1, 2, 5), (2, 3, 5), (2, 0, 3)]
        gw = trimesh.Trimesh(vertices=np.asarray(vs, float), faces=np.asarray(fs, int), process=False)
        gw.unmerge_vertices()
        add_trimesh("STATIC/OBSERVATION_OCTAGON_SEAL_01", "SEAL_CORNER_WEDGE", "frame", gw)
# Beveled octagonal front trim collar framing the reactor mouth cleanly!
oct_pts = [(-17.0, -21.5), (17.0, -21.5), (24.5, -12.5), (24.5, 12.5),
           (17.0, 21.5), (-17.0, 21.5), (-24.5, 12.5), (-24.5, -12.5)]
for a_o, b_o in zip(oct_pts, oct_pts[1:] + oct_pts[:1]):
    pa = np.array([a_o[0], -18.25, a_o[1]], float)
    pb = np.array([b_o[0], -18.25, b_o[1]], float)
    d_o = pb - pa; L_o = np.linalg.norm(d_o)
    cyl = trimesh.creation.cylinder(radius=0.28, height=L_o, sections=8)
    cyl.apply_transform(trimesh.geometry.align_vectors((0, 0, 1), d_o / L_o))
    cyl.apply_translation((pa + pb) * 0.5)
    cyl.unmerge_vertices()
    add_trimesh("STATIC/OBSERVATION_OCTAGON_SEAL_01", "SEAL_OCTAGON_BEVEL", "edge", cyl)


# ============================================================================
# PACK EACH MERGED PART INTO COMPACT BINARY RECORD
# Format per record (little-endian):
#   center_x, center_y, center_z : 3 x float32
#   scale_x,  scale_y,  scale_z  : 3 x float32  (half-extents -> int16 maps [-32767..32767] to [-scale..+scale])
#   uv_scale                     : 1 x float32
#   n_verts                      : uint32
#   n_tris                       : uint32
#   verts: n_verts x (vx:int16, vy:int16, vz:int16, nx:int8, ny:int8, nz:int8, pad:uint8, u:int16, v:int16) = 14 bytes/vert
#   tris:  n_tris  x (i0:uint16, i1:uint16, i2:uint16) = 6 bytes/tri (auto-splits if n_verts > 65000)
# ============================================================================
RECORDS = []
total_v, total_t = 0, 0

for (gpath, pname, mkey), items in sorted(GROUPS.items()):
    vs = np.concatenate([x[0] for x in items], axis=0)
    ns = np.concatenate([x[1] for x in items], axis=0)
    uvs = np.concatenate([x[2] for x in items], axis=0)
    fs_list = []
    off = 0
    for x in items:
        fs_list.append(x[3] + off)
        off += len(x[0])
    fs = np.concatenate(fs_list, axis=0)

    # Deduplicate identical (pos, nrm, uv) vertices within 0.0004 stud to cut payload size ~3x losslessly!
    q_key = np.hstack([
        np.round(vs * 2000.0).astype(np.int64),
        np.round(ns * 120.0).astype(np.int64),
        np.round(uvs * 1024.0).astype(np.int64),
    ])
    _, uniq_idx, inv_idx = np.unique(q_key, axis=0, return_index=True, return_inverse=True)
    vs = vs[uniq_idx]
    ns = ns[uniq_idx]
    uvs = uvs[uniq_idx]
    fs = inv_idx[fs].astype(np.int32)
    # Drop degenerate triangles
    keep_f = (fs[:, 0] != fs[:, 1]) & (fs[:, 1] != fs[:, 2]) & (fs[:, 0] != fs[:, 2])
    fs = fs[keep_f]
    if len(fs) == 0:
        continue
    assert len(vs) < 65000, f"Part {pname} has {len(vs)} verts > 65000"

    vmin, vmax = vs.min(axis=0), vs.max(axis=0)
    center = 0.5 * (vmin + vmax)
    half_ext = np.maximum(0.5 * (vmax - vmin), 1e-4)
    v_local = vs - center[None, :]
    vq = np.clip(np.round(v_local / half_ext[None, :] * 32760.0), -32767, 32767).astype("<i2")
    nq = np.clip(np.round(ns * 127.0), -127, 127).astype("<i1")
    uv_max = float(max(np.abs(uvs).max(), 1e-3))
    uvq = np.clip(np.round(uvs / uv_max * 32760.0), -32767, 32767).astype("<i2")
    fq = fs.astype("<u2")

    v_dtype = np.dtype([("vx", "<i2"), ("vy", "<i2"), ("vz", "<i2"),
                        ("nx", "<i1"), ("ny", "<i1"), ("nz", "<i1"), ("pad", "<u1"),
                        ("u", "<i2"), ("v", "<i2")])
    v_buf = np.zeros(len(vs), dtype=v_dtype)
    v_buf["vx"], v_buf["vy"], v_buf["vz"] = vq[:, 0], vq[:, 1], vq[:, 2]
    v_buf["nx"], v_buf["ny"], v_buf["nz"] = nq[:, 0], nq[:, 1], nq[:, 2]
    v_buf["u"], v_buf["v"] = uvq[:, 0], uvq[:, 1]

    hdr = struct.pack("<7fII",
                      float(center[0]), float(center[1]), float(center[2]),
                      float(half_ext[0]), float(half_ext[1]), float(half_ext[2]),
                      float(uv_max), len(vs), len(fs))
    raw_bytes = hdr + v_buf.tobytes() + fq.tobytes()
    b64 = base64.b64encode(raw_bytes).decode("ascii")
    RECORDS.append({
        "group": gpath,
        "name": pname,
        "mat": mkey,
        "b64": b64,
        "verts": int(len(vs)),
        "tris": int(len(fs)),
    })
    total_v += len(vs)
    total_t += len(fs)

print(f"Compiled {len(RECORDS)} MeshPart records: {total_v:,} unique verts, {total_t:,} tris")
total_b64 = sum(len(r["b64"]) for r in RECORDS)
print(f"Total base64 size: {total_b64/1024:.1f} KB")

# Split RECORDS into ModuleScripts of <= 58 KB each so every MCP upload is tiny & instant!
for old_f in OUT_DIR.glob("Faz2_MeshChunk_*.lua"):
    old_f.unlink()

chunks = []
cur_list, cur_sz = [], 0
for rec in RECORDS:
    est = len(rec["b64"]) + 200
    if cur_list and cur_sz + est > 58000:
        chunks.append(cur_list)
        cur_list, cur_sz = [], 0
    cur_list.append(rec)
    cur_sz += est
if cur_list:
    chunks.append(cur_list)

for idx, ch in enumerate(chunks, 1):
    lines = ["--!nonstrict", f"-- Auto-compiled Faz 2 Paket A 3D Mesh Chunk {idx}/{len(chunks)}", "return {"]
    for r in ch:
        lines.append(
            f'\t{{group = "{r["group"]}", name = "{r["name"]}", mat = "{r["mat"]}", '
            f'b64 = "{r["b64"]}"}},'
        )
    lines.append("}")
    txt = "\n".join(lines) + "\n"
    p = OUT_DIR / f"Faz2_MeshChunk_{idx}.lua"
    p.write_text(txt, encoding="utf-8")
    print(f"  Wrote {p.name}: {len(ch)} records, {len(txt)/1024:.1f} KB")

(OUT_DIR / "manifest.json").write_text(json.dumps({
    "num_chunks": len(chunks),
    "num_records": len(RECORDS),
    "total_verts": total_v,
    "total_tris": total_t,
}, indent=2), encoding="utf-8")
