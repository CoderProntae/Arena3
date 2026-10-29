# Çalışma Alanı Transferi ve Roblox Studio MCP Analizi

**Tarih:** 28 Ekim 2026 — yeni sohbetin devir belgesi
**Kaynak:** GitHub `CoderProntae/Arena` içindeki çalışma alanı ZIP'i (328 dosya, ~54 MB)
**Proje:** AEGIS Reaktörü — `AEGIS_Reactor.rbxlx` (referans: *A Core Game* klibi; birebir kopya iddiası yok, özgün/prosedürel uygulama)

> **Sürüm kuralı (kullanıcının dediği gibi):** Belgeler kronolojiktir, çelişkili değildir. Eski sürümün dosyası yeni sürümde yoksa emeklidir; tarihsel denetim için saklanır. En güncel otorite: `AEGIS_REAKTOR_ANA_YOL_HARITASI_VE_MODELLEME_PLANI.md` (28.10.2026, Rev4.1 dahil) + `reactor_startup/source/` altındaki Faz2/Faz3 modülleri. `reactor_startup/README_TR.md` ve `model_work/*ROADMAP*` daha eski anlık görüntülerdir.

---

## 0. Transferde yapılanlar (bu oturum)

| Adım | Sonuç |
|---|---|
| ZIP indirildi/açıldı, dosyalar önceki düzendeki gibi `/home/user` köküne yerleştirildi | 328 dosya / 54 MB (128 MB snapshot sınırı altında). Scriptler mutlak `/home/user` yolları kullandığı için kök düzen şart. |
| Orijinal ZIP yedeği | `.cache/workspace_backup/` altında (snapshot dışı; kaybolursa açılmış dosyalar kalıcıdır, sorun değil). |
| Eksik kütüphaneler, kodların beklediği `.cache` konumlarına kuruldu | `.cache/studio_pydeps` → `cryptography`; `.cache/modeldeps` → `numpy, pillow, trimesh`; `.cache/modelrender` → `pyrender, PyOpenGL`; `.cache/core_mock_deps` → `lupa`; `.cache/luau/` → Luau 0.701 ikilileri. |
| Python sözdizimi taraması (tümü) | Temiz. |
| Şifreli bus çevrimdışı tur testi (ağa dokunmadan) | `pack → unpack` OK (Fernet + zlib). |
| Luau parse (8 güncel dosya) | Tümü OK. Not: Yeni Luau'da `--only-parse` yok; `.cache/luau/luau-compile` yerine ince uyumluluk kabuğu kondu (`--only-parse` → `luau-ast`), eski `validate_checkpoint*.py` çağrıları bozulmadan çalışsın diye. Kalıcı kaynaklara dokunulmadı. |
| 1 adet GLB yükleme tur testi | OK (`REACTOR_EMITTER_REV03.glb`, 33 geometri). |
| Canlı galeri `0.0.0.0:8080` yeniden başlatıldı | Çalışıyor. Gizli ayar dosyasının 404 ile engellendiği doğrulandı. |
| Köprü durumu — **tek seferlik, salt-okunur** posta kutusu sorgusu (`community_admin.py status`; Studio'ya komut göndermez) | **`recent`: Windows köprüsü hâlâ ONLINE**, 16 araç duyuruyor (15 Studio MCP + `notify_user`). Bu oturumda **hiçbir Studio çağrısı (`CALL`) gönderilmedi**, `notify_user` bile çalınmadı. |

**Önceki modelin son yaptıkları bilinmiyor:** Son kayıtlı işler 28.10 16:33 UTC'ye kadar geliyor (çoğu `execute_luau`/`screen_capture`, toplam 2105 iş kaydı). Yol haritasındaki son güvenilir durum Rev4.1 "çift-dünya sızıntısı" düzeltmesidir. **Herhangi bir yazma işleminden önce salt-okunur Studio denetimi yapılmalı** (bkz. Bölüm 9).

---

## 1. ⚠️ Güvenlik notu — gizli ayar rotasyonu önerisi

Roblox kullanıcı adı/şifresi veya API anahtarı hiçbir dosyada yok; bu açıdan kimlik sızıntısı yok. **Ancak** GitHub'a giden ZIP'in içinde şunlar vardı:

- İki nesil `Roblox_Studio_MCP_Gizli_Ayar.json` (eski `ntfy.sh` çifti kökte, güncel `ntfy.envs.net` çifti `studio_bridge/provider_switch/` altında): rastgele konu adları + Fernet anahtarı.
- Emekli `Roblox_Studio_MCP_Bridge.py` içinde sabit kodlanmış eski relay erişim anahtarı (o relay artık yok, pratik riski düşük ama dosyada duruyor; galeri bu `.py` dosyasını da önizlemede sunabiliyor).

Repo kısa süreliğine de olsa herkese açıksa, bu konu+anahtar çiftini **sızmış kabul etmek** doğru olur; GitHub'dan silmek, indirmiş olabilecek kopyaları geri almaz. Şu an çalışan köprü TAM OTOMATİK olduğundan, bu ayara sahip biri teorik olarak onay beklemeden Studio işlemi kuyruğa sokabilir (komutlar yine yalnızca senin PC'nde köprü açıkken ve allowlist içindeki 15 araçla sınırlı çalışır; publish aracı yok, `.rbxlx` diske yazılamaz).

