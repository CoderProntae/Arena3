# CORE PROTOCOL V2 — görsel açıdan yeniden kurulmuş Roblox reaktör oyunu

Bu paket **HELIOS-9 V1–V4'ü ve önceki CORE PROTOCOL paketini değiştirmez**. Yeni, boş bir Roblox Studio deneyimi veya eski CORE scriptlerinin kaldırıldığı bir yer için hazırlanmıştır. Kullanıcının sağladığı [GitHub klibindeki](https://github.com/CoderProntae/.mp4) *A Core Game* camlı kontrol odası, karşıdan görülen altı yayıcılı çekirdek ve yaklaşık 7:15 süren meltdown dizisi temel alındı. Kaynak Roblox oyununun dosyaları, birebir modelleri veya orijinal sesleri kullanılmadı. Klip 256×144 ve sadece YouTube videosunun 11:49–27:34 bölümünü içerdiğinden klipte görünmeyen startup/freezedown kuralları özgün olarak tasarlandı; **1:1 aynı oyun iddiası yoktur**.

## Kurulum — iki script

1. Roblox Studio'da **yeni bir deneyim** açın veya mevcut CORE PROTOCOL denemenizdeki **eski sunucu Script + eski LocalScript'i SİLİN/devre dışı bırakın**. Aynı anda V1 ve V2 scriptlerini çalıştırmayın; çift dünya ve çift Lighting efektleri oluşur. HELIOS-9 V1–V4 dosyalarını silmeyin.
2. **ServerScriptService** içine bir **Script** ekleyin; adını `CORE_PROTOCOL_V2_Server` yapın. `CORE_PROTOCOL_V2_Server.server.lua` içeriğinin **tamamını** içine yapıştırın.
3. **StarterPlayer → StarterPlayerScripts** içine bir **LocalScript** ekleyin; adını `CORE_PROTOCOL_V2_Client` yapın. `CORE_PROTOCOL_V2_Client.client.lua` içeriğinin **tamamını** içine yapıştırın. Kamera sarsıntısı, ekran parlaması ve müzik için bu ikinci script gerekir; kontrol mantığı sunucudadır.
4. **Test → Play** ile deneyimi başlatın. Yüklenirken Output'ta `[CORE PROTOCOL V2] ...` ile başlayan iki mesajı arayın. Sunucu kendi dünyasını `Workspace/CORE_PROTOCOL_V2_WORLD` altında, istemci iletişim olayını `ReplicatedStorage/CORE_PROTOCOL_V2_CUES` altında oluşturur. Studio Test → Play yerine yalnızca Edit modunda script çalışmaz.
5. Dünyada görünür, kalıcı ekran HUD'u yoktur. Metinler makinelerin üzerinde gerçek `SurfaceGui` etiketleridir; geçici parlamalar kameraya bindirilir.

> **Birden fazla kopya yerleştirmeyin.** Sunucu scripti kendisine ait önceki `CORE_PROTOCOL_V2_WORLD` modelini ve ışık efektlerini yeniden başlatırken temizler; bu paket ayrıca haritadaki diğer `SpawnLocation` nesnelerini devre dışı bırakır. Bu nedenle özellikle yeni/ayrı bir deneyim kullanın. Düğmelere gerçek oyuncu karakteriyle yanlarından yaklaşarak tıklayın; sunucu mesafeyi doğrular.

## Oynanış ve işleyen fiziksel kontroller

