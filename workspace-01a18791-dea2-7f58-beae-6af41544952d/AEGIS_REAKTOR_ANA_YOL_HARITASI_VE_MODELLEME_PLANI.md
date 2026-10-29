> **Arşiv notu — 29 Ekim 2026:** Bu eski yol haritası tarihsel kayıttır ve aşağıdaki durumlar güncel olmayabilir. Tek güncel plan, Fikirler ve Canlı Görseller sekmeleriyle `reports/AEGIS_GUNCEL_PLAN_VE_FIKIRLER.html` dosyasındadır.

# AEGIS REAKTÖRÜ — TEK ANA YOL HARİTASI, ERTELENEN İŞLER VE 3B MODELLEME PLANI (TO-DO)

**Tarih:** 28 Ekim 2026  
**Aktif Roblox Studio Yeri:** `AEGIS_Reactor.rbxlx`  
**Kapsanan Geçmiş Belgeler:** `model_work/REACTOR_MODEL_ROADMAP.md`, `model_work/MODEL_REVIEW_STATUS.md`, `model_work/wall_bay/MECHANICS_SEQUENCE.md`, `reports/REACTOR_GORSEL_KARSILASTIRMA_2026-10-25.md`, `CORE_PROTOCOL_REMAKE_Eksi_ve_Duzeltmeler.md`, `CORE_PROTOCOL_REMAKE_Es_Zamanli_Karsilastirma_ve_Oz_Degerlendirme.md`, `CORE_PROTOCOL_REMAKE_R5_Sonuc_ve_Karsilastirma.md`, `CORE_PROTOCOL_V2_Kurulum.md`, `reactor_startup/SCENE_SPEC_TR.md`, `reactor_startup/README_TR.md`, `references/Video_Ilk_Cozumleme.md`.

Bu belge; proje başından beri **"önce çekirdek, buhar ve 6 lazerin kalbini oturtalım, bunları sonra yaparız"** diyerek ertelediğimiz **bütün 3B modelleri, oda mimarisini, fiziksel hasar sistemini, oynanış modlarını ve ses entegrasyonunu** tek bir çatı altında toplar.

---

## 1. İLK ÖNCE SEN (SON KULLANICI OLARAK) NE YAPACAKSIN?

Biz teknik üretimi, 3B `.glb` modellemeyi, Luau kodlamasını ve canlı Studio testlerini kendi tarafımızda yürüteceğiz. Senin son kullanıcı olarak yapman gerekenler yalnızca şu **5 kısa kontrol noktasıdır**:

- [x] **Adım 1.1 — Eşzamanlı & Eşit Boylu 6 Lazer (`V15`) Canlı Kontrolü ve Kapı 05–06 Onayı (TAMAMLANDI & ONAYLANDI):**
  - Kullanıcı Studio’da `V15`’i bizzat Play ile test edip onayladı ve `Ctrl + S` ile kaydetti (`approve_v15_start_phase2`).

- [x] **Adım 1.2 — Yerel Dosya Kaydı (`Ctrl + S`):**
  - MCP köprüsü güvenlik sınırları gereği Windows diskindeki `.rbxlx` dosyasını doğrudan diske yazamaz; değişiklikleri açık Studio oturumuna işler.
  - Onayladığın her aşamadan sonra Studio’da **`Ctrl + S`** tuşlarına basarak `AEGIS_Reactor.rbxlx` dosyasını kendi bilgisayarında kalıcı olarak kaydet.

- [x] **Adım 1.3 — Yeni 3B Modellerde Ön-İzleme Onayı ("Önce Gör, Sonra Sahneye Koyalım"):**
  - Aşağıdaki **Bölüm 4**’te listelenen her yeni 3B `.glb` model paketini (sekizgen duvarlar, üst/alt kapak yuvaları, soğutma boruları, kırık hasar parçaları, kontrol masası, koridorlar, bunker vb.) önce sana **önizleme görseliyle** sunacağız ve sesli bildirim (`notify_user`) çalacağız.
  - Sen sadece **"Onay"** veya **"Şurasını değiştir"** diyeceksin; onayın olmadan sahneye kalıcı model yerleştirmeyeceğiz.

