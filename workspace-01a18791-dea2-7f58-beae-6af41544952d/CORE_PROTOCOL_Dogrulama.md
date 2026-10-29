# CORE PROTOCOL — test tutanağı ve Studio kontrol listesi

## Gerçekten çalıştırılmış çevrimdışı kontroller

- `npx --yes luaparse CORE_PROTOCOL_Server.server.lua` → **geçti**.
- `npx --yes luaparse CORE_PROTOCOL_Client.client.lua` → **geçti**.
- `python CORE_PROTOCOL_StaticChecks.py` → **25/25 geçti**: toplam kod boyutu 8000 satırın altında; 435 saniye yapılandırması; benzersiz/sıralı 21 kriz olayı (12–430. saniyeler); tanımlı ses anahtarları; yedi fiziksel kumandanın yedi sunucu tıklama bağlantısı; 3 kart/3 yuva bağlantısı; sunucu yetkisi; opak panjur yokluğu; dokuz örnek hattın yaklaşık model geometrisi; temel termal senaryolar.
- Oda camı için **analitik** 9/9 örnek hattın görüş açıklığı test edildi. Bu, Studio'nun gerçek fizik/raycast/render sonucuyla aynı şey değildir. Sunucu Studio Play sırasında `auditView()` ile ayrıca örnek görüş hatlarını raporlar; bu gerçek Studio çıktısı henüz alınmadı.
- Ayrı bir **Lupa/Lua tabanlı sahte-Roblox mühendislik çalışma testi** ile yaklaşık 1798 nesnenin üretimi, sunucu Heartbeat adımları ve istemci olay işleyicisi yürütüldü. Şu iş akışlarının durum sonucu doğrulandı: normal startup; gücü kesince failed startup; freezedown + ignition recovery; acil soğutma rezervinin azalması; erken başarılı SCRAM; üç kart + üç yuva + başarılı final düğmesi; yaklaşık 435 s hasar akışı/patlama/reset; geç SCRAM/rod jam; patlama sırasında bunker içinde sağ kalma; istemcide flash/shake/müzik başlangıç-geçiş-bitiş. Bu test Roblox API'sini/gerçek fiziği **taklit ettiği** için **Studio Play veya gerçek ses/ışık/görünürlük doğrulaması değildir**. Özellikle önizlemede ClickDetector ray hedefi ve asset yetkisi doğrulanmalıdır.
- Referanstaki ilk meltdown bölümü YouTube 11:49–19:04, yani **7:15 = 435 s**. Kodda olaylar bu zaman aralığına dağılır; ilk evre 12/36/63, kırmızı alarm 110, yayıcı kopmaları 143/186/230/271/345, müzik kırılımları 169/305, oda içi mavi sütun 305, bunker kapısı 424, patlama 435. Bu **esinlenilmiş zamanlama**, frame-by-frame eşleşme garantisi değildir.

## Henüz YAPILMAMIŞ olanlar

Bu ortamda Roblox Studio bulunmadığından **Studio Play çalıştırılmadı**. `ClickDetector`, kamera, ses izinleri, fizik, tween, performans ve çok oyunculu hareket hakkında test edilmiş bir çalışma garantisi yoktur. Klibin 144p çözünürlüğü ve startup/freezedown görüntülerinin bu klipte olmaması nedeniyle özgün mekaniğin birebir kopyası iddia edilemez. Yeni Roblox experience içinde ses oynatma izinleri kontrol edilmedi.

## Studio Play'de önerilen test sırası

