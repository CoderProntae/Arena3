# HELIOS-9 V3 — uzun, yazısız ve fiziksel meltdown

Bu sürüm geri bildirime göre **V2'nin yanına ayrı bir sürüm** olarak yazıldı. V1/V2 dosyalarını silmez. Reaktör, çok katmanlı zırhı, 24 hareketli çubuğu, 12 ayrı soğutma hattı, 12 odak lazeri, jeneratörleri, sızıntı birikintileri, çökebilen çatısı ve delinebilen cam panjuruyla oyun başladığında kodla üretilir.

**Oyuncuya gösterilen evre metni, zaman sayacı, olay günlüğü, büyük dijital panel veya özel HUD yoktur.** Arka duvarda yalnızca üç **fiziksel ibreli ölçüm cihazı** vardır; üç kumandanın üzerindeki kısa metal isimlikler ne işe yaradıklarını söyler. Tesisin bozulduğunu su, kıvılcım, sallanan makine, ışıksız kalan jeneratör, metalde açılan gerçek delikler ve seslerle anlarsın.

## 1) Script kurulumu

1. Roblox Studio'da **V1 ve V2 Server Script'lerini ve V2 LocalScript'ini devre dışı bırak**. Önceki dosyaları saklayabilirsin. Aynı anda yalnızca V3 çalışmalı.
2. `ServerScriptService` içine yeni bir **Script** ekle; içeriğini tamamen silip `HELIOS_9_V3_Server.server.lua` dosyasını yapıştır.
3. `StarterPlayer → StarterPlayerScripts` içine yeni bir **LocalScript** ekle; içeriğini tamamen silip `HELIOS_9_V3_Client.client.lua` dosyasını yapıştır.
4. **Play (F5)** ile test et. Model `Workspace.HELIOS9_V3_WORLD`, sunucudan istemciye yalnızca sinematik ipuçları taşıyan olay `ReplicatedStorage.HELIOS9_V3_CUES` altında otomatik oluşur. RemoteEvent, GUI veya Toolbox modeli ekleme.
5. Deneyimde daha önce yerleştirilmiş spawn'lar V3 çalışırken devre dışı bırakılır; oyuncu camlı kontrol odasında reaktöre bakarak doğar.

> V3 istemcisinde `ScreenGui` oluşturulmaz. Roblox'un varsayılan sağlık/oyuncu listesi/çanta katmanları da kapatılır; sohbet ve Roblox'un temel menüsü bırakılır.

## 2) Oyuncu ne yapar?

Kontrol odasındaki **üç büyük metal kolu fareyle tıkla veya mobilde dokun**. Sürekli açılan ProximityPrompt yoktur.

| Tek kumanda | Davranış | Fiziksel karşılık |
|---|---|---|
| **SOĞUTMA** | Her tıklamada sırasıyla `%70 → %100 → %0 → %35 → %70` döner. | Gerçek depoların sıvı seviyesi, pompa kanatları, boru akışının rengi ve ısı dengesi değişir. `%100` sonrasında tekrar tıklayınca `%0` olur: dikkat et. |
| **LAZER** | Isıtmayı aç/kapat. | 12 odak huzmesi çekirdeğe vurur; ışık ve sıcaklık artar. Felakette lazer kafaları fiziksel olarak arızalanabilir. |
| **SCRAM** | Koruma kapağını kaldırıp reaktörü acilen durdurur. | 24 çubuk fiziksel olarak iner, lazer kesilir ve soğutma tam güce geçer. Felaket ilerleyip mekanizma kilitlenirse çubukların yalnızca kısmen inip sıkıştığı gözle görülür. |

**Panjur düğmesi yoktur.** Tehlike yükselince panjur kendiliğinden, yaklaşık **9 saniyede** camın önüne iner. 72 ayrı metal karodan oluşur: evreler ilerledikçe bazı karolar **gerçekten kopar**, metale kalıcı delikler açılır; daha sonra camın kendisi parçalanır. Tavandan su püskürtülmesi ve sığınak kapaklarının kapanması da otomatiktir. Cam odasının arkasındaki yeşil ışıklı ağır kabin sığınaktır.

