# FAZ 4 ÖN HAZIRLIK — 4.1 Temizlik Kaydı + Modelleme Kanca Haritası
Tarih: 28 Ekim 2026 | Durum: **4.1 TAMAM + kaydedildi**. **M13 TAMAM** (modellendi, kullanıcı onayladı, Studio'ya gizli monte edildi, Play kanıtı alındı — Ctrl+S bekliyor). Sırada M14 + 4.2 hacimsel sızıntı bağlantısı.

---

## 1) 4.1 TEMİZLİK — ne silindi, ne kaldı

Dosya: `ServerScriptService.CORE_PROTOCOL_Server` (yerel kopya senkron:
`/home/user/CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua`,
önceki sürüm yedeği: `faz4/CORE_PROTOCOL_Server_onceki_141209.lua.bak`)

**Kaldırılan sahte görseller (19 düzenleme, 141209 → 140244 bayt):**
| Öğe | Adet | Not |
|---|---|---|
| `MOLTEN_EMITTER_DAMAGE_*` turuncu neon yanık küreleri (r=3.1) | 6 | + üzerindeki `BROKEN_EMITTER_SHOWER` 2B kıvılcım yağmurları |
| `PIPE_RUPTURE_LIP_*` boru ağzı küreleri | 10 | + `REAL_BROKEN_PIPE_JET` / `STEAM_FROM_PRESSURE` 2B emiterleri |
| `RISER_PRESSURE_RUPTURE` yara küreleri | 2 | + `VIEWABLE_CYAN_COOLANT_JET` / `BROKEN_MANIFOLD_BLUE_VAPOR` |
| `HAIRLINE_BOROSILICATE_CRACK` + `WINDOW_EDGE_SPIDER_CRACK` düz Part yama çatlaklar | olay başına ~40-90 | Üstelik eski koordinatlarda (z=93.7) yüzüyorlardı; canlı cam z=46.6'da |
| `STUCK_BROKEN_GLAZING_IN_FRAME` yama şeritleri | 16/kırılma | `shatterWindow` içinden |

**Dokunulmayanlar (bilinçli):**
- Oynanış durumu: `e.broken`, `line.broken/leaking`, `state.damagedPipes` (soğutma kaybı
  matematiği `actualCoolant()`), `state.windowBroken` — hepsi aynen çalışıyor.
  Silinen alanların (`e.scorch`, `p.mouth` vb.) tüm kullanımları `if` korumasına alındı.
- `shatterWindow()`'ın fiziksel cam parçaları (gerçek fizik Part'ları) kaldı; M14 gelene
  kadar cam "çatlamadan, kırılınca" davranacak.
- Olay sesleri/sarsıntıları zamanlama işareti olarak kaldı.
- Klasör iskeleti (`06_DAMAGE_THAT_STAYS`, `PERMANENT_SCARS` vb.) yerinde.

**Doğrulama (Play):** açılış COLD temiz, konsol 0 hata, `Geometry rays: 23/23 clear`,
dünya parça sayısı 1370 → **1352** (−18 = silinen küreler), yasaklı isim kalıntısı 0.

> Not: Bu küreler zaten GLB dünyasında hiç görünmüyordu (kod, `REACTOR_MESH_ASSEMBLY`
> varsa R5 görsellerini kapalı tutuyordu). Temizlik görsel kayıp yaratmadan FAZ 4.2/4.3'ün
> önünü açtı; ayrıca dünya her açılışta 18 ölü parça + 28 ölü 2B emiter taşımıyor artık.

## 2) MODELLEME KANCA HARİTASI

### 4.2 için — PIPE_SPOOL kopma modülleri (M13 buraya oturacak)
`REACTOR_MESH_ASSEMBLY.STATIC.REACTOR_COOLANT_PIPING_RING_01` altında 4 hazır modül
(öznitelikler: `Faz3RuptureSpool=true`, `SpoolId=...`):