| Yer | Kumanda | Gerçek etkisi |
|---|---|---|
| Soldaki kontrol masası | **COOLANT FLOW** fiziksel çevrilen düğme | Her tıkta `0 → 25 → 50 → 75 → 100 → 0` dolaşır; başlangıç **50%**. Hazne seviyesini, gerçek akışı ve termal hedefi değiştirir. Hasarlı borular akıştan düşer. |
| Soldaki masa | **REACTOR POWER** çalışan kol | Her tıkta `0 → 25 → 50 → 75 → 100 → 0`; başlangıç **0%**. Çekirdek sıcaklığı, ışığı ve bozulma hızı değişir. |
| Soldaki masa | **FOCUS LASERS** çalışan kol | Gerçek plazma/yayıcı parlaklığını ve ısı üretimini açar/kapatır. Başlatmadan sonra kullanılabilir. |
| Soldaki masa | **E-COOLANT** çalışan kol | Ayrı acil rezervi açar. Soğutucu akışı, buhar efektleri ve ısı değişir; rezerv sürekli azalır, boşalınca kapanır. |
| Soldaki masa | **IGNITION** gömülü basmalı düğme | Yeterli güç/soğutma varsa 44 saniyelik startup başlatır. Freezedown sırasında toparlanmayı tetikler. |
| Soldaki masa | **SHUTDOWN** basmalı düğme | Zemindeki konsolu hidrolikle yukarı çıkarır; kartları ve shutdown kolunu fiziksel olarak erişilebilir yapar. |
| Sağdaki bağımsız kürsü | **SCRAM** güvenlik kapaklı kol | Kontrol çubuklarını indirir. Erken müdahale başarılı kapanış; çok geç/çok az soğutma/kart yetkisi yoksa fiziksel çubuk sıkışması ve başarısız kapanış. |
| Sol ve sağ reaktör servis koridorları | Üç **AUTH 01/02/03** kartı | Her tur altı fiziksel bölmeden rastgele üçüne dağıtılır. Bölmeye gidip renkli kartın kendisine tıklayın. İlk kart gerçek shutdown konsolunu yükseltir. |
| Yükselen merkez konsol | Üç kart yuvası + **ARMED SHUTDOWN** basma düğmesi | Topladığınız kartları eş numaralı yuvalara tıklayarak yerleştirin. Üçü de takılıyken bastığınızda süre/soğutma/donanım koşullarına göre gerçek başarılı veya başarısız sonuç doğar. |
| Servis koridorları / bunker | Otomatik hava kilitleri / koruyucu kapı | Yaklaşıldığında fiziksel servis kapıları açılır; 2,9 saniye sonra kapanır. Bunker girişi patlamadan 11 saniye önce kapanmaya başlar; içeri zamanında girenler patlamadan korunur. |

**İzlenecek örnek yollar**

- **Normal startup:** `REACTOR POWER` koluna **bir kez** basın (`25%`), soğutmayı `50%` bırakın, `IGNITION` düğmesine basın. 44 saniye sonra sistem ONLINE olur. Etiketler sıcaklık, basınç ve akışı gösterir.
- **Failed startup:** Ignition'dan hemen sonra gücü `0%` yapın veya soğutmayı `0%` indirin. Startup 12. saniyesinden itibaren hatayı algılar, fiziksel koruma çubukları iner; 18 saniye sonra yeniden denemeye hazır olur.
- **Freezedown / toparlanma:** ONLINE iken gücü `0%`, soğutmayı `100%`, lazerleri OFF yapın. Yeterince soğuyup 13 saniye düşük kaldığında siyan buhar/freezedown başlar. `IGNITION` yeniden kurtarma gücü/lazerleri açar; 460 °C üstünde ONLINE durumuna döner.
- **Meltdown başlatma:** Online olduktan sonra gücü `100%`, soğutmayı `0%`, lazerleri ON yapın. 1640 °C üstündeki taşma yeterince sürünce 435 saniyelik olay akışı başlar. Mavi plazma, teker teker zarar gören yayıcılar/borular, çatlayan cam, kırmızı kontrol odası, odaya inen mavi ışın, kırılan pencere ve gerçek patlama görülür. Sol duvar ekranında dünya içi `T-mm:ss` sayacı vardır; kamera önündeki camı kapatan panjur **yoktur**.
- **Başarılı shutdown:** Erken SCRAM çekmeden önce `COOLANT`ı en az `25%`e geri getirin; `0%` akışla SCRAM başarısız olur. **Veya** koridorlardan üç yetki kartını toplayıp merkez konsolun üç yuvasına takın ve shutdown butonuna, meltdown başladıktan sonraki **ilk 270 saniyede**, etkili soğutma `18%` üstündeyken basın. Tüm turlarda kartların yeri yeniden karışır. Güç/lazer kapanır, kontrol çubukları iner, alarm ve müzik kesilir, çekirdek soğur. 75 saniye sonra yeni tur hazırlanır.
- **Başarısız shutdown:** Güç/soğutma durumunu bozun ya da ilk **270 saniyeyi** geçirdikten sonra SCRAM/final butonuna müdahale edin. Çubuk sıkışması, yayıcı kırığı, kırmızı patlama işaretleri ve kaçınılmaz kriz sonucu oluşur. Büyük patlama meltdown başlangıcından yaklaşık **7 dakika 15 saniye** sonra gerçekleşir. Bunker koruması için kapı kapanmadan içeri girin. Patlamadan 57 saniye sonra harita/reaktör/kartlar sıfırlanır.

## Kullanıcının iki karesiyle karşılaştırma — hızlı Studio önizlemesi

