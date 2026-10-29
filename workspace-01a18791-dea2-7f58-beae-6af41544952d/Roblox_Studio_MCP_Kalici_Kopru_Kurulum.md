# Roblox Studio MCP — tünelsiz, şifreli bağlantı

Önceki Cloudflare/SSH tünelleri birkaç dakika sonra `530`/`502` vererek koptu. Bu paket **hiçbir dışa açık tünel açmaz**: senin Windows istemcin ile bu oturumdaki ajan, üçüncü taraf `https://ntfy.sh` üzerinde birbirinden bağımsız **giden HTTPS** istekleriyle şifreli komut/sonuç alışverişi yapar. Geçici tünelin açık kalmasına veya benim çalışma alanımda sürekli çalışan bir sunucuya ihtiyaç duyulmaz.

## Windows bilgisayarında

1. Önce eski Python köprüsü hâlâ çalışıyorsa **Ctrl+C** ile durdur. Roblox Studio'da düzenlenecek **yerin bir yedeğini** al. Asistan ayarlarında **Studio'yu MCP sunucusu olarak etkinleştir** açık olsun.
2. `Roblox_Studio_MCP_Sifreli_Postakutusu.zip` paketini **yeni/ayrı bir klasöre çıkar**. Üç dosya birlikte durmalı: `Roblox_Studio_MCP_Kalici_Kopru.py`, `Roblox_Studio_Bus.py`, `Roblox_Studio_MCP_Gizli_Ayar.json`. Gizli ayar dosyası rastgele oturum konuları ve şifreleme anahtarı içerir: **buraya yapıştırma, kimseyle paylaşma ve GitHub'a yükleme.**
3. Yeni klasörde PowerShell aç. **Aynı Python sürümüne** şifreleme kitaplığını bir defa kur:

   ```powershell
   python -m pip install cryptography
   ```

4. İstemciyi başlat ve terminali açık bırak:

   ```powershell
   python .\Roblox_Studio_MCP_Kalici_Kopru.py
   ```

5. `[MCP] Connected. Server advertises 28 tools.` sonrasında **`[bridge] ONLINE via encrypted HTTPS mailbox`** görünürse bu sohbete **"Köprü ONLINE"** yaz. Ben önce `list_roblox_studios` çağrısıyla açık Studio yerini doğrulayacağım; o noktaya kadar oyun düzenlendiğini iddia etmiyorum.
6. Kod düzenleme, Play, Luau çalıştırma ve fare/klavye gibi etkili işlemler terminalde **her istek için ayrı `YES`** onayı ister. Güvenmediğin işlemi boş Enter ile reddet. Büyük değişiklikler onay sırasında açılabilir tam bir JSON dosyasına yazılır. İstediğin zaman **Ctrl+C** ile yerel istemciyi kapat.

## Veri güvenliği ve sınırlar

- Bağlantı kamuya açık `ntfy.sh` hizmetine giden HTTPS üstünden kurulur. Ntfy hizmeti şifreli verileri geçici süre önbelleğe alır; **Studio kodu ve ekran görüntüsü gönderilmeden önce Fernet ile uçtan uca şifrelenir**. Hizmet yine de bağlantı zamanı, ileti boyutu ve rastgele konu adlarını görebilir. Duyarlı/özel proje veya kişisel bilgileri görüntüleyen Studio penceresiyle kullanma.
- Ek kurulumun tek Python bağımlılığı `cryptography` paketidir. Roblox hesabının şifresi veya API anahtarı gerekmez. Kullanıcının bilgisayarında dinleyen bir port açılmaz; Studio'nun kendi `%LOCALAPPDATA%\Roblox\mcp.bat` dosyası yerel stdio ile başlatılır.
- Şifreli postakutusu üçüncü taraf bir ücretsiz hizmet olduğu için kesintisiz erişim garantisi yoktur. Sorun olursa **yalnızca terminaldeki hata metnini** gönder; gizli JSON dosyasını, şifreleme anahtarını veya bütün Python kaynak dosyalarını sohbete kopyalama.
- Hem küçük komutlar hem büyük ekran görüntüleri şifreli gönderilir; 2 MB sınırını aşan yanıtlar doğrulanan parçalara bölünür. Sahte MCP ile `list_roblox_studios` ve `screen_capture` istek/yanıt döngüsü doğrulandı; **gerçek Studio oturumu ve Play hâlâ test edilmeyi bekliyor**.

Roblox Studio MCP açıklaması: https://create.roblox.com/docs/studio/mcp  
Ntfy mesaj/ek sınırları: https://docs.ntfy.sh/publish/