Soğutma ve lazerle oynayıp çekirdeğin tepkisini izle. Orta soğutmada açık bırakılan lazerler zamanla kaçak ve meltdown'a yol açar; **%100 soğutma**, arıza yokken ısıyı kırılma eşiğinin altında tutabilir, ama borudaki sızıntı ve yüksek ibreler hâlâ tehlikeyi gösterir. Lazerleri kapatmak iyileşmeyi hızlandırır. Güvenli müdahale fırsatı vardır: meltdown başladıktan sonraki ilk **45 saniyede** SCRAM başarılı olabilir. Sonrasında mekanizma fiziksel olarak sıkışır; felaket kendi akışında sürer.

## 3) Yaklaşık üç dakikalık sahne (geliştirici notu; oyuncuya gösterilmez)

Bu çizelge **ekranda hiçbir yerde görünmez**. Test sırasında neye bakacağını anlatır:

| Yaklaşık zaman | Oyunda görülen fiziksel olay |
|---|---|
| Ön işaretler | Analog ibreler yükselir; oda sıcak tonda yanar, uğultu düzensizleşir, panjur kendiliğinden kapanır. |
| 11–40 sn | Boru gövdesinden soğutma suyu ve buhar sızar; **zeminde büyüyen birikinti** oluşur. Hat kopunca gerçek boru kesiti yok olur, parçaları uçar. İkinci ve üçüncü hatlarda ayrı kaçaklar gelişir. |
| 54–82 sn | Bir lazer kafası kopar, jeneratörlerden biri kararır, farklı borular kırılır. İkinci alarm devreye girer; tavan su püskürtme sistemi kendiliğinden çalışır. |
| 96–122 sn | Zeminde merkezden dışa **parça parça yayılan kızgın yarıklar** açılır. Gözlem camı çatlar; panjurun farklı bölgelerine darbeler iner ve metal karolar koparak **iki gerçek delik** açılır. |
| 137–159 sn | Reaktörün ayrı zırh yaprakları açılıp yırtılır, muhafaza camı çatlar, çatı traversleri düşer, panjurun daha büyük bir bölümü parçalanır. Ardından gözlem camı kırılır; yağmurlama su basıncını kaybeder. |
| 168–180 sn | Arka sığınağın kapakları otomatik kapanır; elektrik ve siren aniden kesilir, son derin uğultu duyulur. **Yaklaşık 180. saniyede** çekirdek şok dalgalarıyla patlar. Sığınakta kalanlar korunabilir. |

Patlamadan sonra enkaz ve duman bir süre kalır; borular, cam ve makine **aşamalı onarılır**. Oyun kendi kendine yeni vardiyaya döner. Metinle “evre 3” demez, sayaç açmaz.

## 4) Ses ve özgün müzik — önemli kurulum

`HELIOS_9_V3_Ses/` klasöründe **bu proje için sıfırdan sentezlenmiş**, örnek veya başka oyundan müzik kopyalamayan yedi adet `.ogg` vardır. Ana parça `HELIOS9_V3_Meltdown_180s.ogg` tam üç dakikadır; sessiz gerilimden endüstriyel vuruşlara yükselir, final patlamasından hemen önce susar. İstersen diğer altı ses de özgün efekt olarak kullanılır.

**Roblox, bilgisayardaki `.ogg` dosyasını Script'ten doğrudan çalamaz.** En iyi ses deneyimi için Studio **Asset Manager → Import** ile dosyaları **oyununla ilişkili hesabın/grubun ses varlıkları** olarak yükle; her biri için oluşturulan sayısal **asset ID**'yi al. `HELIOS_9_V3_Server.server.lua` başındaki `CONFIG.AUDIO` tablosunda karşılık gelen değeri `"rbxassetid://SENIN_ID"` biçiminde değiştir:

