# CORE PROTOCOL V3 — gerçek Roblox Studio görsel düzeltmesi

**Tarih:** 25 Ekim 2026 · **Düzenlenen açık yer:** `AEGIS_Reactor.rbxlx`  
**Durum:** Studio'da V3 sunucu betiği ve V3 istemci betiği uygulandı, Play ile görüntülendi ve **Edit moduna geri dönüldü**. Windows'taki yerin diske kaydedilmesi kullanıcıya aittir: **Studio'da Ctrl+S / File → Save**. Ayrı `.rbxlx` yedeğini aldığını kullanıcı doğruladı. Bu paket, yedek yer dosyasını içermez.

## Asıl görsel hata ve çözüm

Önceki V2'de kontrol odasının üç gözlem penceresi `Enum.Material.Glass` idi. Roblox'un Glass malzemesi arkasındaki yarı saydam Neon parçaları ve partikülleri göstermediğinden, Play'de reaktörün beyaz yıldızı ve çoğu ışını **yokmuş gibi** görünüyordu. Aynı Play oturumunda, yalnızca istemcide kaydedilmeyen bir malzeme denemesi yapıp yıldızın ve halkaların anında ortaya çıktığını görüntüledim. V3'te pencere, cam sınırını ve kırılma mekaniğini koruyan çok saydam `SmoothPlastic` oldu. Teknik arka plan: [Roblox'un Glass malzemesi açıklaması](https://devforum.roblox.com/t/introducing-new-material-glass/64231).

Ek düzeltmeler: daha okunur kontrol odası ve mavi reaktör arka planı, daha büyük merkez yıldızı/ışınlar, hasarlı projektörlerde kesik kesik arklar, daha belirgin fiziksel gösterge yazıları. Referans kadrajına yaklaşmak için oyuncu ilk kişi görünümüyle başlar; **V** normal üçüncü kişi görünümüyle geçiş yapar. Referansta bulunmayan, pencere önünde sürekli duran kalın mavi ışık sütunu kaldırıldı; olayın kısa elektrik çatlaması ve sesi duruyor. Kontrollerin server-side simülasyonuna dokunulmadı.

## Doğrulama

- Gerçek Windows Roblox Studio MCP: oturum ve araçlar üzerinden yer listelendi, iki betik okundu, kullanıcı terminalinde ayrı ayrı `YES` onayıyla düzenlendi; Play başlatılıp durduruldu.
- **Normal oyun:** `STUDIO_AUTO_MELTDOWN=false`, `STUDIO_PREVIEW_SECOND=0` değerleri son kez doğrudan Studio betiğinden okundu. Başlangıç, `CORE_PROTOCOL_V3_Normal_Baslangic_Studio.jpg` ile görüntülendi. Output'ta V3 sunucusu ve istemcisi başlıyor; V3'e ait çalışma hatası görünmedi.
- **Aktif olay:** test süresince geçici olarak 244. saniye önizlemesi açılıp `CORE_PROTOCOL_V3_Meltdown_Studio.jpg` görüntüsü alındı; projektör hasarı ve olay sonrası kare Studio'da izlendi. Bu test ayarları **sonra kapatıldı**. Tam 435 saniyelik doğal döngü, tüm kumandalara gerçek oyuncu tıklamaları ve ses varlıklarının bu deneyimde oynatılma izni ayrı ayrı doğrulanmadı.
- Çevrimdışı Luau ayrıştırması ile tüm başlangıç/soğutma/arıza/SCRAM/anahtar-kart/bunker/meltdown senaryolarını çalıştıran mühendislik simülasyonu geçti. Bu simülasyon, Studio'daki fizik ve ses doğrulamasının yerine geçmez.
- V3 oyun betikleri **3.541 satır**; 8.000 satır sınırının altında. V1, V2 ve önceki V4 dosyaları değiştirilmedi.

## Kurulum veya geri yükleme

Studio'da düzenleme zaten yapıldı. Gerekirse `CORE_PROTOCOL_V3_Server.server.lua` içeriğini **ServerScriptService → CORE_PROTOCOL_Server (Script)** içine, `CORE_PROTOCOL_V3_Client.client.lua` içeriğini **StarterPlayer → StarterPlayerScripts → CORE_PROTOCOL_Client (LocalScript)** içine koyun; eski betikler ile **aynı anda ikinci kopyalarını çalıştırmayın**. Prosedürel dünya Play sırasında kurulur; bu yüzden Edit viewport'unun boş olması beklenir.

**Sıradaki kullanıcı adımı:** Studio Edit modundayken açık `.rbxlx` dosyasını **Ctrl+S** ile kaydedin. İsterseniz önce ayrı yedeğin adını tekrar kontrol edin. Sesler sessizse Roblox deneyiminin ilgili ses varlıkları için oynatma iznini Studio'da denetleyin. Bu çalışma 144p videodaki varlıkların veya görünmeyen mekaniklerin birebir kopyası olduğunu iddia etmez.

**Köprü hakkında:** Studio ile bu oturum arasındaki trafik resmi Arena bağlayıcısından değil, kullanıcı tarafından açılan `ntfy.sh` HTTPS posta hizmetinden Fernet ile şifrelenmiş olarak geçti. Hizmetin kota/hız sınırları ve geçici ek depolaması vardır. Windows köprü terminali kapatılırsa canlı Studio erişimi sonlanır; yerin kaydedilmiş dosyası bundan etkilenmez.
