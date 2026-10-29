# M14 cam + lazer — uygulama ve test kaydı

## Kullanıcı kararı
`reports/M14_REV2_STUDIO_UC_ACI.jpg` içindeki Rev2 çatlak görünümünün yönü kullanıcı tarafından kabul edildi. Önden, yandan ve yukarıdan görüntüler gerçek Studio Play çekimleridir. İleri aşamada görsellik ve parçalanma kalitesi tekrar değerlendirilebilir.

## Studio Edit'te yapılan değişiklikler
- `ServerScriptService.M14_GlassLaser_Controller` eklendi. Yerel kaynak `faz4/glass_laser/M14_GlassLaser_CONTROLLER_CANDIDATE.server.lua`, üretim kaynağı `build_controller.py`. Üç MeshPart, onaylanmış M14 Rev2 GLB'sinin geometri verisinden oyun başında üretilir. Geçici önizleme kitleri Edit'e kurulmadı.
- `ServerScriptService.CORE_PROTOCOL_Server`: 434. saniyede `FINAL_GLASS_LASER_BREAK` eklenip mevcut `shatterWindow()` çağrıldı. 435. saniye patlamasındaki eski idempotent yedek çağrı korunuyor. Yerel güncel kopya `CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua`; değişiklik öncesi yedek `CORE_PROTOCOL_Server_before_M14.lua.bak`.
- Normal üretim `STUDIO_AUTO_STARTUP=false`, `STUDIO_AUTO_MELTDOWN=false`, `STUDIO_PREVIEW_SECOND=0`: Studio scriptinden tekrar okunarak doğrulandı.

## Davranış
Server'ın mevcut `ReactorMode` / `ReactorMeltdownAge` özniteliklerini dinler. 143, 230, 327 saniyelerinde gerçek 3B mesh çatlak katmanları birikimli açılır; bu anlarda çekirdekten camdaki darbe noktasına 3B neon lazer görünür. 385. saniyede ilave darbe, 434. saniyede daha kalın final lazeri. 434. saniyede mevcut ana sunucu cam kırma kodunu çağırır; 435. saniyede patlama yedek olarak tekrar çağırır ancak durum guard'ı ikinci kez kırmayı engeller. AFTERMATH ve reset sırasında çatlak katmanları saklanır; ana script kendi cam resetini yürütür.

## Testler
- Geçici Play örneğinde kontrolcüye Studio-only bir QA BindableFunction ile sırasıyla 142→143, 229→230, 326→327, 384→385, 433→434, AFTERMATH, COLD enjekte edildi. Katmanlar 0→1→2→3, lazer nesneleri ve son lazer işareti, reset temizliği doğrulandı (`2903f1bada0e481487a4d0cc74932829.json`). Bu test gerçek meltdown simülasyonu yerine kontrollü girdidir.
- Kurulu script ile gerçek ana sunucunun Studio fast-forward modu 430. saniyeden başlatıldı. Olaydan sonra `ReactorMode=AFTERMATH`, `LastImpact=434`, `FinalImpact=true`, `Stage=0`, iki panoramik camın `Transparency=1`, `CanCollide=false` olduğu okundu (`0f6d20885e4c4dbfbc3c180fe8bca6f9.json`). Konsolda M14/Faz2/Faz3/Faz4 hazır ve AFTERMATH geçişi görüldü. Bu test 435 saniyenin tamamını normal hızda koşmadı.
- Play durduruldu. Test-only otomatik meltdown ve fast-forward ayarları kapatıldı ve kod okumasıyla doğrulandı. Studio'da yapılan değişiklikler kullanıcı tarafından henüz kaydedilmiş olarak doğrulanmadı.

## Önceki testte açık olanlar (29 Ekim final çalışması öncesi)
- Mevcut `shatterWindow` halen eski basit dikdörtgen Part parçalarını kullanır. Daha doğal, mekanik ve yönsel cam parçaları istenir; detaylı nihai kırılma henüz tamamlanmış sayılmaz.
- Lazer hedefleri çatlak merkezleriyle uyumlu sabit yerlerdir; engel algılama/raycast ve lazer enerjisinin kaynaktan cam yüzeyine fiziksel davranışı ayrıca doğrulanmadı.
- Normal zamanlı tam meltdown (435 sn), gerçek istemcide lazerin görsel doğruluğu, ses, performans, oyun modu etkileşimleri ve tüm tur reseti uçtan uca henüz test edilmedi. QA'daki reset yalnız kontrolcü katmanı/özniteliklerini kapsar.
- Edit mesh içeriklerinin Studio yeniden açıldıktan sonra kalıcılığı ayrı çözülmedi.

## 29 Ekim — Faz 4.1 final parçalanma ve tam zamanlı tur
- `CORE_PROTOCOL_Server` içine eski 24 dikdörtgenin yerine her iki cam panelinin gerçek ölçülerine göre 110 üçgen cam parçası (220 ince WedgePart) üreten uygulama kuruldu. Hücre köşeleri düzensizleştirilir; her üçgenin iki yarısı birlikte yönsel, dönen ve aşağı düşen bir yörünge izler. Kırıklar çarpışmasız görsel parçalardır; 2,5 saniye içinde kaybolup temizlenir. Fiziksel parçacık çarpışması simüle edilmez.
- Geçici Studio Play testinde iki panelde sırasıyla 80 ve 30 üçgen üretildi; 220 yarının hareketi ve temizlenmesi doğrulandı. Ön görüntü `studio_bridge/provider_switch/community_results/0fd4be12cc064e2ca6f138cd690f636f_1.jpg`; dondurulmuş geometri testidir, hareketli son kare değildir.
- Gerçek sunucu fast-forward t=430 testinde `LastImpact=434`, `FinalImpact=true`, iki panel saydam/çarpışmasız/dokunmasız ve `M14GlassShardTriangles=110`. Gerçek 57 saniyelik AFTERMATH sonu `COLD` resetinde iki panel tekrar görünür, CanCollide ve CanTouch true; çatlak aşaması ve parça sayısı 0.
- Normal zamanlı tam tur: test-only otomatik meltdown, başlangıç ofseti 0. Gerçek ölçümler 143.30/230.28/327.35/385.25/434.35 sn; çatlak evreleri 1/2/3/3/3, LastImpact sırasıyla 143/230/327/385/434. Final=true ve 110 üçgen; 57 sn sonra doğal reset COLD, her iki panel yeniden çarpışabilir ve dokunulabilir, Stage=0 ve parça=0. Kullanıcı butonuyla başlatma testi değildir.
- Beş lazer hedefi için Studio'da `RespectCanCollide=true` raycast ilk çarpışmayı doğru panoramik cam panelinde buldu. Bu, çarpışması kapalı görsel öğelerin engel olmadığına veya tüm kamera açılarında kusursuzluğa dair kanıt değildir.
- Test bitiminde Play durduruldu; `STUDIO_AUTO_MELTDOWN=false`, `STUDIO_PREVIEW_SECOND=0` normale döndürüldü. Yerel `CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua` güncellendi.
- Ayrı açık konular: `MeshContent` kaydedilip yeniden açılma kalıcılığı, gerçek oyuncu kontrollü başlangıç ve farklı cihazlarda FPS ölçümü; ses prototip ayarı muted olduğundan cam sesi bu testte doğrulanmadı.
