# Sıfırdan startup — kapılı görsel geliştirme

Kullanıcı kuralı: **her evrede gerçek Studio Play testi/görüntüsü, ardından ayrı kullanıcı kararı**. Kontrol **01 / fiziksel altı başlık** ve **02 / altı gerçek `NOZZLE__white` ağzından özel yakıt-buhar akışı** onaylandı. **03 / karanlık hacim** gerçek Play üzerinden **koşullu kapsamıyla onaylandı**: ana odanın fiziksel ışıkları/göstergeleri kapanmıyor; küresel görüntü tonu bir miktar etkiliyor. **04 / ana çekirdek–lazer ve altı röle/cyan** kullanıcıca onaylandı, fakat katı çekirdeğin yapay görünmesi not edildi. **05 / efekt kaynaklı beyaz plazma hacmi** sıradaki kapıdır; **05–06 onaylanmadı**. Kullanıcı mevcut reaktör modellerinin ve oda ışık kalitesinin bu kararın konusu olmadığını belirtti.

## Kaynakların sahipliği

- `source/ReactorPilot_SixHeads.server.lua`: COLD başlangıcı; onaylı altı GLB başlığının/pistonların/kapakların rijit hareketi; 02’de gerçek ağızlardan yakıt; 03’te kararma; 04’te **ancak** R5’in ayrı ayrı açtığı altı doğrulanmış röleyle orijinal nozul soketlerinden cyan lazer ve mevcut GLB çekirdeğinde cyan GPU hacmi; **05 V13’te** `age=49..54` geçişinde katı GLB merkez yüzeylerini tamamen gizleyerek prosedürel bulut dokulu 6 Beam katmanı, 14 gezinen dış/kenar plazma kaynağı ve 5 kavisli ark ile doğal beyaz-kobalt plazma hacmine geçer (`WHITE_PLASMA_HOLD_FOR_USER_APPROVAL`). **ONLINE’a geçilmez; 05 kullanıcı kararı bekleniyor.**
- `source/ReactorPilot_CustomFlow.server.lua` ve `source/ReactorPilot_CustomVapor.client.lua`: altı farklı nozuldan özgün, çalışma anında üretilmiş dokuya bağlı yönlü akış. Hazır Roblox dumanı değil; geçici BillboardGui tanıları kaldırıldı. Onaylı kaynak konumlarını değiştirmeyin.
- Ana `CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua`: gerçek fiziksel kontroller, startup/aydınlatma ve altı rölenin tek server yetkilisi. 03’te reaktör servis lambalarını azaltır; kontrol odasının fiziksel ışıkları/göstergeleri kalır. 04’te her GLB piston/nozul konumunu ayrı doğrulayıp röleleri sırayla açar. Startup dışı hasar/meltdown akışı korunur.
- Mesh controller startup sırasında yalnız fiziksel başlık otoritesini Pilot’a bırakır; client startup kamerasında sarsıntı ve sahte merkez ışını yok. Onaylı altı GLB ve metal arka duvar değiştirilmedi; yeni görünür Part/model/ses eklenmedi. Eski Boot scriptlerinin Studio `Source`’ları boşaltıldı; önceki silme izni reddedildi, bunu başarılı silme saymıyoruz.

## Gerçek Play kanıtları ve QA

- [Kontrol 01 görseli](../reports/KONTROL_01_GERCEK_PLAY.png), `qa/checkpoint01_approval.json`.
- [Kontrol 02 kabul edilmiş görseli](../reports/KONTROL_02_ALTI_NOZUL_GERCEK_PLAY.png), `qa/checkpoint02_approval.json`; `python reactor_startup/qa/validate_checkpoint02_six_nozzles.py`.
- [Kontrol 03 karanlık gerçek Play karesi](../reports/KONTROL_03_KARANLIK_GERCEK_PLAY.jpg), [kapsamlı kullanıcı kararı](qa/checkpoint03_approval.json), [teknik rapor](qa/KONTROL_03_TEST_RAPORU_TR.md); `python reactor_startup/qa/validate_checkpoint03.py`.
- [Kontrol 04 cyan gerçek Play karesi](../reports/KONTROL_04_ALTI_GERCEK_LAZER_CYAN_CEKIRDEK_PLAY.jpg), [onay ve çekirdek görsel notu](qa/checkpoint04_approval.json), [teknik rapor](qa/KONTROL_04_TEST_RAPORU_TR.md); `python reactor_startup/qa/validate_checkpoint04.py`. Reaktör modeli/oda ışığı bu evrenin nihai kabul konusu değil; çekirdeğin yapay katılığı 05’te ele alınmalı.

## Kontrol 05: gerçek Studio Play kanıtı alındı, kullanıcı kararı bekleniyor

- [Kontrol 05 beyaz plazma gerçek Play karesi](../reports/KONTROL_05_EFEKT_BAZLI_BEYAZ_PLAZMA_PLAY.jpg), [teknik rapor](qa/KONTROL_05_TEST_RAPORU_TR.md); `python reactor_startup/qa/validate_checkpoint05.py`.
- **Kontrol 05 henüz onaylı değildir**; 06 / `ONLINE` aşamasına geçilmedi. Odanın fiziksel ışıkları/ekranları kesilmez; 05'te R5'in beyaz evre bloom ayarı global görünümü ölçülü etkiler, bu bir elektrik kesintisi değildir.
- Play oturumu durduruldu, Studio'da `STUDIO_AUTO_STARTUP=false` geri yüklendi ve `script_read` + COLD Play ile doğrulandı (`qa/checkpoint05_cold_final_attr.json`). Sesler `SILENT_PROTOTYPE=true`; elle fiziksel START tıklaması, hareket videosu, publish veya `.rbxlx` kaydı **yapılmadı**. Özgün varlıklar eksikken birebir oyun eşdeğerliği garanti edilemez.

Workspace bütçesi ve kayıpsız kanıt ayıklaması `../studio_bridge/provider_switch/ARCHIVE_NOTES_TR.md` içindedir. Büyük yeniden indirilebilir referans video `.cache` geçici alanındadır ve sonraki oturumda bulunmayabilir.