- [x] **Adım 1.4 — Ses Aşamasına Gelindiğinde Roblox Ses İzin Kontrolü (Faz 7’de):**
  - Roblox’ta ses varlıkları (`rbxassetid://...`) deneyime özel izin gerektirir. Faz 7’ye geldiğimizde kendi hesabın/deneyimin altında Creator Store’dan seçtiğimiz veya senin yüklediğin seslerin Studio Output’ta `Failed to load sound` hatası vermediğini birlikte doğrulayacağız.

- [x] **Adım 1.5 — Kendi Karakterinle Fiziksel Yürüme & Tıklama Kabul Testi (Faz 5–6 Sonunda):**
  - Yeni kontrol masası, koridorlar ve kart dolapları yerleştiğinde Studio’da kendi karakterinle yürüyüp düğmelere, kollara (`SCRAM`, `POWER`, `COOLANT`) ve yetki kartlarına (`AUTH 01–03`) bizzat tıklayarak kullanım rahatlığını onaylayacaksın.

---

## 2. ŞU ANA KADAR NELER TAMAMLANDI, NELER ERTELENDİ?

### Tamamlanan ve Korunan Temel (Dokunulmayacak Onaylı Çekirdek)
| Katman | Durum | Özet |
|---|---|---|
| **Canlı Görsel & Dosya Galerisi (`0.0.0.0:8080`)** | **Aktif (Canlı Önizleme)** | Mesaj bitmesini beklemeden tüm test karelerine (`.cache/model_debug`), onay panolarına, `.glb` modellerine ve kod/plan dosyalarına anlık erişim sağlar. |
| **V2 Sesli Oyuncu Alarm Köprüsü** | **Tamamlandı** | Ben iş bitirdiğimde veya soru sorduğumda odak çalmadan WAV alarmı + tepsi bildirimi gönderir (`notify_user`). |
| **Kontrol 01 — 6 Fiziksel GLB Başlık, Kapak & Piston** | **Onaylı** | `REACTOR_EMITTER_REV03` (×6), `REACTOR_PISTON_GUIDE_01` (×6), `REACTOR_WALL_HATCH_THROUGH_01` (×2) rijit hareket ediyor. |
| **Kontrol 02 — 6 Gerçek `NOZZLE__white` Ağzından Düz Buhar** | **Onaylı** | Yerçekimsiz (`Gravity = 0`), aşağı sarkmadan eksen boyunca düz püsküren 3B buhar jetleri. |
| **Kontrol 03 — Reaktör Kararması (Kontrol Odası Elektriği Kesilmeden)** | **Onaylı** | Reaktör odası kararırken kontrol odasının fiziksel ışıkları ve ekranları sönmez. |
| **Kontrol 04–06 (`V14D` + `V15`) — `%0` 2B Efektli 3B Bulutsu Çekirdek & Eşzamanlı 6 Lazer** | **Canlı Doğrulandı** | `2.688` mikro-bulutluk 3B `EditableMesh` + `SurfaceAppearance` çekirdek, yanal Z-tampon gizleme, **`0 -> 63` tek adımda eşzamanlı 6 lazer ateşlemesi** ve 6 kolda **`0.000000` stud farkla** tam `FOCUS = (0, 26.5, 2.70)` merkez birleşimi (`V15`). |

