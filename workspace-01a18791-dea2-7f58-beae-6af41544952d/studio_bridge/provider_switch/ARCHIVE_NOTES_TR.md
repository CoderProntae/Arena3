# Çalışma alanı bütçesi — 26.10.2026

Kullanıcı çalışma alanının 128 MiB sınırını aştığını bildirdi. **Onaylı GLB'ler, betik kaynakları, 01–04 Play raporları ve QA JSON bağlantıları korunmuştur.**

- `unlinked_studio_responses_2026-10-26.tar.gz`: hiçbir QA/rapor dosyasında yolu geçmeyen 490 eski köprü JSON yanıtının kayıpsız arşivi; adlar arşivin içinde aynen durur. Bağlantılı 353 JSON yanıtı `community_results` klasöründe okunabilir halde bırakıldı. Arşiv, kullanıcıya sunulacak yeni Play kanıtı değildir.
- Bağlantılı 53 `screen_capture` JSON yanıtındaki JPEG base64 kopyaları, **bayt bayt aynı JPEG dosyaları doğrulanarak** kaldırıldı. Her yanıt halen `response.result.isError` durumunu ve JPEG yolunu/SHA-256 değerini içerir; gerçek JPEG'ler aynı adlarıyla klasördedir. Fotoğraflar yeniden üretilmedi veya düzenlenmedi.
- `references/A_Core_Game_709-1649_144p.mp4` (23,76 MiB) kaynağı ve SHA-256 değeri `references/Video_Ilk_Cozumleme.md` içinde kayıtlıdır; büyük yerel kopya geçici, **snapshot dışında** `.cache/references/` klasörüne taşındı. Sonraki oturumda yoksa özgün adresten yeniden indirilebilir. Çıkarılmış kare/sahne referansları korunmuştur.

Bu düzenleme 128 MiB altına inmeye yöneliktir; önceki uyarıda 252 dosyanın kaydedilmemiş olması geriye dönük onarılamaz. Kritik dosya bütünlüğü `reactor_startup/qa/validate_checkpoint05_local.py` ile ayrıca denetlenmelidir. Kullanıcı başka bir Studio ortamına geçtiğini belirtti: eski köprüyü yeni ortam saymayın ve izinsiz Studio değişikliği yapmayın.
