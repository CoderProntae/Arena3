# Roblox Studio MCP — kullanıcı tarafından çalıştırılan canlı köprü

Bu paket, **bu sohbet için** hazırlanmış bir Windows Python istemcisidir. Roblox Studio'nun kendi `%LOCALAPPDATA%\Roblox\mcp.bat` MCP sunucusunu Windows bilgisayarında başlatır. Benim çalışma alanımla **giden HTTPS bağlantısı** üzerinden konuşur. Böylece bağlantı gerçekten kurulursa Studio modelini okuyabilir, ekran görüntüsü alabilir ve **yalnızca sen terminalde her isteği ayrıca onaylarsan** Play, Luau, script değişikliği ve giriş simülasyonu isteyebilirim. Roblox hesabının şifresi veya API anahtarı gerekmez. Windows'ta kullanıcı istemcisi MCP el sıkışmasını yapıp 28 araç listeledi; **açık Studio yerini görme/düzenleme henüz doğrulanmadı**. Bu yeni SSH/HTTPS tünelinde ayrı bir sahte-MCP istek/yanıt testi de geçti.

## Senin yapacağın

1. Roblox Studio'yu ve **çalışacağımız yerin bir yedeğini** aç. Studio'da **Asistan → MCP Sunucuları → Studio'yu MCP sunucusu olarak etkinleştir** seçeneğinin açık olduğunu doğrula. Windows'ta Python 3 kurulu olsun.
2. ZIP'i indirip Windows'ta bir klasöre çıkar. `Roblox_Studio_MCP_Bridge.py` dosyasını çalıştırmadan önce istersen düz metin editörüyle incele. **Dosyada bu oturuma özgü erişim anahtarı vardır; dosyayı başkalarına gönderme.**
3. Çıkardığın klasörde PowerShell aç ve `py -3 .\Roblox_Studio_MCP_Bridge.py` çalıştır. Windows'ta `py` komutu yoksa `python .\Roblox_Studio_MCP_Bridge.py` dene. Dosyaya çift tıklama: hata olursa konsol hemen kapanabilir.
4. Konsol açık kalsın. `[MCP] Connected. Server advertises ... tools.` ve ardından `[bridge] Online; ...` yazmasını bekle. Studio MCP ayarlarındaki **yeşil bağlı istemci göstergesine** de bak. Sonra bu sohbete **"Köprü bağlandı"** yaz. Ben önce Studio oturumlarını listeleyeceğim; yer kimliğini ancak listeden aldıktan sonra kullanacağım.
5. **İki önceki Cloudflare adresi de devre dışı.** Bu sürüm varsayılan olarak `https://35c8e6eeb824e3.lhr.life` üzerinden bir **localhost.run SSH/HTTPS tüneline** bağlanır. Hâlihazırda HTTP/2 paketini indirdiysen yeniden indirmeden PowerShell'de önce `$env:ARENA_STUDIO_RELAY_URL='https://35c8e6eeb824e3.lhr.life'`, ardından `python .\Roblox_Studio_MCP_Bridge.py` çalıştırabilirsin. Adres ileride değişirse aynı değişkeni yeni adresle ayarla; yeni adresi yalnızca benden aldığında kullan. `[bridge] Online` görünmeden sohbetten Studio işlemi isteyemem.
6. Studio'yu etkileyen **her** işlem (`start_stop_play`, `multi_edit`, `execute_luau`, fare/klavye/giriş) terminalde ayrıntıları gösterilerek **YES** ister. İstemediğin işlemde sadece Enter ile reddet. Uzun kodlarda tam parametreler onay süresince geçici bir JSON dosyasına yazılır; yol konsolda gösterilir. Bağlantıyı istediğin zaman **Ctrl+C** ile kes.

## Güvenlik ve sınırlar

- Bilgisayarında dinleyen ağ portu açılmaz; istemci yalnızca Studio'nun **yerel stdio** sunucusunu çalıştırır ve dışarıya HTTPS istekleri yollar.
- Arena önizleme adresi dışarıdan otomatik bağlanmayı reddettiği ve Cloudflare Quick Tunnel iki kez `530` verdiği için geçici **localhost.run SSH/HTTPS tüneli** kullanılıyor. Açık place'in kodu, MCP cevapları ve ekran görüntüleri bu üçüncü tarafın HTTPS uç noktası üzerinden bu oturuma taşınabilir. Gizli bir proje veya kişisel veri içeren pencereyle deneme. Uç noktada **ayrı rastgele çalışan/ajan anahtarları** bulunur; yalnızca çalışan anahtarı Windows dosyasındadır. Ücretsiz tünel geçicidir; SSH bağlantısı kesilirse bu dosyadaki adres geçersizleşebilir.
- Kullanıcının Windows bilgisayarındaki gerçek Studio MCP sunucusuyla bağlantı **henüz doğrulanmadı**. Sorun olursa konsoldaki **hata metnini** buraya yapıştır; erişim anahtarını veya Python dosyasının tamamını yapıştırma.
- Köprü Roblox Studio'nun sunduğu araçlarla sınırlıdır. Çok sayıda Studio penceresi açıksa hangisinde çalışılacağını beraber seçeceğiz. Değişiklikler otomatik yayımlanmaz; önce yedek ve Studio Play denetimi yap.
- Resmî Studio MCP açıklaması: https://create.roblox.com/docs/studio/mcp