### Şimdiye Kadar "Sonra Yaparız" Diyerek Ertelediğimiz Başlıkların Özeti
1. **Model 06 Rev02 Sekizgen Demir Yan Duvarların** Studio’da nihai ölçek/konum onayı ve kalıcı montajı.
2. **Üst, Alt ve Çapraz 4 Yayıcı İçin Gerçek Duvar/Tavan/Zemin Yuvaları ve Kapakları** (şu an yalnızca sol ve sağ yayıcılarda gerçek delikli kapak var).
3. **Pistonların Arkasındaki Bağlantılı Servis Tesisi** (kapaklar açıldığında arkada siyah boşluk görünmemesi için).
4. **Reaktör Odası Tavanı, Alt Çukuru, Gözlem Penceresi Zırh Çerçevesi ve Çevresel Soğutma Boruları / Kablo Hatları.**
5. **Gerçek 3B Fiziksel Hasar Modelleri** (eski R5 sahte turuncu yanık kürelerinin sökülüp gerçek yırtılan boru, bükülen yayıcı/anten ve kademeli çatlayan/kırılan cam modellerinin yapılması).
6. **Kontrol Odası Yeniden Modellemesi, Bloom’da Patlamayan Dünya-İçi (`SurfaceGui`) Göstergeler, Sol/Sağ Servis Koridorları, 6 Kart Dolabı ve Zırhlı Sığınak (Bunker).**
7. **Startup Dışı Tüm Oyun Senaryolarının (`Failed Startup`, `Freezedown`, `435 sn Meltdown`, `+320 sn Dikey Mavi Sütun`, `Successful Shutdown`, `Failed Shutdown`)** yeni `%0` 2B / gerçek 3B mimariyle tam uyumlu hale getirilmesi.
8. **Deneyime Özel Doğrulanmış Ses Paketi (`SILENT_PROTOTYPE = false` geçişi)** ve üretim moduna (`STUDIO_AUTO_STARTUP = false`) dönüş.

---

## 3. BİZ SIRAYLA NE YAPACAĞIZ? (FAZ 1 -> FAZ 7 UYGULAMA SIRASI)

Her faz kendi içinde bağımsızdır; bir faz bitip canlı Studio Play ile doğrulanmadan sonrakine geçilmez.

### FAZ 1 — Startup & `ONLINE` Görsel Kapısının Kapatılması ve Fiziksel Başlatma Geçişi (TAMAMLANDI & ONAYLANDI)
- [x] **1.1.** `V15` eşzamanlı (`0 -> 63`) ve `0.000000` stud farkla eşit boylu 6 lazer + `V14D` `%0` 2B organik bulutsu çekirdek canlı Studio Play ile doğrulandı ve kullanıcı tarafından onaylandı (`approve_v15_start_phase2`).
- [x] **1.2.** Fiziksel başlatma ve ters kapanış (`PULL_SCRAM` -> `SUCCESS_SHUTDOWN`) korundu.

### FAZ 2 — Reaktör Odası Kabuğu, Sekizgen Duvarlar, Arka Türbin Fanı & 6 Yayıcı Yuvası (3B Modelleme Paketi A — TAMAMLANDI & ONAYLANDI)
- [x] **2.1.** Çok tonlu grimsi-demirimsi (`01_komut_110.jpg` kalibreli: üst soğuk arduvaz mavi-gri `RGB(101,113,134)`, orta soğuk grafit-demir `RGB(74,79,94)`, alt zeytuni-gri çelik `RGB(72,69,61)`) sekizgen yan duvarlar (`REV03_DIAG_OPEN`) + sıfır bakırımsı/turuncu sızıntı güncellendi.
- [x] **2.2.** **Üst (`SL-00`), Alt (`SL-05`), Sol-Alt (`SL-03`) ve Sağ-Alt (`SL-04`) yayıcılar** için sekizgen gövdeyle bütünleşen 3B geçiş tünelleri ve çift yapraklı mekanik sürgülü kapaklar (`REACTOR_RADIAL_HATCH_*`) kuruldu; `LiveGate_*` / `ReactorPilotGate_*` ile `±5.85` stud senkron çalışıyor.
- [x] **2.3.** Sekizgen tavan/zemin çukuru, köşe kafes kirişler + şerit çalışma lambaları, zeytuni-gri panjurlu radyatörler, **10 kanatlı keskin CNC arka türbin fanı (`(0, 28.30, -16.25)`) + üst kobalt-mavi panjur + arkası `%0` boşluklu 18 stud kapalı stator/tünel/12 nikel serpantinli kondenser plenum odası** kuruldu ve canlı Play’de döner mekanik animasyonu doğrulandı.
- [x] **2.4.** Kontrol odası **simetrik 3 bölmeli zırhlı gözlem camı dikmeleri** (`X = ±11.25`) ve reaktör ağzı ön sekizgen sızdırmazlık contası (`OBSERVATION_OCTAGON_SEAL`) kuruldu.
- [x] **2.5.** `ServerScriptService.Faz2_ChamberAndTurbine` (`54.286` bayt, `Stop` sonrası kalıcılık doğrulandı) ile `AEGIS_Reactor.rbxlx` kurulumu ve canlı Studio Play görsel kanıtı (`model_exports/FAZ2_PAKET_A_CANLI_STUDIO_PLAY_KANIT.png`) tamamlandı ve kullanıcı tarafından onaylandı.

