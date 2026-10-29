# CORE PROTOCOL REMAKE — eksik → düzeltme günlüğü

**25 Ekim 2026.** Hedef, açık durumdaki `AEGIS_Reactor.rbxlx` Studio projesi. Karşılaştırma: kullanıcının *A Core Game* kareleri (`uploads/image-2.png`–`image-8.png`) ve gerçek Studio Play yakalamaları. 144p videodan görünmeyen varlık/mekanik birebir kopyası olduğu iddia edilmez.

| # | Gözlenen somut eksik | Yapılan işlem / kanıt | Durum |
|---|---|---|---|
| 1 | COLD’da parlak yıldız ve altı ışın zaten açıktı. | Yıldız, neon çubuk, gerçek Beam, toz ve optik lensler duruma bağlandı; COLD Play’de merkez karanlık (`remake_evidence/R5_COLD_Studio.jpg`). | **Düzeltildi; Play’de görüldü.** |
| 2 | STARTUP 44 saniye bekletiyordu; görsel aşama yoktu. | 6. saniyede soğutma hazırlığı; 12–27. saniyelerde altı yayıcının röle/lensleri sırayla; ~29. saniyede füzyon; ~44. saniyede nominal durum. Başlangıç/ateşleme/nominal Play kareleri ve tıklamasız durum simülasyonu var. | **Düzeltildi; Play’de aşamalar görüldü.** |
| 3 | Konsol ve karakterin oranı uyuşmuyordu. | Oda, kumandalar ve model ölçeği avatar boyuna indirildi; yakın üçüncü kişi kamera eklendi. | **Düzeltildi; Play’de görüldü.** |
| 4 | Konsolun çarpışması karakteri cihazların içine sokabiliyordu. | Taşıyıcı konsol parçasına fiziksel çarpışma eklendi. Kullanıcı ek tıklama testi istemediğinden yeniden hareket/etkileşim testi yapılmadı. | **Kod düzeltildi; yürüyüşle yeniden doğrulanmadı.** |
| 5 | Roblox `Glass` penceresi arkasındaki şeffaf yıldızı, Beam ve parçacıkları gizliyordu. | Pane saydam `SmoothPlastic` oldu; görsel etki Play’de görünür. | **Düzeltildi.** |
| 6 | Ön cam dikmesi yıldızı/sağ yayıcıyı kesiyordu. | Bölücü x=43’e, karşılık gelen iki gerçek pane birleşimine taşındı; pano/çerçeve korunuyor. | **Düzeltildi; R5 Play’de merkez açık.** |
| 7 | Kalın soğutma hatları yayıcıların önünden ve merkezin üzerinden geçiyordu. | Studio Client ışın sorgusu geçeni `BREAKABLE_BLUE_FEED_PIPE_3` olarak belirledi. Kırılabilir 10 hat ve tanklar merkezin dışına yönlendirildi; sızıntı/damage işlevleri korundu. | **Düzeltildi; R5 Play’de görüldü.** |
| 8 | Üst yazı tavan lambalarının arkasında kesiliyordu. | Altı asılı ışık ve büyük armatür tavana alındı; beyaz durum bandı artık `CORE OFFLINE / STANDBY` ve `CONTAINMENT FAILURE` metnini kesmeden gösteriyor. | **Düzeltildi; COLD/meltdown Play’de görüldü.** |
| 9 | Tavan armatürleri taşındığında oda fazla karardı. | Yazıya engel olmayan sekiz gizli yerel dolgu ışığı ve dengeli pozlama; beyaz zemin/duvar kontrastı geri geldi. | **Düzeltildi; R5 COLD Play’de görüldü.** |
| 10 | Oda büyük düz kutular ve ilgisiz dekor gibi görünüyordu. | Açık renkli döşeme, servis ızgaraları, kablolar, metal bağlantılar, panel dizileri, renkli lambalar ve sadece reaktör/servis/bunker işlevli alanlar yeniden modellendi. | **Belirgin iyileşti; özel mesh/doku gerektiren referans ayrıntıları birebir değil.** |
| 11 | Yayıcılar ve merkez tel halkalar/tekdüze küre gibi görünüyordu. | Altı makineli metal silindir, lens, soğutma manşonları, mor/beyaz optik Beam, radyal yıldız kolları ve hareketli mavi-mor arka plan eklendi; yıldız COLD’da kapalı. | **İyileşti; referansın fotogerçekçi plazmasıyla birebir değil.** |
| 12 | Meltdown’da merkez yerine yan efektler öne çıkıyor, çevrede fiziksel hasar zayıftı. | Artan merkez kıvılcımı, beyaz basınç dalgası, mor bulut, yayıcı arızası, kırılan boru/pencere, yanıp sönen alarmlar ve merkez starburst. `remake_evidence/R5_MELTDOWN_244_Studio.jpg` 244. saniyenin geçici Play önizlemesi. | **İyileşti; bütün 435 saniye gerçek zamanlı izlenmedi.** |
| 13 | Alarm bütün zemini tek neon pembeye boyuyordu. | Kırmızı ışık yerel armatürlerde/top ışıkta; zemin çoğunlukla beyaz bırakıldı. | **R5 Play’de görüldü.** |
| 14 | Konsol metinleri küçük/kırık, kontroller tanımsızdı. | İki ön durum paneli, üst bant ve duvar tanıları okunabilir fiziksel `SurfaceGui` oldu; kumandalar server tarafında çalışıyor. Önceki turda güç/ateşleme çalışmıştı. | **Ekranlar Play’de görüldü; kullanıcı isteği üzerine yeni tıklama testi yapılmadı.** |
| 15 | Ses varlıklarının deneyime özgü oynatma yetkisi belirsiz. | Önceki Play’de beş sürekli ses yüklenmiş ve Output’ta oyun kaynaklı izin hatası görülmemişti. **Tüm tek seferlik efektlerin ve müziğin kullanıcının deneyiminde duyulabilirliği doğrulanmadı.** | **Açık doğrulama sınırı; çalışıyor diye kesin söz verilmez.** |
| 16 | Sadece analitik görüş hattı başarıları görsel görünürlüğü garanti etmiyordu. | 23/23 geometrik ışın kontrolüne ek olarak gerçek Play kareleri, pencere malzemesi düzeltmesi ve Studio ışın sorgusu kullanıldı. | **Daha güvenilir görsel doğrulama yapıldı.** |
| 17 | Önceki V1–V4 yerinin bozulma riski. | Ayrı açık remake Studio yeri düzenlendi; eski V3 kaynakları korunuyor. | **Korundu.** |

**Eş zamanlı karelerle yeniden değerlendirme:** [13:21, 15:53, 17:27 referans/Studio karşılaştırması ve öz eleştiri](CORE_PROTOCOL_REMAKE_Es_Zamanli_Karsilastirma_ve_Oz_Degerlendirme.md). İlk sürüme göre ilerleme olsa da, görsel referans sadakati yalnızca yaklaşık **3/10**; özellikle hacimsel plazma, ayrıntılı varlıklar, alçak konsol, geç meltdown asimetrisi ve kriz pozlaması açık eksikler olarak kaldı.

**Kalıcı kaydetme uyarısı:** MCP düzenlemeleri açık Studio Edit DataModel’ine uygulandı. Windows’taki yerel `.rbxlx` dosyasına diskte yazıldığını bu köprü doğrulamıyor. Studio’da **Ctrl+S** ile `AEGIS_Reactor.rbxlx` dosyasını kaydedin.

**Son test bayrakları:** `STUDIO_AUTO_STARTUP=false`, `STUDIO_AUTO_MELTDOWN=false`, `STUDIO_PREVIEW_SECOND=0`; Studio `script_read` ile doğrulandı. Oyun kodu toplamı **3.982 satır**, üst sınır 8.000.