1. **Output / yükleme**: İki `[CORE PROTOCOL]` satırı; Lua hata izi olmamalı. `Workspace/CORE_PROTOCOL_WORLD` var. Pencereden yıldız ve altı yayıcı görünüyor. Sunucunun sightline raporu `9/9 clear` olmalı; farklı sonuç varsa engel ismiyle birlikte Output'a yazılır.
2. **Fiziksel kontrol ve geri bildirim**: Masada yedi gerçek kumandaya tıklayın. Kollar, pilot lambalar, dial ve fiziksel durum yazıları senkron değişiyor mu? Normal güç/soğutma değerleri ve lazer ON/OFF termal gidişatı etkiliyor mu? Tıklanabilir görünmesine rağmen tepki vermeyen bir kumanda varsa konum ve kamera açısını not edin.
3. **Başlangıç ve failure**: Power 25% / coolant50% ile IGNITION → 44 s sonra ONLINE. İkinci turda startup sırasında güç0 → FAILED_STARTUP → yaklaşık 18 s sonra standby. Koruma çubukları/ışıklar yerinde mi?
4. **Freezedown & E-coolant**: ONLINE iken power0/coolant100 → düşük sıcaklıkta siyan olay; IGNITION ile kurtarma. E-COOLANT açılınca sprey ve acil rezerv düzenli azalıyor mu? Aşırı ısınmadan önce açılırsa meltdown erteleniyor/önleniyor mu?
5. **Kartlar/odalar**: Her iki servis koridorundaki otomatik kapılar oyuncuya çarpmadan açılıp kapanıyor mu? Altı yerden üç kart bulunabiliyor mu? İlk kartta konsol yükseliyor mu? Üç yuva eş numaralı kartları alıyor mu? Yakın olmayan oyuncu kliklerini sunucu reddediyor mu?
6. **7:15 dizisi**: `STUDIO_AUTO_MELTDOWN=true` ile başlatıp tam süre izleyin. Kırmızı aydınlatma, yayıcı ve boru hasarı, kırılabilir halka, cam çatlağı, 305. saniye civarı oda içi mavi sütun, 424. saniye kapı ve 435. saniye cam kırılması/patlama görünür mü? Filmin kendisi kamerayı sürekli fiziksel olarak kapatıyor mu? **Kapanmamalı.**
7. **Üç kapanış yolu**: Erken SCRAM başarılı; 3 kartı takıp 270. saniyeden önce soğutmayla final butonu başarılı; geç/etkisiz SCRAM veya geç final butonu başarısız (turuncu sıkışma, ardından meltdown). Alarm/müzik kesilme/geçiş durumlarını kontrol edin.
8. **Bunker ve tur yenileme**: 424. saniyeden önce bunkere giren oyuncu 435'te yaşıyor mu, dışarıdaki ölüyor mu? 57 s sonra yeni kart yerleri, cam, soğutma, yayıcılar ve kapılar düzeliyor mu? Başarılı shutdown sonrasında 75 s otomatik reset var mı?
9. **İki oyuncu + geç katılım**: Diğer oyuncu ile aynı durumu gördüğünüzü, kartların paylaşıldığını ve sonradan girenin doğru müzik evresini aldığını doğrulayın. Düşük FPS ve farklı grafik seviyelerinde test edin.
10. **Ses izinleri**: `Sound failed to load` uyarılarını ayrı inceleyin. Gerekirse `CFG.AUDIO` kimliklerini deneyime uygun Roblox sesleriyle değiştirin. Kamera ve fiziksel dünya sesler olmadan da işlemeli.

## Bilinen bilinmezler ve sınırlar

- Yakın seslerin Creator Store kimlikleri yeni projede yetki gerektirebilir. Uzaktan ses dosyası gömülmedi.
- 7:15 meltdown, kullanıcı etkileşimiyle geçersiz kılınabilir: erken başarılı shutdown krizi bitirir. Bu tasarımsal işlevdir; izleme için Studio otomatik testi kullanın.
- Client FX kalıcı HUD barındırmaz, ancak filmin geçici tam ekran flaşı vardır.
- Servis koridorları ve bunker reaktör oynanışı için sınırlıdır; videoda olmayan reaktör dışı ek mekânlar bilinçli olarak yapılmadı.
- Kaynak metni Lua ayrıştırıcısı ile doğrulamak Roblox Luau/runtime nesne API'sini doğrulamak değildir. Çıktı tutanağına Play testi yapılmış gibi bir ifade yazılmamalıdır.