### FAZ 3 — Reaktör Borulama Ağı ve Piston Arkası Servis Tesisi (3B Modelleme Paketi B — STUDIO MONTAJI & CANLI PLAY TAMAMLANDI)
- [x] **3.1.** Referans videoda reaktör çevresinde görünen **ana kriyojenik soğutma boruları, kollu kesme vanaları, ışıklı manometre blokları, flanşlar ve yüksek gerilim kablo tavaları** (`REACTOR_COOLANT_PIPING_RING_01.glb` — `95` mesh, `52.620` üçgen, Faz 4.2 için `4` ayrı `PIPE_SPOOL_*` kopma modülü dahil) çekirdek, 6 lazer ve 10 kanatlı arka türbin görüşünü `%100` açık bırakacak şekilde modellendi.
- [x] **3.2.** **Piston Arkası Bağlantılı Servis Tesisi (`MECHANICS_SEQUENCE.md` ertelenen madde):** 6 radyal kapak (`SL-00`..`SL-05`) açıldığında teleskopik pistonların arkasında boş siyah uzay görünmemesi için; `35.5` stud derinlikli zırhlı hidrolik servis galerileri, çift akümülatörler, delikli yürüyüş ızgaraları, gömme şerit servis lambaları ve dış tesis bakım hava kilidi (`PISTON_REAR_SERVICE_BAY_01.glb` — `37` mesh, `9.612` üçgen) modellendi ve kullanıcı ön-izleme onayı alındı (`approve_mount_faz3`).
- [x] **3.3.** `ServerScriptService.Faz3_PipingAndServiceBays` (`37.692` bayt, `129` `MeshPart`, `Stop` sonrası kalıcılık doğrulandı) ile `AEGIS_Reactor.rbxlx` kurulumu ve canlı Studio Play görsel kanıtı (`model_exports/FAZ3_PAKET_B_CANLI_STUDIO_PLAY_KANIT.png`) tamamlandı — **28.10.2026'da kullanıcı tarafından kabul edildi** (kabul öncesi Faz 4 kapısı olarak boşluk/mühür + içiçe geçme denetimi tamamlandı: tek bulgu CROWN_DECK merkez zemin yarığı, `DENETIM_MUHUR_ZEMIN_01` ile mühürlendi — `audit_faz3/DENETIM_RAPORU_FAZ4_ONCESI.md`).

### FAZ 4 — Gerçek Fiziksel Hasar, Boru Patlaması ve Cam Kırılması Modelleri (3B Modelleme Paketi C)
- [x] **4.1.** Eski R5 döneminden kalan **sahte turuncu yanık kürelerinin ve düz Part yamalarının tamamen temizlenmesi**. *(28.10.2026 tamam: `CORE_PROTOCOL_Server` 141209→140244 B, dünya 1370→1352 parça, Play doğrulandı; kanca haritası: `faz4/FAZ4_ON_HAZIRLIK.md`)*
- [ ] **4.2.** **Kırılabilir Boru Modülleri:** Sağlam boru + patlamış/yırtılmış boru ağızları (`INTACT` / `RUPTURED` mesh çifti) ve kırılan noktadan çıkan gerçek 3B hacimsel basınçlı buhar/plazma sızıntısı.
- [ ] **4.3.** **Yayıcı Asimetrik Arıza Fiziği:** Meltdown ilerledikçe 6 yayıcının aynı anda değil kademeli/asimetrik olarak arızalanması; arızalanan kolda gerçek `NOZZLE__` / `ANTENNA__` parçalarının burkulması, o kolun 3B lazerinin kesilmesi ve merkez çekirdeğin dengesizleşip çırpınması.
- [ ] **4.4.** **Kademeli Gözlem Camı Hasarı:** Düz çıkartma yerine 3 aşamalı gerçek 3B çatlak geometrisi (`Hafif Çatlak -> Ağır Örümcek Çatlak -> Son Evrede Kırılan Zırhlı Cam Parçaları`).

