STARTUP OTOMATİK KÖPRÜ / kullanıcının açık isteğiyle hazırlanan sınırlı sürüm

1) Windows'taki mevcut köprü terminalinde Ctrl+C.
2) Bu ZIP içindeki Roblox_Studio_MCP_Kalici_Kopru_STARTUP_OTOMATIK.py dosyasını
   mevcut Roblox_Studio_MCP_Kalici_Kopru.py ile AYNI klasöre çıkar.
   Roblox_Studio_Bus.py ve mevcut Roblox_Studio_MCP_Gizli_Ayar.json aynı klasörde
   kalmalı. Gizli JSON'u ZIP'e koymadık; kimseyle paylaşma.
3) Aynı klasörde Komut İstemi/PowerShell aç; çalıştır:
   py -3 Roblox_Studio_MCP_Kalici_Kopru_STARTUP_OTOMATIK.py
   (py yoksa: python Roblox_Studio_MCP_Kalici_Kopru_STARTUP_OTOMATIK.py)
4) Terminalde 'AUTO STARTUP POLICY' ve 'ONLINE' çıktısı görülmeli.
   Studio açık kalsın. Kapatmak için Ctrl+C. Eski elle-onaylı dosyaya
   dönmek için bu işlemi durdurup eski dosyayı yeniden çalıştır.

Bu dosyada otomatik geçilenler:
- yalnız seçili Studio örneğinde Play başlat/durdur;
- yalnız Edit modunda CORE_PROTOCOL_Server, REACTOR_MESH_CONTROLLER,
  CORE_PROTOCOL_Client veya adı STARTUP360_ ile başlayan açılış betikleri.

Bütün diğer düzenleme yolları, execute_luau, fare/klavye işlemleri ve gezinti
onay istemeden REDDEDİLİR. Read-only araçlar zaten otomatik çalışır.
Yayınlama veya dosyaya .rbxlx kaydetme aracı yoktur; oyun publish edilmez.
Sunucunun 'oldu' demesi oyunun diske kaydedildiğini kanıtlamaz.

Güvenlik: Daha geniş izin vermek için kodu değiştirme; banyodayken terminali
ızle. Uzaktan üçüncü taraf posta kutusundan şifreli komutlar taşınır;
şifreli konfigürasyon dosyasını kimseyle paylaşma.
