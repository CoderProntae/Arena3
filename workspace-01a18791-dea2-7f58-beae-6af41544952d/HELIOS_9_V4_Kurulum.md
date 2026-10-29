# HELIOS-9 V4 — Görünen Çekirdek

V3'teki hatayı **ayrı bir sürümde** düzelten prosedürel Roblox reaktör oyunu. V1, V2 ve V3 dosyalarına dokunulmadı. **V4'ün tamamı iki Luau dosyasıdır; üçüncü taraf model, dış ses dosyası veya HUD gerekmez.**

## Kurulum

1. Roblox Studio'da bir **Baseplate** açın. Önceki sürümlerin çalışan Script/LocalScript örneklerini **devre dışı bırakın**; dosyalarını silmeniz gerekmez.
2. `ServerScriptService` içine normal bir **Script** ekleyin. İçeriğinin tamamını `HELIOS_9_V4_Server.server.lua` ile değiştirin. Aynı sunucu Script'inden yalnızca **bir** kopya çalışsın.
3. `StarterPlayer > StarterPlayerScripts` içine **LocalScript** ekleyin. İçeriğinin tamamını `HELIOS_9_V4_Client.client.lua` ile değiştirin.
4. **Play (F5)** başlatın; yalnız `Run` kullanmayın. Avatar kontrol odasının orta aksında, parlak çekirdeğe bakarak doğar; istemci referanstaki gibi **birinci şahıs kamera** kullanır, avatar görüşü kapatmaz. İnşa edilen sahne `Workspace > HELIOS9_V4_WORLD` altındadır.
5. Önce normal durumdaki yıldızı görün. Soğutmayı %70'ten %100'e çıkaran ilk tıklamayı, lazer kolunu ve SCRAM'i ayrı ayrı deneyin. Meltdown'a geçmek için lazerleri açıp soğutmayı %70 veya daha aza bırakın. `ServerScriptService` Script'inin başındaki `STUDIO_TEST_AFTER_12_SECONDS=true` yalnızca **Studio'da**, testi 12 saniye sonra otomatik başlatır; oyuncuya süre/evre göstermez. Yayından önce `false` bırakın.

## V3'ten gerçek farkı

- Önceki **opak 72 parçalı perdenin yerinde** yine 9 × 8 hareket eden bir koruma matrisi vardır; fakat **54 merkez parça %98 geçirgen cam**, yalnızca **18 dış kanat çelik**. Merkez karoların kaynak dikişleri de görünmez. Kapatıldığında karakterlere çarpan koruma **çekirdeğin önünü kapatmaz**; yalnız ince, ışıldayan bir çerçeve merkezde enerji kalkanı olduğunu belli eder. Soldaki ve sağdaki çelik kanatlar ileride fiziksel olarak delinebilir. Merkez şeffaf laminat da parçalanabilir.
- Gözlem penceresi 11 dar/lekeli camdan **beş geniş, %95,5 geçirgen panoramik panele** dönüştü. Çekirdeği örten öndeki iki zırh yaprağı termocamdır; tam orta eksendeki eski lazer namlusu da şeffaftır. Üç kumanda tezgâhı görüş konisinin **yanlarına taşındı**.
- Kameraya dönük **altı büyük mekanik ışın yayıcı** (uzun siyah namlu, indüksiyon bilezikleri, lens, pençeler), yüz yüze görülen üç döner manyetik halka, mor-beyaz **altı kollu yıldız**, akkor merkez ve canlı plazma arkları eklendi. Yayıcılar birer birer kopar; halka bölümleri gerçek parçalar bırakarak kırılır. Olaylar uzak su jetlerinde değil **görünür çekirdeğin ön düzleminde** olur.
- Geniş parlak karo zemin, yalnız yanlarda duran eğik konsollar, iki duvarda fiziksel alarm matrisi/osiloskop, tepede kırmızıya dönen ışık bankası ve çekirdeğin **arkasındaki** turuncu tehlike panelleri sahneyi doldurur. Dekor düğmeleri **çalışmaz**. `ScreenGui`/geri sayım/oyuncuya yazılı evre açıklaması **yoktur**.

## Kumandalar ve oyun