### FAZ 5 — Kontrol Odası, Okunaklı Ekranlar, Servis Koridorları ve Bunker (3B Modelleme Paketi D)
- [ ] **5.1.** **Alçak Merkezi Kontrol Konsolu & Kumanda Elemanları:** Kadrajı kapatmayan referans oranlı ana konsol ile üzerinde gerçek hareketli 3B kumandalar:
  - `COOLANT FLOW` çevirmeli fiziksel valf/kadran (`0–25–50–75–100%`),
  - `REACTOR POWER` kademeli fiziksel kol (`0–25–50–75–100%`),
  - `FOCUS LASERS` ve `E-COOLANT` mandallı şalter kolları,
  - Koruma kapaklı `IGNITION` ve `SHUTDOWN` basmalı butonları,
  - Sağda bağımsız, şeffaf güvenlik kapaklı **`SCRAM`** kürsüsü,
  - Zeminden hidrolikle yükselen **3 kart yuvalı `ARMED SHUTDOWN` merkez konsolu**.
- [ ] **5.2.** **Bloom’da Patlamayan Dünya-İçi (`SurfaceGui`) Paneller:** Kalıcı ekran HUD’u kullanmadan; sıcaklık (`°C`), basınç (`PSI`), soğutma akışı, 6 yayıcı röle diyagramı ve meltdown’da sol duvarda gerçek dünya-içi **`T-mm:ss`** geri sayım ekranının net okunaklı hale getirilmesi.
- [ ] **5.3.** **Kontrol Odası Tavan & Aydınlatma Mimarisi:** Tavan armatürlerinin üst durum yazısını kapatmadığı, reaktör odasından daha aydınlık/soğuk endüstriyel kontrol odası kabuğu.
- [ ] **5.4.** **Sol/Sağ Servis Koridorları, Otomatik Hava Kilitleri ve 6 Yetki Kartı Dolabı (`AUTH 01/02/03`):** Yaklaşıldığında açılıp `2.9 sn` sonra kapanan fiziksel hava kilitleri ve her tur rastgele 3 dolaba dağıtılan fiziksel yetki kartları.
- [ ] **5.5.** **Acil Durum Sığınağı (Bunker):** Patlamadan `11 sn` önce ağır zırhlı kapısı kapanmaya başlayan, zamanında içine giren oyuncuları patlamadan koruyan tam 3B sığınak odası.

### FAZ 6 — Startup Dışı Tüm Oynanış Modlarının `%0` 2B / Gerçek 3B Entegrasyonu
- [ ] **6.1.** **Termal & Güç Simülasyonu Kalibrasyonu:** Güç, soğutma, hasarlı boru kaybı, `FOCUS LASERS` ısı artışı ve sınırlı `E-COOLANT` tankının dengelenmesi.
- [ ] **6.2.** **Failed Startup (Başarısız Başlatma):** Startup sırasında güç veya soğutma kesilirse fiziksel koruma çubuklarının inmesi, lazerlerin kapanması, 6 başlığın geri çekilip kapakların kapanması ve `18 sn` sonra temiz yeniden deneme.
- [ ] **6.3.** **Freezedown (Aşırı Soğuma) & Kurtarma:** Düşük güç + yüksek soğutmada `460 °C` altında 3B kriyojenik buz-buhar zarfının oluşması ve `IGNITION` ile yeniden ısıtıp `ONLINE`’a dönüş.
- [ ] **6.4.** **435 Saniyelik (`7 dk 15 sn`) Referans Meltdown Sekansı:**
  - Tam ekran kırmızı filtre **kullanmadan**, gerçek döner kırmızı ikaz lambaları ve kontrollü exposure ile acil durum aydınlatması,
  - Kademeli boru patlamaları, yayıcı kırılmaları ve cam çatlaması,
  - **`+320.` saniye referans imzası:** Çekirdekten dikey yükselen devasa **3B mavi plazma enerji sütunu**,
  - Yalnızca meltdown/patlama anlarına özgü sarsıntı ve şok dalgaları (**startup’ta kamera sarsıntısı kesinlikle yok**),
  - Bunker kapısı kapanışı, merkez radyal füzyon patlaması ve `57 sn` `AFTERMATH` sonrası tam tur sıfırlama (`resetMachine`).