**Öneri (sen onaylarsan uygularım):** Yeni rastgele konular + yeni Fernet anahtarı üret, Windows tarafına yalnızca yeni JSON'u ver (eski köprüyü `Ctrl+C` ile kapatıp yenisiyle başlat), eski çiftleri arşivle. Bu yapılana kadar köprüyü yalnızca aktif çalışırken açık tut. rotasyon yapılmadan yeni Studio işine girilmesini önermem.

Galeri tarafında: `live_gallery_server.py`, `Roblox_Studio_MCP_Gizli_Ayar.json` adını her konumda engelliyor (test edildi: 404). Ama iş kayıtları/ekran görüntüleri gibi diğer dosyalar önizleme adresinden görülebilir; adres tahmin edilemez olsa da galeriyi iş bitince kapatmak iyi pratik.

---

## 2. Proje soy ağacı — neyin yerine ne geçti

1. **HELIOS-9 V1–V4** — eski, ayrı proje (3 kumanda / ~3 dk / HUD). Emekli; yalnızca tarihsel referans.
2. **CORE PROTOCOL V1 → V2 → V3** — camlı kontrol odası + altı yayıcılı çekirdek + 435 sn meltdown'un ilk nesilleri.
3. **CORE PROTOCOL REMAKE (R5) + MESH_INTEGRATED** — güncel ana hat:
   - `CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua` (3882 satır) — oynanış/startup/aydınlatma/rölelerin tek sunucu yetkilisi.
   - `CORE_PROTOCOL_REMAKE_Client.client.lua` — güncel istemci.