| Ses dosyası | Sunucudaki anahtar | Nereye etki eder? |
|---|---|---|
| `HELIOS9_V3_Meltdown_180s.ogg` | `score` | Üç dakikalık oyuncuya özel müzik. **Önce bunu yükle.** |
| `HELIOS9_V3_Tesis_Ugultusu.ogg` | `idle` | Normal reaktör uğultusu. |
| `HELIOS9_V3_Uzak_Siren.ogg` | `siren` | Krizde yavaş siren. |
| `HELIOS9_V3_Su_Sizintisi.ogg` | `hiss` | Konumsal, sürekli kaçak sesi. |
| `HELIOS9_V3_Boru_Patlamasi.ogg` | `rupture` | Metal borunun fiziksel kopması. |
| `HELIOS9_V3_Panjur_Delinmesi.ogg` | `breach` | Panjur metalindeki gerçek delik. |
| `HELIOS9_V3_Nihai_Patlama.ogg` | `explosion` | Final patlaması. |

Diğer olaylar (ikinci alarm, kıvılcım, cam kırılması, elektrik, metal çökmesi, kapak motoru ve yağmur) için kodda ayrıca Creator Store örnek ses kimlikleri yer alır. **Örnek seslerin senin deneyiminde oynatma izni olduğunu buradan doğrulayamıyorum.** Ses duyulmazsa Studio **Output**'taki varlık erişim uyarılarını incele; kendi içe aktardığın dosyaların/deneyiminin izinlerini kontrol et ve ilgili `CONFIG.AUDIO` anahtarını değiştir. Özellikle özgün `score` dosyasını yüklemek, müziği rastgele bir katalog varlığına bağlı bırakmaz. Resmî belge: https://create.roblox.com/docs/audio/assets

Dosyalar mono/24 kHz `.ogg` biçimindedir; en uzunu 180 saniye ve yaklaşık 1 MB'tır. İstersen `HELIOS_9_V3_Ses/ses_uret.py` ile özgün sentezi yeniden üretebilirsin.

## 5) Düzgün test etme

- **Normal test:** Play'e bas; lazer koluna dokun. Çekirdeğe giden huzmeleri, ısınan ibreyi ve bir süre sonra inen panjuru izle. Felaket hemen patlamaz. Soğutmayı yükselt ve lazeri kapatınca sistemin toparlandığını da dene.
- **Tam sahne testi:** Sunucu Script'inin başında `STUDIO_TEST_AFTER_12_SECONDS = true` yap; Play'e yeniden bas. Studio'da yaklaşık 12 saniye sonra sahne kendiliğinden başlar. **Yeni bir test düğmesi eklenmez.** Tüm 180 saniyeyi, SCRAM'a basmadan seyret. İşin bittiğinde ayarı `false` yap.
- **Müdahale testi:** Ayrı bir Play oturumunda ilk 45 saniyede SCRAM koluna tıkla. Bir sonraki denemede geç bas ve çubukların sıkışmasını gözlemle.
- **Çok oyuncu testi:** Studio'nun çoklu oyuncu modunda bir oyuncu lazeri/soğutmayı değiştirirken diğeri aynı fiziksel makineyi görmeli. Tüm kontrol kararları sunucudadır.
- **Düşük donanım:** Bu V3'te yüzlerce metal/ışık parçacığı, 12 hat, 72 panjur karosu ve hareketli halkalar vardır. Gerekirse parçacık `Rate` değerlerini veya sunucunun `animAccumulator >= 0.10` eşiğini yükselterek animasyon yükünü azaltabilirsin.

**Doğrulama notu:** Kodlar Lua sözdizimi ve statik bağlantı kontrollerinden geçirildi. Bu ortamda Roblox Studio Play testi yapılamadığı için hesap/deneyim ses izinlerini ve gerçek cihaz performansını Studio'da ayrıca doğrulamalısın.
