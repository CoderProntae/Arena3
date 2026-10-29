# Reactor wall-port deployment — approval-stage mechanism specification

**Scope/status:** Offline 3D mesh and motion preview, NOT installed or tested in Roblox Studio. Wall hatch **approved** by user. Interior guide/hydraulic piston modeled separately and **approved by user**; behind the piston will eventually be a connected service facility, as the user explicitly clarified. Both real GLBs and the composite GIF exist; no sound or VFX is implemented in Studio yet.

## Approved user motion description

1. **COLD:** Wall opening has two closed leaves. Approved emitter is wholly retracted behind the wall. No star, energy rays or ignition sounds.
2. **STARTUP, hatch first:** `HATCH_LEFT` moves in local −Y and `HATCH_RIGHT` in +Y. Open mechanical sounds should play only after authorized audio asset import/permissions are verified.
3. **STARTUP, actuator next:** An approved modeled hydraulic piston/guide (03B) pushes the **whole rigid emitter** forward along local +X. The piston can telescope in three stages, but the emitter itself does *not* telescope, deform, or stretch. Servo/hydraulic sounds should synchronize with this motion after asset permissions are verified.
4. **Ignition last:** Only after the moving emitter seats do its emissive state and Roblox Beam/ParticleEmitter/Trail/light effects ramp up. This is not baked into a static GLB; do not leave star/rays active in COLD.
5. **Shutdown:** Energy effects/sound decay → the piston retracts the rigid emitter → the two wall-port hatch leaves close (with sound). No shutter is allowed to cover the **central** reactor star.
6. **Meltdown:** Escalating alarms, room sound, reactor damage/leaks and center event are still required, with experience-specific audio permission verification.

## Model dimensions and inspectable files

- `model_exports/REACTOR_WALL_HATCH_THROUGH_01.glb` — actual through-hole, doors closed, named separate `HATCH_LEFT`/`HATCH_RIGHT` mesh nodes.
- `model_exports/REACTOR_WALL_HATCH_OPEN_INSPECTION_01.glb` — same geometry with doors slid aside so the hole can be inspected. This is an inspection pose, not a different asset for Studio.
- `model_exports/REACTOR_PISTON_GUIDE_01.glb` — 20 meshes (BASE, GUIDES, STAGE1/2/3, PUSHER); its rear-view approval sheet is `model_exports/REACTOR_PISTON_GUIDE_01_ONAY.png`. This rear guide and actuator are **our approved original interpretation**, not directly identifiable from the reference image.
- `model_exports/REACTOR_WALL_HATCH_MOTION_01.gif` — approved hatch's first offline *real mesh* animation preview, deliberately silent.
- `model_exports/REACTOR_DEPLOYMENT_WITH_PISTON_01.gif` — updated **offline and silent** synchronized front/rear, real-mesh preview with piston. It does NOT prove Roblox animation, audio playback or asset permissions.
- Local Y door travel is ±5.85 studs. Approved emitter's planned local X transform ranges from −11.47 (retracted) to +8.33 (extended), 19.80-stud rigid travel. Port opening 11.56 × 7.14 studs; emitter's max radius ~3.07 and deep tunnel half-height 3.31, giving cross-sectional clearance during passage. Stationary cage interior ~3.57 radial; moving piston stages offset +6.60 / +13.20 / +19.80 studs; pusher travels +19.80 with the emitter.
- This is concept geometry and sequencing. Only after model approvals should Studio implement replicated server-side stages and client VFX; verify **experience-specific** sound permissions before saying hatch/piston/motor/ignition/alarm audio works. No physical mouse-click tests.
- Numeric travel/timing are current preview proportions, adjustable only after feedback. All final state sequencing and movement must be done by replicated server-side scripts in Studio and tested at the end, not asserted from this GIF.