- [ ] **6.5.** **Successful Shutdown & Failed Shutdown (YouTube `26:00` ve `19:04` Karşılıkları):**
  - İlk `270 sn` içinde yeterli soğutmayla erken `SCRAM` veya 3 `AUTH` kartı + `ARMED SHUTDOWN` basıldığında: 3B çekirdek/lazer sönümü -> 6 pistonun yayıcıları rijit geri çekmesi -> 6 kapağın kapanması (`CORE OFFLINE / STANDBY`).
  - `270 sn` sonrası veya yetersiz soğutmada: fiziksel kontrol çubuğu sıkışması, yayıcı kırılması ve `SHUTDOWN FAILURE / REACTOR CRITICAL` evresine geçiş.

### FAZ 7 — Doğrulanmış Ses Paketi, Performans & Karakter Çarpışma Cilası
- [ ] **7.1.** Kullanıcıyla izinleri doğrulanmış ses varlıklarının (`kapak ray sesi`, `3 kademeli hidrolik piston`, `kriyojenik buhar`, `6’lı eşzamanlı lazer ateşleme`, `manyetik çekirdek uğultusu`, `alarm/siren`, `opening / escalation / finale` müzikleri) bağlanıp `SILENT_PROTOTYPE = false` yapılması.
- [ ] **7.2.** Tüm odalarda karakter yürüyüş/çarpışma (`CollisionFidelity`), görüş hattı ve canlı FPS (`BulkMoveTo` + statik GPU `Content` bütçesi) son kabul testi.

---

## 4. MODELLENECEK TÜM 3B VARLIKLAR ENVANTERİ (`GLB` LİSTESİ)

> **Kural:** Mevcut onaylı 4 model korunur. Yeni yapılacak **14 modelin her biri** önce çevrimdışı render/önizleme ile sana gösterilip onayın alındıktan sonra Studio’ya aktarılır.