**Tıklanabilir parça sayısı üç:** solda **SOĞUTMA** (`x≈−45`), sol-ortada **LAZER** (`x≈−25`), sağda kapaklı **SCRAM** (`x≈+36`). Hepsi `z≈147` çizgisindedir. Soğutma %70 → %100 → %0 → %35 → %70 döngüsü yapar. Lazer anahtarı ışınları reaktörün üzerinde gerçekten yakıp söndürür. SCRAM kontrol çubuklarını fiziksel olarak indirir; meltdown başladıktan **ilk 45 saniyede** kullanılınca kurtarma olasıdır, geç basılırsa çubuklar sıkışır. İç ikaz lambaları, analog göstergeler, kollar ve reaktör renkleri durumu sözcüksüz anlatır.

Meltdown'ın aktif yıkım süresi **yaklaşık 180 saniye**; oyuncuya hiçbir sayaç gösterilmez. Teknik gözlem sırası (oyunun içinde yazılmaz): ilk saniyelerde yıldız dalgalanması ve yan kanatların kapanması; yaklaşık 35–96. saniyelerde yayıcıların ve halkaların ardışık kopması, cam/boru/zemin gerilimi; 108–159. saniyelerde kanat delinmesi, merkezde çatlak ve patlayan cam; son dakikanın sonunda merkezde genişleyen/sıkışan enerji, sığınak ve **çekirdekten doğan büyük patlama**. Patlamadan sonra otomatik temizlik/yeniden başlangıç vardır. Ana görsel her evrede hâlâ görüş eksenindedir. Bunker kapısı otomatik çalışır, dördüncü kumanda değildir.

## Roblox katalog sesleri

V4 **Roblox `rbxassetid://` varlıklarını** kullanır. Sunucu dosyasının başındaki `CONFIG.AUDIO` değiştirilebilir. Örnek müzikler: `1843973421` (açılış), `9040229071` (yükseliş) ve `9042675817` (final). Ses örnekleri arasında iki siren (`9113073742`, `9113073796`), metal kırılması (`9116554136`), plazma (`9125742111`), su (`9120562287`), patlama ve darbeler bulunur. Müzik istemcide çift Sound kanalıyla çapraz geçer; mekânsal sirenler/efektler sunucuda fiziksel konumdan duyulur. **V3'ün OGG dosyaları V4 için gerekli değildir.**

Katalog sayfaları örnek olarak: [Caution](https://create.roblox.com/store/asset/9040229071/Caution), [Chase Me](https://create.roblox.com/store/asset/9042675817/Chase-Me), [siren](https://create.roblox.com/store/asset/9113073796/Air-Raid-Siren-Old-Fashioned-2-SFX), [plazma](https://create.roblox.com/store/asset/9125742111/Plasma-Trails-Constant-Airy-Whooshing-Windy-SFX). **Creator Store'da görünmesi, oyununuza oynatma izni verildiğinin garantisi değildir.** Studio Output'ta ses izin/404 hatası çıkarsa deneyimin erişebildiği başka bir katalog varlığına ilgili `CONFIG.AUDIO` ID'sini değiştirin. Gerçek ses erişimini ancak Studio/oyun hesabınız doğrulayabilir.

## Görüş ve kalite kontrolü

Studio Play sırasında **Output** penceresini açın. Kod, Studio'da açık panjura müdahale etmeden kapalı konumdaki korumayı anlık olarak kurup merkez yıldız için **dokuz görüş ışını** kontrol eder. Başarı mesajı `Kapali panjurda 9/9 cekirdek gorus ...` biçimindedir; engel bulunursa nesne adını uyarı olarak yazar. Ayrıca 54 şeffaf merkez karo için otomatik `assert` vardır. Bu teknik test, avatarla camın önüne gidip **normal → kapalı yan kanat → delinen kanat → final** evrelerini gözle görerek doğrulamanın yerine geçmez.

Kamera sarsıntısı/flaş ve müzik **LocalScript** olmadan eksik kalır. Ses izinleri, grafik performansı, gerçek ışık/glass görünümü ve Script çalışma zamanı bu çalışma ortamında **Roblox Studio açılamadığı için test edilmedi**; Luau sözdizimi ve statik/geometrik kurallar kontrol edilmiştir. Yoğun parçacık/Neon efektleri zayıf cihazlarda kalite ayarı gerektirebilir. Bir görüntü hâlâ kapanıyorsa **Output uyarısı + çekirdek/cam ekran görüntüsü** paylaşın; sahneyi buna göre düzeltebiliriz.

**Dosyalar:** `HELIOS_9_V4_Server.server.lua` → ServerScriptService; `HELIOS_9_V4_Client.client.lua` → StarterPlayerScripts. Sunucu+istemci toplamı 8.000 satır sınırının altındadır.
