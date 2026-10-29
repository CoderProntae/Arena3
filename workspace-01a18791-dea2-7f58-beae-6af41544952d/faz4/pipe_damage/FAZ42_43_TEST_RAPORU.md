# Faz 4.2–4.3: uygulama ve test durumu

## Kurulum
- Edit: `FAZ42_PipeDamage_Controller` sunucu betiği, `REACTOR_MESH_CONTROLLER` ve `ReactorPilot_CustomVapor` düzenlemeleri uygulandı. Ana sunucudaki yinelenmiş maske yazımı kaldırıldı; önceden var olan gerçek `ReactorPipeBrokenMask` otoritedir.
- Boru eşlemesi gerçek R5 hat numarası / maske biti: üst sol 6/5, üst sağ 3/2, arka sol 8/7, arka sağ 1/0. Sol/sağ konumu hatların x işaretiyle uyuşur; üst/arka eşlemesi tasarım seçimidir, birebir geometrik karşılık değildir.
- Mesh başlıkları gerçek `ReactorEmitterBrokenMask` kırılma kenarında deformasyona başlar, hasar şiddeti zamanla artar. İstemci yıldızı yalnızca MELTDOWN sırasında kırık başlık sayısına bağlı hafif düzensizlik alır.

## Studio Play sonuçları
- Son sürüm için kontrollü maske testi 0, 32, 4, 128, 1, 165, 0: görünür sızıntı sayıları 0, 2, 2, 2, 2, 8, 0; her durum spool görünürlüğü denetlendi.
- Gerçek hızlandırılmış MELTDOWN: t≈255.7, gerçek ve görsel boru maskesi 164; üst sol, üst sağ ve arka sol kırık; 6 sızıntı; emitter maskesi 14 ve arızalı başlıkların hasar şiddeti ≈0.35–0.41. Sonraki ölçüm t≈284.5: emitter maskesi 30; önceki başlıklar 1'e, yeni başlık ≈0.58'e ulaştı.
- İstemci: emitter maskesi 30 iken iki sağlam başlığın lazeri görünür, dört kırığın lazeri gizli, LaserActiveCount=2.
- Kontrollü telemetry sıfırlamada kırık dört başlık severity=0/HeadCracked=false, boru maskesi=0 ve görünür sızıntı=0. Bu **tam gerçek oyun reseti değildir**.
- `STUDIO_AUTO_STARTUP=false`, `STUDIO_AUTO_MELTDOWN=false`, `STUDIO_PREVIEW_SECOND=0` geri alındı; Play durduruldu.

## İlk sürümde açık olanlar (bulut iyileştirmesi öncesi)
- Sızıntı 3B ağının iki sürümü Studio'da görüntülendi; ikinci sürüm daha yumuşak ama gerçekçi sis yerine hâlâ yarı saydam kabuk izlenimi verebiliyor. Üç açılı görsel doğrulama ve daha iyi hacimsel buhar gerekli. Son görüntü: `studio_bridge/provider_switch/community_results/4d5400cdd8774994977abe56042d9ba7_1.jpg`.
- Gerçek normal süreli meltdown, AFTERMATH ve tam otomatik reset, başlangıç/normal rejimde geri dönüş testi ve FPS etkisi tamamlanmadı. Faz 4.1 doğal cam parçalanması da açık.
- Edit'teki prosedürel MeshContent'in dosya kaydedilip yeniden açıldığında kalıcılığı hâlâ doğrulanmadı. Studio değişiklikleri kullanıcının proje dosyasına kaydedilmelidir.
- İlk entegrasyonda yinelenmiş aynı isimli maske fark edildi, gerçek maskeyle çatıştığı Play testiyle saptandı ve kaldırıldı. Son denetleyici gerçek 10 hatlı maskeyi doğrudan okuyor.