- Oyuncu ilk açılışta **sol arka, çapraz açıdan** (-29, 151) başlar; küçültülmüş fiziksel kontrol bankı solda, kapatılmamış geniş cam ve reaktör sağda kalır. V1'in kadrajı kaplayan büyük kumandaları artık burada bulunmaz; karşılaştırma için bu yeni başlangıç noktasından kare alın.
- Kullanıcının YouTube karesi **15:53**, yani meltdown başlangıcı 11:49'a göre yaklaşık **244. saniye**. Karşılaştırmak için sunucu `CFG` bölümünde `STUDIO_AUTO_MELTDOWN=true`, `STUDIO_PREVIEW_SECOND=244` yapın; **Play** başladıktan 12 s sonra sahne o ana sarılır. İlk birkaç saniyede önceki hasar olayları hızlıca işlenir; **5–10 saniye bekleyin** ve fotoğrafı çekin. Bu sadece Studio'ya özel **görsel prova** kısayoludur; özgün videonun o karedeki kamera hareketlerini kopyalamaz.
- Baştan sona 7:15 süreyi test etmek için `STUDIO_PREVIEW_SECOND=0` kullanın. Normal tam oyun için iki parametreyi de varsayılanına döndürün: `STUDIO_AUTO_MELTDOWN=false`, `STUDIO_PREVIEW_SECOND=0`. Studio dışındaki sunucuda bu kısayol çalışmaz.
- V2 parlama bütçesi sunucu dosyasının başındaki `CFG.VISUAL` tablosundadır. `ROOM_EXPOSURE=-0.82` başlangıç önerisidir. Sizin Roblox grafik ayarlarınızda sahne fazla karanlıksa `-0.65`, hâlâ parlaksa `-1.0` deneyebilirsiniz. `CORE_LIGHT_RANGE=59` değerini **67'nin üzerine çıkarmayın**: camın yakınındaki oda yeniden gereksizce aydınlanır. `BLOOM_IDLE=0.16`, `BLOOM_MELTDOWN=0.38`, `BLOOM_THRESHOLD=2.45` patlama haricinde highlightların kontrol altında kalmasını hedefler. Bu değerlerin Studio'daki nihai görünümü henüz burada doğrulanmadı.

## Ses, görüntü ve güvenlik notları

- `CFG.AUDIO` içindeki `rbxassetid://...` değerleri deneyime göre oynatma izinlerine tabidir. **Seslerin yeni deneyimde kesin çalacağını iddia etmiyoruz.** Studio Output'ta `Failed to load sound`/izin hatası görürseniz Creator Store'dan kendi deneyiminizde kullanılabilen seslerle ilgili kimlikleri değiştirin; bu üç müzik kimliğini sunucudaki `opening`, `escalation`, `finale` alanlarında güncelleyin. Kalan efekt ve ambient kimlikleri de aynı tablodadır. Sesler sessiz kalsa bile fiziksel reaktör çalışmaya devam eder.
- Çok sayıda Neon/ışık/parçacık ve 11 Hz sunucu animasyonu kullanır. Düşük donanımda Roblox grafik düzeyini azaltın. İstemci flash efektleri tam ekran ama geçicidir; kalıcı HUD değildir.
- İstemci `CORE_PROTOCOL_V2_CUES` olayını yalnızca durum **senkronu istemek** için çağırabilir; hiçbir oyuncu istemciden güç, kart, soğutma veya hasar durumunu zorlayamaz.
- Klip orijinal deneyimin kodunu ve görünmeyen bölüm mekaniklerini açıklamaz. Buradaki ortam prosedürel bir yeniden yorumlamadır, **orijinal asset/rip/kopya değildir**. Etkileşimlerin tamamının/animasyonun Roblox Studio'da hatasız çalıştığı ayrıca **Play testiyle doğrulanmalıdır**; bu çalışma ortamında Roblox Studio bulunmadığından buna ilişkin garanti verilmez.

## Paket içeriği

- `CORE_PROTOCOL_V2_Server.server.lua` — dünya, fiziksel kontroller, yetki, sıcaklık, arıza, 435 saniyelik olay akışı, bunker ve sonuçları üreten sunucu kodu.
- `CORE_PROTOCOL_V2_Client.client.lua` — çevresel müzik, geçici ekran parlaması ve kamera sarsıntısı. Reaktör state değiştirmez.
- `CORE_PROTOCOL_V2_StaticChecks.py` — isteğe bağlı çevrimdışı kaynak/analitik görüş kontrolü (`python CORE_PROTOCOL_V2_StaticChecks.py`); gerçek Studio Play testinin yerini tutmaz.
- `CORE_PROTOCOL_V2_Dogrulama.md` — gerçekleştirilen statik testler ve Studio için kontrol listesi.

**Eski V1–V4 dosyaları bu paketle değiştirilmedi.**
