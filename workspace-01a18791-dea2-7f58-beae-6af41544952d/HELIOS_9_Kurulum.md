# HELIOS-9 — Roblox reaktör kontrol oyunu

**Ana dosya:** [`HELIOS_9_Tek_Script.server.lua`](HELIOS_9_Tek_Script.server.lua)

## Kurulum

1. Roblox Studio'da yeni bir **Baseplate** açın.
2. **Explorer → ServerScriptService → + → Script** seçin.
3. Yeni Script'in içindeki varsayılan kodu silip ana dosyanın **tamamını** yapıştırın.
4. **Play (F5)** ile deneyin. `Workspace/HELIOS9_RUNTIME_WORLD` ve oyuncu HUD'u otomatik oluşur.
5. Çalıştığından emin olduktan sonra place'i kaydedip yayınlayın. Harita her sunucu açılışında bu tek Script'ten yeniden üretilir; Play'deki üretilmiş nesnelerin ayrıca kaydedilmesi gerekmez.

> Önemli: Roblox, oyun çalışırken bir Script'in başka scriptlerin `Source` alanına kod yazmasına izin vermez. Bu sürüm **bunu yapmaz**: dünya, kontrol sistemi, arayüz ve efektler tek bir ServerScript tarafından `Instance.new` ile oluşturulur. Başka Script/LocalScript/RemoteEvent gerektirmez.

## Oyunda neler var?

- Dairesel, çatılı endüstriyel tesis; duvarlar, kolonlar, geçit ışıkları, zırhlı sığınaklar, cam muhafaza.
- Hareketli çok eksenli reaktör halkaları, plazma çekirdeği, kumanda çubukları, türbinler, çift sarmal soğutma hattı ve tanklar.
- Yedi etkileşimli istasyon: **akı**, **soğutma**, **basınç tahliyesi**, **kontrol çubukları**, **manyetik stabilizasyon**, **SCRAM/yeniden başlatma** ve **bakım**.
- Dinamik sıcaklık/basınç/zırh simülasyonu, arızalar, enerji üretim sözleşmesi, takım kredileri ve vardiya sayacı.
- **Aşamalı meltdown:** acil kilit/panjur ve alarm → buhar ve eriyen zemin → çatlayan muhafaza ve elektrik arkları → çekirdek patlaması, beyaz flaş, iki darbe halkası, fiziksel parçalar, serpinti, oyuncu hasarı → tesisin otomatik yeniden kuruluşu.
- Patlamadan önce sığınakta bekleyen oyuncuya hayatta kalma kredisi. Meltdown başladıktan sonraki **ilk 14 saniyede**, muhafaza bütünlüğü yeterliyse SCRAM ile süreci durdurabilirsiniz.

## Kontroller ve hızlı test

- **WASD / mobil hareket** ile gezin; konsoldaki renkli düğmeye yaklaşınca **E / dokunma istemini** kullan.
- Meltdown görmek için akıyı artırıp soğutmayı azaltın ve kontrol çubuklarını geri çekin. Ayarlar uç noktalara ulaştıktan sonra kritik durum yaklaşık saniyeler içinde başlar; akabinde aşamalı sahne devreye girer.
- Kırmızı **SCRAM** istasyonuna zamanında ulaşarak reaktörü kurtarın veya dış çevrede **yeşil SIĞINAK** yazan açık alanlardan birine girin.
- SCRAM sonrası ısı **720°C altında**, basınç **%62 altında** olduğunda aynı istasyondan yeniden başlatın.

## İsteğe bağlı sesler ve sınırlar

Script başındaki `SETTINGS.AUDIO` tablosuna **kullanma izniniz olan** `rbxassetid://...` ses ID'lerini girebilirsiniz. Varsayılan olarak alanlar boştur; bütün oynanış ve görsel efektler harici ses varlığı olmadan çalışır. `Kredi` ve `Vardiya` skorları **oturumluk** tutulur; DataStore eklenmemiştir.

Lua sözdizimi statik olarak kontrol edilmiştir. Roblox Studio motorunda burada Play testi yapma olanağım olmadığı için kendi Studio sürümünüzde **Play + Output** üzerinden çalışmasını kontrol edin.