| Kod | Model Adı (Hedef `.glb`) | Durum | Hareketli Alt Parçalar / Teknik Not |
|---|---|---|---|
| **M01** | `REACTOR_CORE_MANYETIK_01.glb` | **Onaylı & Sahnede** | Merkez referans ankrajı; katı küreleri gizli, canlı 3B `EditableMesh` çekirdek aktif. |
| **M02** | `REACTOR_EMITTER_REV03.glb` (×6) | **Onaylı & Sahnede** | `NOZZLE__white`, `OPTIC__cyan`, `WINDOW__cyan_core`, `ANTENNA__*`; rijit `19.8` stud strok. |
| **M03A** | `REACTOR_WALL_HATCH_THROUGH_01.glb` (×2) | **Onaylı & Sahnede** | Sol/sağ gerçek geçiş deliği; `LEAF_LEFT` ve `LEAF_RIGHT` (`±5.85` stud). |
| **M03B** | `REACTOR_PISTON_GUIDE_01.glb` (×6) | **Onaylı & Sahnede** | `BASE`, `GUIDES`, `STAGE1/2/3`, `PUSHER` 3 kademeli teleskopik aktüatör. |
| **M06** | `REACTOR_SIDE_WALLS_OCTAGONAL_IRON_REV03_DIAG_OPEN.glb` | **Onaylı & Sahnede** | Çok tonlu arduvaz/grafit/zeytuni-demir sekizgen yan duvarlar + açık alt çapraz portlar. |
| **M07** | `REACTOR_CROWN_DECK_AND_RADIAL_PORTS_01.glb` (4 kapak) | **Onaylı & Sahnede (Rev2)** | `UPPER`, `LOWER`, `LOWER_LEFT`, `LOWER_RIGHT` gerçek açılır kapaklı zırhlı yuvalar (`±5.85` stud) + `%100` düz ve okunaklı `SL-00/03/04/05` plakaları. |
| **M08** | `REACTOR_REAR_TURBINE_AND_PLENUM_01.glb` | **Onaylı & Sahnede (Rev2)** | 10 kanatlı keskin CNC döner türbin fanı + krom-nikel tahrik mili + cıvatalı rulman yatağı + çift 8-kollu dökme demir stator taşıyıcıları + zırhlı üst HVAC kondenser kanalı. |
| **M09** | `REACTOR_REAR_BULKHEAD_IRON_REV05_TURBINE_PORT.glb` | **Onaylı & Sahnede** | Dairesel fan boğazlı ve çok tonlu grimsi-demir kaburgalı arka zırh duvarı. |
| **M10** | `OBSERVATION_WINDOW_ARMOR_FRAME_01.glb` | **Onaylı & Sahnede** | 3 bölmeli kontrol odası zırhlı cam dikmeleri (`X = ±11.25`) + sekizgen ön sızdırmazlık contası. |
| **M11** | `REACTOR_COOLANT_PIPING_RING_01.glb` | **Sahnede — Rev2 360° Play Doğrulandı** | Gerçek içi delik (`hollowPipe`) çelik borular, açık boğazlı ANSI flanşlar, ön/arka zırhlı şalt & kollektör dolapları, kondenser plenum tavan/yan bağlantıları (`%0` kesik uç) ve 4 adet `PIPE_SPOOL_*` modülü. |
| **M12** | `PISTON_REAR_SERVICE_BAY_01.glb` (×6 / Modüler) | **Sahnede — Rev2 360° Play Doğrulandı** | 6 piston arkasında `35.5` stud derinlikli servis galerileri: kesintisiz tavan/akümülatör devresi, `BRACKETS__frame` 4 köşe ray manşon bağlantısı, 3 dövme çelik piston kaidesi, dış manşon ve `%100` düz `MAINT-BAY` yazıları. |
| **M13** | `DAMAGE_PIPE_RUPTURE_KIT_01.glb` | ✅ **Tamamlandı + onaylandı + Studio'ya gizli monte edildi (28.10.2026)** — `FAZ4_DamageAssets` betiği, 32 MeshPart + 8 ağız ankrajı, Play değişim kanıtı alındı. Hacimsel sızıntı hunisi 4.2 kapsamında ankrajlara bağlanacak. | Patlayan boru flanşları, yırtılmış metal ağızlar ve kopan kelepçe parçaları. |
| **M14** | `DAMAGE_GLASS_FRACTURE_STAGES_01.glb` | **Modellenecek (Faz 4)** | Gözlem camı için 3 kademeli gerçek 3B çatlak ve kırık cam parçaları seti. |
| **M15** | `CONTROL_CONSOLE_MAIN_LOW_01.glb` | **Modellenecek (Faz 5)** | Görüşü kapatmayan alçak merkezi kontrol masası + hareketli `POWER`, `COOLANT`, `LASERS`, `E-COOLANT`, `IGNITION`, `SHUTDOWN` mekanizmaları. |
| **M16** | `SCRAM_PEDESTAL_AND_RISING_CORE_DESK_01.glb` | **Modellenecek (Faz 5)** | Şeffaf kapaklı `SCRAM` kürsüsü + hidrolikle yerden çıkan 3 kart yuvalı `ARMED SHUTDOWN` konsolu. |
| **M17** | `CONTROL_ROOM_SHELL_AND_CEILING_01.glb` | **Modellenecek (Faz 5)** | Kontrol odası duvarları, ekran nişleri ve tabelayı örtmeyen endüstriyel tavan armatürleri. |
| **M18** | `SERVICE_CORRIDORS_AND_AIRLOCK_01.glb` | **Modellenecek (Faz 5)** | Sol/sağ servis koridorları ve iki kanatlı otomatik hava kilidi kapıları. |
| **M19** | `AUTH_KEYCARD_LOCKERS_AND_CARDS_01.glb` | **Modellenecek (Faz 5)** | 6 fiziksel güvenlik dolabı ve taşınabilir/yuvalara takılabilir `AUTH 01/02/03` kart modelleri. |
| **M20** | `BLAST_BUNKER_CHAMBER_01.glb` | **Modellenecek (Faz 5)** | Patlamadan 11 sn önce kapanan ağır hidrolik zırh kapılı acil durum sığınağı. |