| SpoolId | Pivot (Studio) | Eksen/Boy | Boru | Flanş |
|---|---|---|---|---|
| UPPER_LEFT | (-19.95, 42.35, 4.70) | Z / 7.0 | dış Ø1.0 | Ø1.62 |
| UPPER_RIGHT | (+19.95, 42.35, 4.70) | Z / 7.0 | dış Ø1.0 | Ø1.62 |
| REAR_LEFT | (-19.95, 31.20, -10.80) | Y / 6.2 | dış Ø1.0 | Ø1.62 |
| REAR_RIGHT | (+19.95, 31.20, -10.80) | Y / 6.2 | dış Ø1.0 | Ø1.62 |

Her modül 6 MeshPart: `nickel_pipe_01, pipe_bore_02, flange_03, gunmetal_04, clamp_05, cryo_band_06`.
**M13 isterleri:** aynı uç/flanş düzlemlerine oturan `RUPTURED` karşılıkları (yırtık ağız, dışa
kıvrık metal, kopmuş kelepçe) + değişim anında gösterilecek 3B hacimsel sızıntı hunisi için
ağız ankrajı. Değişim mekaniği: INTACT modül gizle ↔ RUPTURED göster (Faz 6 tetikleyecek;
Faz 4.2 yalnız model + göster/gizle iskeleti + elden tetikleme kanıtı).
Oynanış tarafı hazır: `state.damagedPipes` sayacı ve `breakLine(id)` olayları duruyor
(görsel uçları boşta — spool eşlemesi Faz 6.1/6.4'te bağlanacak).

### 4.3 için — yayıcı arıza iskeleti (büyük kısmı zaten var)
`REACTOR_MESH_CONTROLLER` (yerel kopya yeni alındı:
`reactor_startup/source/REACTOR_MESH_CONTROLLER.server.lua`, 424 satır):
- Her kafada `NOZZLE__*` + `ANTENNA__*` MeshPart'ları `bendParts` olarak toplanıyor
  (kafa başına ≥3 zorunlu; gerçekte NOZZLE 7 + ANTENNA 4 parça — örn. `NOZZLE__white`,
  `NOZZLE__pink`, `ANTENNA__silver`...), yerel pozları yedekleniyor.
- Tetik: dünya özniteliği `ReactorEmitterBrokenMask` (yayıncı: CORE_PROTOCOL_Server
  s.3251; yaş: `ReactorMeltdownAge` s.3197). Bit=1 olunca tek seferlik burkulma uygulanıyor:
  dışa 0.46/0.75 stud sürüklenme, -0.13.. düşey, ±0.14/0.18 yan, Z ±13/-16°,
  renk (145,55,41)/(72,49,48), `GLB_HeadCracked=true`; bit=0'da pozlar geri yükleniyor.
- **4.3'ün işi:** tek kademeyi **kademeli/asimetrik ilerlemeye** çevirmek (yaşa bağlı
  çok basamaklı burkulma şiddeti + kol bazlı farklı eşikler), lazer kesimini maske ile
  uçtan uca doğrulamak (Pilot `ReactorPilotRelayMask` yayını + CustomVapor istemci lazerleri),
  çekirdek dengesizliğini kırık kol sayısına bağlamak.
