# HELIOS-9 V2 — Panoramik Kontrol Odası ve Reaktör Oyunu

Bu sürüm, oyuna girildiğinde **dev bir reaktör salonu** ile salona bakan **camlı, ayrı bir kontrol odasını** kodla kurar. Konsolların tamamı kontrol odasındadır. Yaptığın ayarlar yalnızca HUD'da sayı değiştirmez: reaktörün parçaları, ışıkları, pompa devirleri, jeneratörleri, buharı, lazerleri, su baskını nozulları ve gözlem camı panjuru sunucuda gerçekten değişir. Meltdown, ses ve fiziksel yıkım içeren aşamalı bir olaydır.

## Kurulum — iki dosya, doğru yerlere

1. **Roblox Studio**'da oyununu aç. Eski sürümün `HELIOS_9_Tek_Script.server.lua` Script'ini **Disable** et veya çalışma alanından kaldır. V1 ve V2 aynı anda çalışmamalı. V1 dosyasını bilgisayarından silmen gerekmez.
2. **Explorer → ServerScriptService → + → Script** ekle. İçindeki örnek kodu tümüyle sil, `HELIOS_9_V2_Server.server.lua` dosyasının **tamamını** bu Script'e yapıştır. Script'in adını örneğin `HELIOS9_V2_Server` yap.
3. **Explorer → StarterPlayer → StarterPlayerScripts → + → LocalScript** ekle. İçindeki örnek kodu tümüyle sil, `HELIOS_9_V2_Client.client.lua` dosyasının **tamamını** buna yapıştır. Adını örneğin `HELIOS9_V2_Client` yap.
4. **Play (F5)** ile dene; yalnızca **Run** seçeneğiyle değil. Dünya, `Workspace.HELIOS9_V2_WORLD` altında; haberleşme nesnesi `ReplicatedStorage.HELIOS9_V2_EVENTS` altında otomatik kurulur. Ayrıca elle RemoteEvent, model veya GUI oluşturmana gerek yok.
5. Eski oyundan kalma başka reaktör Script'leri veya aynı ada sahip LocalScript'ler varsa onları da devre dışı bırak. V2 oyun başladığında diğer `SpawnLocation` nesnelerini kapatır; mevcut haritana kuruyorsan bu davranışı sunucu Script'indeki spawn bölümünden değiştirebilirsin.

> **Not:** Studio'daki bir Play oturumunu durdurunca üretilmiş dünya o oturumla birlikte kapanır; sonraki Play'de yeniden oluşturulur. İki dosyayı doğru servislere koymak kalıcı kurulumdur.

## Mekân ve kontroller

- **Reaktör salonu:** Yaklaşık **256 stud çapında, 108 stud yüksekliğinde**. Katmanlı yürüyüş yolları, asılı kirişler, merkezde çok halkalı plazma çekirdeği, 16 hareketli kontrol çubuğu, 8 soğutma hattı, 10 odak lazeri, 4 jeneratör ve 12 tahliye bacası içerir.
- **Kontrol odası:** Salonun `+Z` tarafında, yüksekte ve 11 bölmeli geniş **gözlem camının** gerisindedir. Başlangıçta burada doğarsın. Cam önüne gidip reaktörü görebilirsin; arka tarafta zırhlı kabin/sığınak vardır.
- **Kullanım:** Konsol düğmelerine yaklaş ve **E** tuşunu basılı tut; mobilde görünen etkileşime dokun. Konsollardaki ProximityPrompt işlemleri sunucuda doğrulanır. HUD görüntüleme içindir; hiçbir istemci, RemoteEvent üzerinden keyfî reaktör ayarı gönderemez.
- **Asansörler:** Odadaki sol servis asansörüyle salona in; salondaki asansörle kontrol odasına dön.
- **Canlı grafik:** Kontrol odasının arka duvarında yaklaşık son 15 saniyelik **MW çubukları ve ısı izi** fiziksel olarak güncellenir.