## 29 Ekim — Faz 4.2 yeni buhar ve doğrulama
- Eski tek konik yarı saydam kabuk yerine her ağızda hareket eden 4 çok loblu, düzgün normalli 3B mesh bulutu oluşturuldu. Toplam 4 boru / 8 ağız / 32 bulut. Bu bir hacimsel 3B görsel yaklaşımdır, akışkan simülasyonu değildir; ParticleEmitter/Beam kullanılmaz.
- Kullanıcıya daha önce onaylatılmış M13 borular ve R5 maskesi korundu. Ağız/mesh üretimi tamamlanmadan binding yapılmaz; eski vent klasörü güvenli temizlenir.
- Geçici Play kontrollü maskeler 0,32,4,128,1,165,0: görünür bulut sayıları 0,8,8,8,8,32,0; sağlam/kırık görünürlüğü ile tüm sağlam meshlerin `CanCollide`, `CanTouch`, `CanQuery` değerleri orijinal hâllerine geri döndü.
- Son kaynak kurulu gerçek olay fast-forward 430: gerçek ve görsel maskeler 677; eşlenen dört boru kırık, 32 bulut ve gizli/etkisiz sağlam borular doğrulandı. Gerçek 57 saniyelik AFTERMATH resetinde maskeler 0, 0 görünür bulut, her modülde 6 sağlam görünür, 0 kırık görünür.
- Gerçek Studio'da 3 farklı erişilebilir açı: `community_results/21f239039b024967b6c911fe8b89591b_1.jpg`, `3f3ccf88d0e2433b8b7d316a8e34a7b5_1.jpg`, `efbdef93cfb9455f8096186c42febd06_1.jpg`. Kapalı duvar içinden alınan iki kare gözlem sayılmadı.
- Kısa Studio sunucu Heartbeat örneklemesi: boşta ortalama 16.66 ms, p95 18.94 ms (3 sn); 32 bulut açıkken ortalama 16.75 ms, p95 18.98 ms (4 sn). Küçük, tek oturumluk ölçümdür; istemci GPU/FPS, mobil cihazlar veya tam senaryo için performans garantisi değildir.
- Sonrasında Play durduruldu; `STUDIO_AUTO_STARTUP=false`, `STUDIO_AUTO_MELTDOWN=false`, `STUDIO_PREVIEW_SECOND=0` Studio betiğinden okundu. Kurulu denetleyicinin yerel kopyası `FAZ42_PipeDamage_Controller.server.lua`.
- Ayrı sınırlar: üst/arka R5 eşlemesi hâlâ tasarım seçimidir, fiziksel simülasyondaki 10 hattın birebir aynı geometrik konumu olarak değerlendirilmemelidir. Yeni bulut sürümü normal süreli tam turda değil, kontrollü maskelerde ve 430'dan hızlandırılmış gerçek tur + gerçek reset ile test edildi. Dosya kaydı/yeniden açılışta `MeshContent` kalıcılığı, ses ve düşük güçlü cihaz testi henüz doğrulanmadı.

## 29 Ekim — güncel bulut ile normal süreli tam tur
- `STUDIO_AUTO_MELTDOWN=true`, başlangıç ofseti 0 ile normal süreli otomatik Studio turu çalıştırıldı. 87.48 sn: maskeler 4/4, 8 bulut; 186.43 sn: 36/36, 16 bulut; 230.48 sn: 164/164, 24 bulut; 345.51 sn: 165/165, 32 bulut. Görsel etkin spool sayıları sırasıyla 1, 2, 3, 4.
- 435 saniye ardından 57 saniyelik gerçek AFTERMATH resetinde COLD, gerçek/görsel maskeler 0/0, etkin spool 0, görünür bulut 0. Önceki hızlandırılmış turda her modülün 6 sağlam ve 0 kırık meshe döndüğü de ölçüldü.
- Bu test yeni bulut sürümüyle normal süreli otomatik turdur; oyuncu kontrolleriyle başlatma, düşük güçlü cihaz GPU/FPS testi, ses ve kaydedip yeniden açılış kalıcılığı ayrı kalır. Test ayarı kapatıldı ve Studio betiğinden false/false/0 olarak okundu; Play durduruldu.