- **İşaretli legacy (Faz 6'da %0 2B'ye çevrilecek):** MeshController içindeki 2B
  `BROKEN_NOZZLE_SMOKE` / `METAL_ARC_AT_REAL_HEAD` ParticleEmitter'ları ve `FaceCamera`
  Beam lazer şeritleri; server tarafında `fracture()` elektrik arkı parçaları,
  `UNLATCHABLE_CEILING_ISOLATOR` kıvılcım yağmuru, `emergencySteam` sis emiterleri,
  `EDGE_EMERGENCY_BLUE_ARC` neon kolon. 4.1 kapsamında **değiller** (canlı olay görselleri;
  karşılıkları Faz 6'da 3B yapılacak), burada envantere işlendi.

### 4.4 için — gözlem camı (M14 ölçüleri CANLI ölçüldü)
Kodun ürettiği değil, Faz 2 yamasıyla **canlıda geçerli** geometri (Play ölçümü):
| Parça | Konum | Boyut |
|---|---|---|
| `PANORAMIC_LAMINATED_GLASS_1` | (-2.75, 24.625, 46.625) | 48.5 × 22.5 × 0.2 |
| `PANORAMIC_LAMINATED_GLASS_2` | (24.25, 24.625, 46.625) | 5.5 × 22.5 × 0.2 |
| `SLIM_OFFSET_GLASS_MULLION` | (-11.25, 24.625, 46.725) | 0.42 × 22.5 × 0.65 |
| `SLIM_SYMMETRIC_GLASS_MULLION_R` | (+11.25, 24.625, 46.725) | 0.42 × 22.5 × 0.65 |

Cam düzlemi z=46.625; toplam açıklık x∈[-27, 27], y∈[13.4, 35.9]; paneller T=0.98
(yani camın kendisi neredeyse görünmez sınır — M14 çatlak geometrisi bu düzlemde,
panel/mullion bölünmelerine saygılı 3 kademe olarak modellenecek).
Durum makinesi hazır: `crackPanes(0.55/1.05/1.4/1.9)` çağrıları (s.2563/2585/2618/2634 —
şimdilik yalnız ses/sarsıntı) ve `shatterWindow()` (fiziksel parçalar çalışıyor);
M14 kademeleri bu çağrılara bağlanacak.

## 3) Sıradaki adım (modelleme)
1. ✅ **M13** `DAMAGE_PIPE_RUPTURE_KIT_01.glb` — 4 spool için RUPTURED varyantlar + onay renderı (kullanıcı onayladı 28.10.2026).
2. **M14** `DAMAGE_GLASS_FRACTURE_STAGES_01.glb` — 3 kademe + onay renderı (SIRADAKİ).
3. ✅ M13 montajı + elden tetiklemeli Play kanıtı tamam (aşağıda). Buhar hunisi 4.2'de hacimsel motora bağlanacak (ankrajlar hazır: `MOUTH_A`/`MOUTH_B`).

## 4) M13 MONTAJ KAYDI (28.10.2026)
- **GLB (tasarım/onay):** `model_exports/DAMAGE_PIPE_RUPTURE_KIT_01.glb` (32 mesh, 13.528 üçgen) + `..._ONAY.png` (6 açı) + `..._RENK_KARSILASTIRMA.png`. Üreteç: `model_work/damage_rupture/make_damage_rupture_kit.py`.
- **Studio karşılığı:** `ServerScriptService.FAZ4_DamageAssets` (624 satır, 22.652 bayt; yerel kaynak `faz4/FAZ4_DamageAssets.server.lua`). MeshBin çekirdeği + palet + `hollowFlange` Faz 3'ten birebir; yırtık güdük GLB ile aynı formüller (LCG tohumlu, spool başına farklı diş deseni). Canlı iç yarıçap 0.36 (Faz 3 `rMain*0.72`).
- **Sahne:** `STATIC/DAMAGE_PIPE_RUPTURE_KIT_01` (`Faz4Generated`) > 4× `PIPE_SPOOL_<ID>_RUPTURED` (`Faz4RupturedSpool`, `SpoolId`) > spool başına 8 MeshPart (flange/gunmetal/clamp/nickel_pipe/torn_steel/pipe_bore/frost/cryo_band) + 2 görünmez ankraj `MOUTH_A/B` (`Faz4MouthAnchor`, CFrame bakışı egzoz yönünde).
- **Doğrulama (Edit):** montaj MeshPart 677 → **709** (+32), 8 ankraj; tüm parçalar Transparency=1, CanCollide/CanQuery/CanTouch=false; eksenel boylar sağlam karşılıklarıyla aynı (7.03/6.23), ankraj konumları hesapla birebir (örn. UL MOUTH_A (-19.95, 42.35, 5.26)).
- **Play kanıtı:** UPPER_LEFT + REAR_LEFT elden değişimi (sağlam gizle ↔ patlak göster) çalıştı; 3 kare `faz4/captures/M13_PLAY_*.jpg` — flanşlar komşularla kusursuz, renkler ortamla aynı, duvar/tava teması yok. Play durduruldu (çalışma anı değişikliği kalıcı değil).
- **Not:** Betik her Play'de yalnız kendi `Faz4Generated` kitini tazeler; Faz 2/3 yenilemelerinden etkilenmez. Tetikleme (hangi hasarda hangi spool) Faz 6'da `state.damagedPipes`/`breakLine(id)` ile bağlanacak.