---

## 5. KORUNACAK KIRMIZI ÇİZGİLER (HİÇBİR FAZDA BOZULMAYACAK KURALLAR)

1. **`%0` 2B Efekt Zorunluluğu:** Çekirdek, lazer, buhar ve oda bulutsusunda `ParticleEmitter`, `BillboardGui` veya 2B `Beam` kullanılmaz; tamamı yüksek poligonlu 3B `EditableMesh` + `SurfaceAppearance` olarak kalır.
2. **Eşzamanlı ve Eşit Boylu 6 Lazer (`V15`):** 6 lazer asla sırayla teker teker yanmaz; `mask: 0 -> 63` tek anda ateşler, 6’sı da eşit boyda tam `FOCUS = (0, 26.5, 2.70)` merkezinde buluşup reaktörü başlatır ve sağ/sol açılardan çekirdek içi asla görünmez.
3. **Buhar Fiziği:** Yalnızca 6 gerçek `NOZZLE__white` ağzından çıkar ve aşağı sarkmadan düz ilerler.
4. **Aydınlatma Disiplini:** Dış ışıklar duvar veya yayıcı malzeme renklerini ağartmaz; kontrol odasının fiziksel elektriği startup kararmasında kesilmez; tam ekran kırmızı filtre veya kör edici sis kullanılmaz.
5. **Yasaklı Eski Parçalar:** Siyah merkez diski, çekirdeği örten panjur, sahte turuncu R5 hasar küreleri, `Model 06 Rev01` ve startup kamera sarsıntısı kesinlikle geri getirilmez.
6. **Canlı Kanıt ve Bildirim:** Her faz sonunda gerçek Studio Play doğrulaması yapılır ve kullanıcıya soru/onay sunulmadan hemen önce `notify_user` ile sesli bildirim çalınır.

## Rev4.1 — Cift-Dunya (Duplicate World) Sizinti Duzeltmesi (28.10.2026)

- **Kok neden:** `Edit` modunda birakilan `Workspace.CORE_PROTOCOL_V2_WORLD`, `Play` acilisinda sahneye kopyalaniyor; `REACTOR_MESH_CONTROLLER` / `Faz3` / `ReactorPilot_*` `WaitForChild` ile bu ILK ornege baglaniyor, `CORE_PROTOCOL_Server` ise `previous:Destroy()` edip IKINCI dunyayi yaratiyordu. `"03_STAR_REACTOR"` gizlemesi silinen ornekte kaliyor, eski R5 sivi kolonlari (`ACTIVE_BLUE_WATER`) sahnede kaliyordu.
- **Uygulanan duzeltme:** Studio `Edit` icindeki tum `CORE_PROTOCOL_V2_WORLD` kopyalari silindi (`removed_count = 1`, `world_left_in_edit = 0`); `Faz3_PipingAndServiceBays.server.lua` icindeki Heartbeat surucusune `world.Parent ~= Workspace` yeniden-baglanma korumasi eklendi ve Studio'ya yazildi (`Faz3 source = 62.118 B`, `faz3_has_guard = true`).
- **Kural:** `Play` baslatilmadan once `Edit` `Workspace` icinde `CORE_PROTOCOL_V2_WORLD` kesinlikle bulunmamali ve `Edit` modunda `CORE_PROTOCOL_Server` calistirilmamali.
