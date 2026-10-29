# HELIOS-9 V4 — Doğrulama notu

**Bu ortamda Roblox Studio çalıştırılmadı.** Aşağıdakiler sözdizimi/kaynak/geometri kontrolleridir; görsel kalite ve katalog seslerinin oyunda açılması ayrıca Studio Play ile doğrulanmalıdır.

- `luaparse` ile sunucu ve istemci Luau sözdizimi: **geçti**.
- İki kod dosyası toplamı: **3.386 satır**, 8.000 sınırının altında.
- Tıklanabilir işlev: **tam üç `MouseClick` bağlantısı** (soğutma, lazer, SCRAM). Yeni dekor panoları/tuşları interaktif değil. `ScreenGui` ve `ProximityPrompt` örneği yok.
- Kapalı koruma: 9×8 = 72 hücre; **54 merkez cam %98 geçirgen, 18 dış çelik opak**. Dokuz analitik kontrol odası → yıldız ışınının hiçbiri opak kanada düşmedi; cam penceresinin dikey açıklığı içinde kaldı. Studio Script'inde ayrıca **gerçek Workspace Raycast ile kapalı koruma üzerinde dokuz ışınlık uyarı testi** var; sonucu yalnız Play sırasında Output'ta görülebilir.
- Merkezde 6 ayrılabilir yayıcı, 3 kırılabilir ön halka, 26 sürekli konum değiştiren ark, 18 ayrı zamanlı olay ve yaklaşık **180 saniyelik** felaketin sonunda büyük çekirdek patlaması kodda mevcut.
- Kullanılan 16 SFX anahtarının tümü `CONFIG.AUDIO` içinde tanımlı; varlıklar `rbxassetid://` biçiminde. Üç müzik hareketi ve istemcide çapraz geçiş tanımlı. **Roblox oynatma izinleri doğrulanmadı.**
- V3'ün sunucu, istemci ve kılavuz dosyaları önceki V3 ZIP paketindeki sürümlerle **bayt bayt aynı**; V1/V2 kaynakları da değiştirilmedi.

**Studio görsel kabul testi:** V4 kurulumunu Play ile açın; doğduğunuz noktada parlayan altı kollu merkezi kontrol edin. `STUDIO_TEST_AFTER_12_SECONDS=true` ile otomatik tetikleyin. Yan kanatlar kapanırken yıldızın kaybolmaması, yaklaşık 35/54/82/96/122/151. saniyelerde yayıcı ve halka kopması, alarm odasının kırmızıya dönmesi ve finalde olayın doğrudan yıldız merkezinden çıkması beklenir. Output'taki görüş uyarısını ve ses yetki mesajlarını kontrol edin. **Burada bu Play sonucu gözlemlenmedi, garanti edilmez.**