| İstasyon | Eylem | Reaktörde hemen görülen/yaşanan sonuç |
|---|---|---|
| Çekirdek akısı | `%8` artır / azalt | Plazma parlaklığı, jeneratör gücü ve ısı dengesi değişir. |
| Pompalar / soğutma | `%12` artır / azalt | Sekiz depo seviye göstergesi ve pompalar hareket eder; sıcaklık hedefi değişir. |
| Kontrol çubukları | `%10` içeri / dışarı | 16 fiziksel şaft iner/çıkar; enerji ve ısı değişir. |
| Odak lazerleri | Aç / kapat | 10 gerçek ışın çekirdeğe uzanır; üretim artar, çekirdek **ısınır**. |
| Panoramik cam zırhı | Kapat / aç | 8 ağır çelik panjur paneli pencere önünde hareket eder. Tam kapanma yaklaşık **2,5 saniye** sonra koruma sağlar. Açık cam varken bile arka sığınak korur. |
| Basınç / buhar | Tahliye et | 12 bacadan buhar yükselir, basınç anında **21 puan** düşer; yeniden kullanım bekleme süresi vardır. |
| Manyetik muhafaza | Aç / kapat | Bobinler ve dönen halkalar canlanır/söner, termal denge etkilenir. |
| Şebeke / jeneratör | Bağla / ayır | 4 jeneratör ve hatları yanar/söner; şebekeden ayrılınca **MW çıkışı sıfır** olur. |
| Bakım / hat onarımı | Onar | Sırayla kopuk bir boruyu; sonra kırık/çatlak gözlem camını; sonra etkin arızayı; en son muhafaza zırhını onarır. Yaklaşık **11 saniye** bekleme süresi vardır. |
| Acil kapatma | SCRAM / yeniden başlat | Çubuklar ve pompalar emniyet konumuna alınır, lazerler kapanır; güvenli ısı/basınç sonrası yeniden başlatılabilir. |
| Sağ yan duvar: su baskını | Aç / kapat | 12 tavan nozulu odaya soğutucu püskürtür; termal hedef yaklaşık **90°C** düşer. İleri evrede kaçınılmaz hale gelen meltdown'ı tek başına durdurmaz. |

Kontrol odası yıkımında cam/panjur/sığınak ayrı sistemlerdir: **pencereyi kapatmak** camı silmez; panjuru çekip pencereyi fiziksel olarak örtersin. Cam çatlar veya kırılırsa bakım konsolu onarabilir. Sığınak ortadaki **yeşil işaretli zırhlı kabindir**.

## Oyun döngüsü

- Dengeli üretimde MW kazan, **50 saniyelik güvenli enerji sözleşmelerini** tamamlayarak kredi topla. Sözleşme için yeterli güç yanında sıcaklık `<945°C`, basınç `<%85`, muhafaza `>%64`, hiç kopuk boru olmaması gerekir. İlerledikçe MW hedefi artar.
- Denemek için örnek bir **başlangıç ayarı**: Önce soğutmayı üç kez artırıp `%100` yap; çubukları iki kez geri çekip `%20` yap; akıyı üç kez artırıp `%79` yap; en sonunda lazerleri aç. Arıza yokken yaklaşık **843 MW**, dengede **833°C** ve **%83 basınç** öngörülür. Parametreleri HUD'dan izle: gerçek davranış, geçiş süreci ve olası arızalar önemlidir.
- Kaçak, sıkışmış valf, manyetik sapma ve şebeke kısa devresi olabilir. Kırık hatlar gerçek soğutmayı azaltır; bakım konsolunda sırayla düzeltilir. Aşırı basınç da boru patlatabilir.
- Isı/basınç uzun süre tehlikeli bölgede kalırsa veya muhafaza bütünlüğü biterse aşamalı **meltdown** başlar.

### Meltdown sahnesi

1. **0–7 sn:** Siren, plazma düzensizliği, elektrik atlaması ve ilk boru kopması.
2. **7–16 sn:** Eriyen zemin, ikinci boru, artan buhar, korumasız camda çatlaklar. Mekanizma hâlâ uygunsa ilk **16 saniyede SCRAM** ile süreç kesilebilir.
3. **16–27 sn:** Çekirdek muhafazası çatlar; SCRAM kilitlenir, servis kirişleri kopar.
4. **27–35 sn:** Panjur tam mühürlü değilse gözlem camı parçalanır, parçalar kontrol odasına saçılır. Panjur kapalıysa darbe zırhta karşılanır.
5. **Yaklaşık 35. sn:** Çekirdek yıkımı, şok dalgası, patlama sesi, ışık patlaması, kamera sarsıntısı, uçan parçalar, boru hatlarının dağılması; sığınakta veya mühürlü panjur gerisinde duran oyuncular korunur.