4. **reactor_startup/** — "kapılı" startup geliştirme hattı (Bölüm 6).
5. **AEGIS Ana Yol Haritası** — hepsini tek çatıda toplayan Faz 1–7 planı:
   - **Faz 1** Startup V14D/V15: ✅ tamamlandı, onaylandı, `Ctrl+S` kaydedildi.
   - **Faz 2** Paket A (sekizgen oda kabuğu, 4 radyal kapak, arka türbin+plenum): ✅ tamamlandı/onaylandı.
   - **Faz 3** Paket B (borulama halkası M11 + piston arkası servis galerileri M12): Studio montajı + canlı Play tamam; yol haritasında kullanıcı kabulü bekliyor görünüyor. 28.10 Rev4.1 ile çift-dünya sızıntısı düzeltmesi uygulandı (Edit'teki artık `CORE_PROTOCOL_V2_WORLD` kopyası silindi; Faz3 sürücüsüne `world.Parent ~= Workspace` yeniden bağlanma koruması).
   - **Faz 4–7** (gerçek hasar modelleri, kontrol odası/koridor/bunker, startup dışı modlar, ses) henüz başlamadı.

Kritik kalıcı kural (Rev4.1): **Play öncesi Edit `Workspace` içinde `CORE_PROTOCOL_V2_WORLD` bulunmamalı**; Edit modunda ana sunucu scripti çalıştırılmamalı (çift dünya + silinen örneğe bağlanma bug'ı).

---

## 3. MCP bağlantısı — dört nesil evrim

Ortak ilke hiç değişmedi: Windows PC'de **dinleyen port açılmaz**. Köprü, Roblox'un kendi yerel MCP sunucusunu başlatır:

```
%LOCALAPPDATA%\Roblox\mcp.bat   →   cmd.exe /d /c .\mcp.bat   (StdioMCPClient, subprocess)
     ↕ stdio üzerinden satır bazlı JSON-RPC 2.0 (initialize → notifications/initialized → tools/list → tools/call)
```

`initialize` sırayla `2025-06-18`, `2025-03-26`, `2024-11-05` protokol sürümlerini dener; `tools/list` sayfaları toplanır (Studio 28 araç duyurur) ama **yerel allowlist** yalnızca 15'ini geçirir:

- **Salt-okunur (9):** `list_roblox_studios`, `get_studio_state`, `search_game_tree`, `inspect_instance`, `script_search`, `script_grep`, `script_read`, `get_console_output`, `screen_capture`
- **Etkili (6):** `start_stop_play`, `execute_luau`, `multi_edit`, `character_navigation`, `user_mouse_input`, `user_keyboard_input`
- Her nesilde: publish/kaydetme aracı yok; 14 MB istek tavanı; `tools/call` zaman aşımı 180 sn; işlenmemiş istemci metotlarına `-32601` (yalnız `ping` cevaplanır).

### Nesil 1 — Canlı köprü + relay + tünel (EMEKLİ)
- Ajan tarafında `INCELEME/relay_server.py`: `0.0.0.0:$BRIDGE_PORT` (varsayılan **8765**), `ThreadingHTTPServer`.
- Uçlar: worker tarafı `/worker/hello|poll|result`, ajan tarafı `/admin/state|tools|queue|result|wait`; **ayrı worker/admin Bearer anahtarları** (admin anahtarı Windows paketine hiç girmezdi).
- Dışarı açma: önce Cloudflare Quick Tunnel (iki kez `530`), sonra localhost.run SSH/HTTPS tüneli (`*.lhr.life`); Windows istemcisinde adres `$env:ARENA_STUDIO_RELAY_URL` ile değiştirilebilir.
- Darboğaz: tüneller dakikalar içinde `530/502` ile kopuyordu → terk edildi. Kalıntıları: `Roblox_Studio_MCP_Bridge.py` + kökteki 4 adet `Roblox_Studio_MCP_Canli_Kopru*.zip` / `Kopru_SSH.zip` (içlerinde aynı relay'in kopyası + kurulum notu var).

### Nesil 2 — Şifreli posta kutusu, ntfy.sh (EMEKLİ — kota)
- `Roblox_Studio_Bus.py` (`EncryptedBus`) + `Roblox_Studio_MCP_Kalici_Kopru.py`: İki taraf da yalnızca **giden HTTPS** ile `ntfy.sh` üzerindeki rastgele `arena_studio_…` konularını yoklar. Tünel, dinleyen süreç, Arena önizleme anahtarı yok.
- Etkili her araç için Windows konsolunda **ayrı ayrı `YES`** onayı (uzun argümanlar incelenmek üzere geçici JSON'a yazılır, sonra silinir).
- Kalıntıları: kökteki Bus/Köprü/Gizli Ayar üçlüsü + `Roblox_Studio_MCP_Sifreli_Postakutusu.zip`. **ntfy.sh günlük kotası dolunca** emekliye ayrıldı.

### Nesil 3 — Sağlayıcı değişimi: ntfy.envs.net + kota disiplini (GÜNCEL TAŞIMA KATMANI)
- Klasör: `studio_bridge/provider_switch/`. Bus yalnızca `https://ntfy.envs.net`e izin verir (host allowlist kodda kilitli). Yeni konu çifti + yeni anahtar.
- Kota ayarları: HELLO kalp atışı 155→**240 sn**, yoklama uykusu 7→**11 sn**, `since` pencereli okuma (eski ekran görüntüleri tekrar indirilmez), ajan tarafında HELLO önbelleği.
- **Ajan tarafı yöneticisi — `community_admin.py`** (Bölüm 5).
- Ara varyant **STARTUP_OTOMATIK**: `make_startup_auto_bridge.py` üretir; yalnızca bilinen Studio örneğinde Play aç/kapat + Edit'te belirli script yollarına (`CORE_PROTOCOL_Server`, `REACTOR_MESH_CONTROLLER`, `CORE_PROTOCOL_Client`, `STARTUP360_*`) sınırlı `multi_edit` otomatik geçer, gerisi sormadan **reddedilir**. Elle onaylı asıl dosyaya dokunmaz.

### Nesil 4 — TAM OTOMATİK (kullanıcının açık isteğiyle)
- **V1** (`TAM_OTOMATIK_KOPRU.zip` içindeki 316 satırlık dosya, `FULL_AUTO_ALL_TOOLS_V1`): 15 aracın tamamı konsol onayı beklemeden çalışır (Luau ile `:Destroy()` dahil).
- **V2 ALARM** (güncel: kökteki ve `provider_switch` altındaki `..._TAM_OTOMATIK.py`, 493 satır, `FULL_AUTO_ALL_TOOLS_V2_ALARM`): V1 + yerel 16. araç **`notify_user`** — bellekten sentezlenen WAV melodiyi `winsound` ile varsayılan kulaklık/hoparlörden çalar + odak çalmayan Windows tepsi baloncuğu gösterir (modlar: `done/question/review/test`, tekrar 1–4). Açılışta `test` melodisiyle kendini doğrular.
- HELLO zarfındaki `auto_policy` alanı hangi politikanın aktif olduğunu duyurur; ajan tarafı bunu iş kayıtlarında görebiliyor.

### Şifreli zarf protokolü (`EncryptedBus`)
- Paketleme: `Fernet( zlib-9( JSON ) )`; başlıklar `ArenaStudioEncryptedV1` (parça manifesto: `ArenaStudioChunkV1`).
- Boyut katmanları: ≤3500 B → satır içi mesaj; ≤1,75 MB → ek dosya; daha büyüğü (ekran görüntüsü vb.) → ayrı şifreli parçalar + SHA-256'lı şifreli manifesto (en fazla 9 parça). Sert tavan: 14 MB (şifresiz açılışta da taşma koruması var).
- Ek URL'leri yalnızca `https://<seçili host>/file/…` kabul edilir; kimliği doğrulanamayan/bozuk/şişkin veri sessizce yok sayılır, asla çalıştırılmaz.
- Mesaj tipleri:
  - `HELLO` (Windows → responses): `{session: token_hex(16), tools: [şemalar], auto_policy?, time}` — başlangıçta 8 denemeye kadar artımlı beklemeyle; sonra her 240 sn'de bir.
  - `CALL` (ajan → commands): `{job: uuid4hex, session, tool, arguments, time}` — worker; oturum eşleşmesi, tek seferlik job (dedupe kümesi), zaman penceresi (−900/+120 sn) ve allowlist kontrolü yapar.
  - `RESULT` (Windows → responses): `{job, tool, ok, response: <JSON-RPC yanıtı>, time}`. Yayın başarısız olursa **etkili çağrı tekrarlanmaz** (çift uygulama riski).

---

## 4. Portlar — ne, nerede, nasıl açıldı

| Servis | Taraf | Bağlama | Dışarı açma yolu | Durum |
|---|---|---|---|---|
| `mcp.bat` (Roblox Studio MCP) | Windows | **Port yok** (stdio alt süreci) | — | Güncel |
| Windows köprü istemcileri (tüm nesiller) | Windows | **Dinleyen port yok**; yalnızca giden HTTPS | — | Güncel ilke |
| `relay_server.py` | Ajan sandbox | `0.0.0.0:8765` (`BRIDGE_PORT`) | Cloudflare Quick Tunnel → localhost.run SSH tüneli (geçici genel HTTPS adresi) | Emekli (tünel kararsızlığı) |
| `live_gallery_server.py` | Ajan sandbox | `0.0.0.0:8080` (`GALLERY_PORT`) | Arena canlı önizleme proxy'si: `https://8080-<sandboxId>.e2b.app` (sandbox değişince host değişir; eski adres geçersiz) | **Şu an açık** |
| ntfy posta kutusu istemcisi (`community_admin.py`) | Ajan sandbox | **Port yok**; her komut kısa ömürlü giden HTTPS yoklaması | — | Güncel |

Galeri ayrıntıları (`studio_bridge/live_gallery_server.py`, 857 satır, yalnızca stdlib):
- Başlatma: uzun ömürlü süreç olarak `python3 studio_bridge/live_gallery_server.py` (çalışma dizini `/home/user`).
- Kökü `/home/user` tarar; görsel (en yeni 120), model/GLB+ZIP (60), belge/kod (80) listeler.
- Yollar: `/`, `/api/state` (JSON tarama), `/api/render_md?path=…`, `/view/<yol>` (biçimlendirilmiş Markdown sayfası), `/raw/<yol>` (asıl dosya; `.md` doğrudan gezinmede de biçimli açılır, `?download=1` indirir).
- Tamamen göreli URL'ler, her Host/Origin kabulü, iframe gömmeye izin; harici CDN yok (Markdown çevirici dosyanın içinde).
- Güvenlik: yol kaçış koruması (`/home/user` dışı çözümlenemez) + ada göre gizleme (`Roblox_Studio_MCP_Gizli_Ayar.json`, `.git`, `.netrc`, `.git-credentials`); `.cache` içinde yalnızca iki izinli alt klasöre inilir; bazı bağımlılık klasörleri tarama dışı.

---

## 5. Ajan tarafı işletim — komutlar ve disiplin

Her şey `studio_bridge/provider_switch/community_admin.py` üstünden yapılır. **Bu dosyayı kendi klasöründen çalıştırmak gerekir**: Python, script klasörünü import yoluna başa koyduğu için `Roblox_Studio_Bus`'un *envs.net* sürümü yüklenir. Kökten yanlış Bus ile güncel ayarı açmaya çalışmak "only supports ntfy.sh" hatasıyla güvenle başarısız olur (bu oturumda canlı görüldü; dosya çiftlerini karıştırmama kuralı).

```powershell
# (ajan sandbox'ında, kabuk)
cd studio_bridge/provider_switch
PYTHONPATH=/home/user/.cache/studio_pydeps python3 community_admin.py status
PYTHONPATH=/home/user/.cache/studio_pydeps python3 community_admin.py tools
PYTHONPATH=/home/user/.cache/studio_pydeps python3 community_admin.py schema execute_luau
PYTHONPATH=/home/user/.cache/studio_pydeps python3 community_admin.py call script_read @istek.json
PYTHONPATH=/home/user/.cache/studio_pydeps python3 community_admin.py wait <job> 120
PYTHONPATH=/home/user/.cache/studio_pydeps python3 community_admin.py result <job>
```

Kayıt düzeni:
- `community_jobs.json`: her işin `{session, tool, queued}` kaydı (aktarımda 2105 iş: 508 `screen_capture`, 498 `execute_luau`, 352 `start_stop_play`, 228 `multi_edit`, … 12 `notify_user`).
- `community_results/<job>.json` + görüntü içerikleri ayıklanıp `<job>_1.jpg/png` olarak yanına yazılır (PNG/JPEG sihirli bayt doğrulamasıyla).
- `community_active_hello.json`: son kimliği doğrulanmış HELLO önbelleği (260 sn taze sayılır; ağ hatasında 350 sn'ye kadar yedek). **HELLO 260 sn'den eskiyse `call` reddedilir** — ölü köprüye değişiklik kuyruğa sokulmaz.
- Sonuçlar yalnızca işin kuyruğa girdiği andan sonrası (`since`) taranarak alınır; kota dostu yoklama (11 sn, hız sınırında 12 sn soğuma).
- Argümanlar düz JSON veya `@dosya` ile verilir. Önceki iş paketleri klasörde duruyor: `patch_*_request.json` (çoklu düzenleme yamaları), `qa_*_enable/disable.json` (Play QA için `STUDIO_AUTO_STARTUP` gibi bayrakları açıp kapatan tek satırlık `multi_edit` paketleri), `audit_*` / `inspect_*` (salt-okunur Luau denetimleri — çıktıyı `HttpService:JSONEncode` ile döndürme kalıbı; yazan Luau'larda `game.Name == "AEGIS_Reactor.rbxlx"` bekçisi).
- Üst katman `reactor_startup/tools/studio_bus.py`: anahtarlı, kaldığı yerden süren istek günlüğü (`reactor_startup/qa/studio_jobs.json`); yalnızca 7 araca izin verir; >80 KB argümanı dosyaya yazar; aynı anahtar+farklı argüman = sert hata (kısmen uygulanmış işin üstüne çelişki yazmayı engeller). Komutu aynen tekrarlamak kaldığı yerden devam eder.

Windows tarafı (güncel tarif):
1. Studio açık, doğru yerin **yedeği** alınmış, Asistan → MCP ayarlarında "Studio'yu MCP sunucusu olarak etkinleştir" açık.
2. Aynı klasörde üç dosya: `Roblox_Studio_MCP_Kalici_Kopru_TAM_OTOMATIK.py` + **envs.net sürümü** `Roblox_Studio_Bus.py` + `Roblox_Studio_MCP_Gizli_Ayar.json`. Bir kez: `python -m pip install cryptography`.
3. `py -3 .\Roblox_Studio_MCP_Kalici_Kopru_TAM_OTOMATIK.py` → `Server advertises … tools` + `ONLINE` + test melodisi. `Ctrl+C` = anında kes.
4. Her onaylı aşamadan sonra Studio'da **`Ctrl+S`** (MCP, `.rbxlx`i diske yazamaz; değişiklik açık oturumdadır).

Köprü ID disiplini: İstekteki `studio_id` asla tahminen yazılmaz; önce `list_roblox_studios` çağrılır, kimlik o listeden alınır (eski oturumların kimliği yeni oturumda geçerli sayılmaz).

---

## 6. Oyun (Luau) mimarisi — güncel yığın

| Dosya | Satır | Rol |
|---|---:|---|
| `CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua` | 3882 | Ana oynanış sunucusu: fiziksel kontroller (sunucuda doğrulanan her tıklama), durum makinesi (COLD/STARTUP/ONLINE/MELTDOWN 435 sn +320 sn imzası/başarılı-başarısız shutdown/freezedown), aydınlatma bütçesi, altı rölenin tek yetkilisi. Dünya öznitelikleriyle yayın yapar (`ReactorMeshSignal`, `ReactorMode`, `ReactorStartupAge`, …) — istemciden mod kabul etmez. |
| `CORE_PROTOCOL_REMAKE_Client.client.lua` | 292 | İstemci: kamera/etkileşim geri bildirimi; kalıcı HUD yok (metinler dünya içi `SurfaceGui`). |
| `model_work/studio_import/REACTOR_MESH_CONTROLLER.server.lua` | 423 | Startup dışı GLB hareket/hasar/ONLINE denetimi. `REACTOR_MESH_ASSEMBLY` (STATIC/MOVING) + 6 başlık (`EmitterModuleCount == 6`) yoksa sahte ışın üretmeyi reddeder; eski Part projektör klasörünü yalnızca Play'de emekliye ayırır. |
| `reactor_startup/source/ReactorPilot_SixHeads.server.lua` | 358 | Startup mekanik pilotu: 6 onaylı GLB başlık/piston/kapağın rijit hareketi + senkron durum skalerlerinin (Fuel, Darkness, RelayMask, Cyan/WhiteVolume) tek yayıncısı. Kontrol 05'te bekler, ONLINE'a kendiliğinden geçmez. |
| `reactor_startup/source/ReactorPilot_CustomVapor.client.lua` | 1890 | 60 FPS gerçek 3B hacimsel motor (istemci): düz eksenli buhar (6 gerçek `NOZZLE__white` ağzı, yerçekimi 0), 3B `EditableMesh` bulutsu çekirdek, donanım Z-tamponuyla çekirdek içi ışın gizleme, V15 eşzamanlı 6 lazer görselleştirmesi. |
| `reactor_startup/source/ReactorPilot_CustomFlow.server.lua` | 13 | "%0 2B efekt" politikasını dünya öznitelikleriyle ilan eden küçük sunucu eşlikçisi. |
| `reactor_startup/source/Faz2_ChamberAndTurbine.server.lua` | 1546 | Faz 2 sahne modülü (üretilmiş gömülü geometri; açılışta `EditableMesh → MeshPart`, canlı `EditableMesh` sızıntısı 0/8). |
| `reactor_startup/source/Faz3_PipingAndServiceBays.server.lua` | 1268 | Faz 3 sahne modülü (129 `MeshPart`); Rev4.1 yeniden bağlanma korumasının yerel kopyası. |

Önemli yapılandırma (ana sunucu `CFG`, yerel kopyadaki hali): `STUDIO_AUTO_STARTUP=false`, `STUDIO_AUTO_MELTDOWN=false`, `SILENT_PROTOTYPE=true` (izinsiz katalog sesleri kapalı), `MELTDOWN_SECONDS=435`, `RESET_DELAY=57`, `SHUTDOWN_RESCUE_UNTIL=270`, etkileşim mesafesi 11 stud, bloom/pozlama bütçeleri bilinçli kısık.

**Gerçeğin kaynağı Studio'daki `Source`lardır.** Yamalar `multi_edit` ile Studio'ya işlendiğinden yerel kopyalar Studio'dan geride kalabilir; düzenleme öncesi `script_read` ile canlı kaynak çekilip karşılaştırılmalı. `studio_bridge/provider_switch/studio_server_before_mesh_integration.lua` (3718 satır) entegrasyon öncesi güvenlik kopyasıdır.

Kırmızı çizgiler (hiçbir fazda bozulmaz): %0 2B efekt (`ParticleEmitter`/`BillboardGui`/düz `Beam` yok — her şey 3B `EditableMesh`+`SurfaceAppearance`); lazerler sırayla değil `mask 0→63` tek adımda ve eşit boyda (`FOCUS=(0, 26.5, 2.70)`); buhar yalnızca 6 gerçek ağızdan, sarkmadan düz; startup'ta kamera sarsıntısı yok; kontrol odası elektriği kararmada kesilmez; yasaklı eski parçalar geri gelmez (siyah merkez disk, panjur, turuncu R5 küreleri, Rev01 yan duvar); faz sonunda gerçek Play kanıtı + onaydan önce `notify_user`.

Kontrol kapıları (`reactor_startup/`): 01 COLD/fiziksel komut, 02 yakıt, 03 kararma, 04 altı röle+cyan onaylı; 05 beyaz plazma ve 06 ONLINE geçişi V14D/V15 dalıyla Faz 1 kapsamında canlı doğrulandı/onaylandı (en güncel kayıt yol haritası). QA betikleri: `reactor_startup/qa/validate_checkpoint01..05*.py` (Luau parse + kanıt dosyası karmaları) ve çevrimdışı yapısal testler `CORE_PROTOCOL_*_StaticChecks.py` + lupa tabanlı sahte-Roblox koşumları `references/core_mock_*` — hiçbiri gerçek Play'in yerine geçmez.

---

## 7. 3B model hattı

**Üretim (çevrimdışı):** `model_work/*/*.py` — `trimesh` ile prosedürel geometri + gömülü PBR dokular, `pyrender` (EGL) ile onay görselleri; yazar koordinatları X-yatay / Y-derinlik / Z-yükseklik, "1 kaynak birimi = 1 stud", paylaşımlı merkez `ORIGIN=(0, 26.5, 0)`. Her model ayrı önizleme + kullanıcı onayından geçer; reddedilen revizyonların kaynakları denetim için kalır, çıktıları `.cache`e atılır ("ahşap görünümlü", "yama gibi", "düz/yakın" gibi gerekçeler `model_work/MODEL_REVIEW_STATUS.md`de kayıtlı).

**Studio'ya taşımanın iki yolu kullanıldı:**
1. **Elle GLB içe aktarma (ilk 7 model):** MCP, Linux çalışma alanındaki GLB'yi okuyamaz. `model_work/studio_import/prepare_studio_pack.py` yazar uzayından glTF Y-up'a döndürülmüş kopyaları paketler; kullanıcı Studio'nun kendi GLB aktarıcısıyla yerelden alır; sonra `install_existing_models.lua` tek seferlik kurulumcusu `execute_luau` ile çalıştırılır: MeshPart sayısı/boyut ön kontrolleri, 180° yön düzeltmesi, malzeme renklerinin geri verilmesi, `REACTOR_MESH_ASSEMBLY` altında STATIC/MOVING gruplaması, özgün aktarımlar `ServerStorage`da yedekte. Herhangi bir iddia (assert) tutmazsa kurulum geri alınır.
2. **Gömülü Luau geometrisi (Faz 2/3):** `model_work/crown_deck_ports/compile_faz2_studio_modules.py` onaylı GLB'leri Studio uzayına `(x, 26.50+z, −y)` dönüşümüyle, MCP ile güvenli taşınabilen <72 KB'lık `ModuleScript` parçalarına ("chunk") derler; sahne modülü açılışta `AssetService:CreateEditableMesh → CreateDataModelContentAsync → CreateMeshPartAsync` ile kalıcı `MeshPart` üretir, üretici `EditableMesh`leri yok eder.

**Envanter (özet):** `model_exports/` altında 15 GLB var — onaylı çekirdek set `REACTOR_CORE/EMITTER_REV03/WALL_HATCH_THROUGH/PISTON_GUIDE/REAR_SERVICE_GRILLES` + Faz 2/3 seti (`SIDE_WALLS…REV03_DIAG_OPEN`, `CROWN_DECK_AND_RADIAL_PORTS`, `REAR_TURBINE_AND_PLENUM`, `REAR_BULKHEAD…REV05`, `OBSERVATION_WINDOW_ARMOR_FRAME`, `COOLANT_PIPING_RING`, `PISTON_REAR_SERVICE_BAY`, slate_02 varyantları). Yol haritası Bölüm 4'teki M01–M20 tablosu otoritedir; M13–M20 (hasar kiti, cam kırığı, konsollar, koridorlar, kart dolapları, bunker) Faz 4–5 işidir. Onaylı GLB'ler onaysız değiştirilmez; ölçek sorunu çıkarsa geometri değil yerleştirme ayarlanır.

---

## 8. Transferde eksik olanlar (bilinçli/bilinçsiz kayıplar)

Bunlar ZIP'te yok; çoğu `.cache` (snapshot dışı) alışkanlığının beklenen sonucu. Kritik olanı: **oyunun gerçek durumu kullanıcının PC'sindeki `AEGIS_Reactor.rbxlx` + açık Studio oturumunda**; yerel eksikler Studio denetimiyle telafi edilebilir.

- `.cache` bütünü: kurulu bağımlılıklar (yeniden kuruldu), reddedilen GLB çıktıları, ham renderlar, `studio_ready` paket ara dosyaları, referans video yerel kopyası (yeniden indirme adresi + SHA-256 `references/Video_Ilk_Cozumleme.md`de).
- `uploads/` (kullanıcı referans görselleri), `reports/` içindeki KONTROL_01–05 Play kanıt görselleri, `reactor_startup/qa/*_approval.json` ve `studio_jobs.json`, `model_work/studio_import/faz2_luau/` parçaları, `REACTOR_STUDIO_TEK_PAKET.zip`, 490 yanıtlık tar arşivi. (Arşiv notuna göre bir ara 252 dosya snapshot'a girememiş; bu kayıp geriye dönük onarılamaz.)
- `community_results` yalnızca 34 dosya (2105 işe karşılık) — geri kalan sonuçlar/ekran görüntüleri aktarımda yok.
- Bazı ada göre anılan GLB'ler (örn. `REACTOR_REAR_BULKHEAD_IRON_REV04.glb`, açık poz inceleme GLB'si) yok; yerlerine yeni revizyonları (REV05 vb.) var — sürüm kuralıyla tutarlı.

---

## 9. Şimdi neredeyiz & önerilen sonraki adım

- Köprü **şu an çalışır durumda** (Windows'ta TAM OTOMATIK V2 açık görünüyor). Bu oturumda kasıtlı olarak yalnızca durum sorgusu yapıldı; Studio'ya yazan/Play başlatan/ses çalan hiçbir çağrı gönderilmedi.
- Bilinmeyen: önceki (kötü) modelin son mesajlarında Studio'da ne yaptığı. Bunu senin anlatımın + salt-okunur denetimle netleştirmeliyiz.

Onay verirsen ilk iş paketi (Studio'yu değiştirmeyen denetim):
1. `list_roblox_studios` → açık yeri ve güncel `studio_id`yi doğrula (eski kimliği varsayma).
2. `get_studio_state` (Edit/Play durumu) + Edit `Workspace`te artık `CORE_PROTOCOL_V2_WORLD` var mı (`search_game_tree`).
3. Ana scriptlerin canlı kaynaklarını `script_read` ile çekip yerel kopyalarla fark karşılaştırması (beklenmedik değişiklik var mı?).
4. `get_console_output` son hatalar; COLD durumda tek `screen_capture` ile görsel durum.
5. Sonuç raporu + `notify_user`, sonra karar: gizli rotasyon → Faz 3 kabul teyidi → Faz 4 (Paket C: M13/M14 hasar modelleri) sırası.

Bu denetim bile köprü kotası ve senin vaktini kullanır; başlat demeden başlatmayacağım. Ayrıca Bölüm 1'deki rotasyon kararını ve "kötü model en son ne yaptı / nerede kaldık" bilgin gelirse denetimi tam o noktalara hedeflerim.

---

## Ek — 28.10 kullanıcı kararları ve ortam notları (yeni sohbet)

- Önceki (kötü) model **hiçbir Studio işlemi yapmadı**; kullanıcı izin vermedi. Bu yüzden hasar denetimi gerekmiyor; kullanıcı kararıyla salt-okunur Studio denetimi de atlandı ("zaten çalışıyor").
- **`notify_user` kuralı güncellendi:** Kullanıcı genellikle ekranı izliyor; yalnızca "oyuna geçiyorum / ayrılıyorum / video izleyeceğim" dediğinde çal. Varsayılan: çalma.
- Render ortamı onarımı (snapshot'ta kalmaz, her yeni sandbox'ta tekrar gerekir): sistem GL kitaplıkları `sudo apt-get install -y libglu1-mesa libgl1 libegl1 libgles2`; `.cache/modeldeps` = numpy/trimesh yığını, `.cache/modelrender` = `pyrender 0.1.45 + PyOpenGL 3.1.7 (--no-deps)` + `freetype-py, six, networkx, pyglet 1.5.31`. Script başında `pyglet.options['headless']=True` gerekli olabilir.
- Geçici test modeli üretildi: `model_work/test_regulator/make_test_regulator.py` → `model_exports/TEST_KRIYO_REGULATOR_01.glb` + `_ONAY.png` (kullanıcı değerlendirmesi bekliyor; Studio'ya konmadı).