Ardından sistem **otomatik onarıma** geçer ve meltdown başlangıcından yaklaşık **68 saniye** sonra yeni vardiya açılır. Sağlıklı/erken SCRAM sonrası yeniden başlatma için ısı **740°C veya altında**, basınç **%62 veya altında** olmalıdır. Çatlamış cam SCRAM ile sihirli biçimde düzelmez; bakım konsolunu kullan.

## Studio içinde hızlı test

- **Dünya testi:** F5 ile doğ; kontrol odasındaki camdan çekirdeği gör, odanın sağ yanındaki su baskınını aç, tavandaki nozul parçacıklarını kontrol et.
- **Canlı kontrol testi:** Lazerleri aç/kapat; çekirdeğe uzanan 10 ışını gör. Panjuru kapat; panellerin aşağı inip birkaç saniye sonra muhafazaya kilitlendiğini gör. Ekranda ve HUD'da anahtar durumları değişmeli.
- **Kriz testi:** Studio Play'de kontrol odası arkasındaki **turuncu “MELTDOWN TESTİ” düğmesi** görünür (canlı oyunda görünmez). Basıp açık panjurla tüm sahneyi izle; başka testte önce panjuru kapatıp camın korunmasını karşılaştır. Düğmeden hemen sonra uygun durumda SCRAM'a koşarsan felaketi iptal edebilirsin.
- **Çok oyunculu test:** Studio → Test → birden çok oyuncuyla başlat. Bir oyuncu konsola basarken diğer oyuncunun da **aynı lazerleri, panjuru ve kırılan boruları** görmesi gerekir.
- **Output penceresi:** Beklenmedik bir durum olursa `View → Output` içindeki `[HELIOS-9 V2]` satırlarına ve kırmızı hatalara bak.

## Ses, performans ve özelleştirme

- Sesler `HELIOS_9_V2_Server.server.lua` başındaki `SETTINGS.AUDIO` bölümündedir. Roblox Creator Store'da bulunabilen örnek varlık kimlikleri kullanılır; **deneyimin/hesabın oynatma izinleri nedeniyle bazı sesler yüklenmeyebilir**. Böyle olursa erişebildiğin ses ID'leriyle değiştir. Ses erişimindeki sorun dünya, efektler veya oynanış için engel oluşturmaz.
- Sunucu kodundaki `SETTINGS.STUDIO_TEST_LEVER`, meltdown test düğmesini Studio için etkin tutar. `MELTDOWN_SCRAM_WINDOW`, `MELTDOWN_DETONATION_AT`, `ROUND_RESET_AT`, arıza sıklığı ve sözleşme süresi aynı yerde ayarlanabilir.
- Bu, **çok parçalı, efektli büyük bir sahne**dir. Düşük donanımlarda parçacık oranlarını, dinamik ışıkları ve animasyon sıklığını azaltmak gerekebilir. Başka bir oyuna yerleştireceksen sahne merkezini ve spawn koordinatlarını kaynak kodda uyarlaman gerekir.
- Güvenlik modeli: fiziksel `ProximityPrompt` → sunucuda mesafe/sağlık/bekleme doğrulaması → sunucu simülasyonu → oyunculara durum yayını. HUD ve kamera efektleri sadece yerel sunumdur.

**Dosyalar:** `HELIOS_9_V2_Server.server.lua` + `HELIOS_9_V2_Client.client.lua`. Önceki `HELIOS_9_Tek_Script.server.lua` V1 olarak ayrı saklanır; yeni sürüm ona kod eklemek yerine baştan kurulmuş daha büyük bir deneyimdir.

**Doğrulama notu:** İki dosya sözdizimi ve statik bağ kontrollerinden geçirildi. Buradan doğrudan Roblox Studio Play testine erişim olmadığı için gerçek Roblox çalışma zamanı / cihaz performansı kesin olarak doğrulanamadı.
